import numpy as np
from itertools import combinations
from math import comb

from TP1.GF2m import GF2m
from TP1.GFPoly import GFPoly

from TP_Extra.bch import (
    cyclotomic_coset,
    systematic_bch_encoder,
    int_to_bit_array,
    build_generator_matrix,
    build_parity_check_matrix,
    matrix_bch_encoder,
    build_syndrome_lut,
    lut_bch_decoder,
    peterson_chien_decoder
)


def main():

    # ============================================================
    # 1. BCH(31,21) SETUP
    # ============================================================

    N = 31
    K = 21

    gf32 = GF2m(m=5, primitive_poly=0b00101)

    alpha = gf32.element(2)

    c1 = cyclotomic_coset(1, N)
    c3 = cyclotomic_coset(3, N)

    roots_c1 = [alpha ** exponent for exponent in c1]
    roots_c3 = [alpha ** exponent for exponent in c3]

    m1 = GFPoly.from_roots(gf32, roots_c1)
    m3 = GFPoly.from_roots(gf32, roots_c3)

    g = m1 * m3

    G = build_generator_matrix(gf32, g, N, K)
    H = build_parity_check_matrix(G, N, K)

    syndrome_lut = build_syndrome_lut(H)


    # ============================================================
    # 2. REFERENCE CODEWORD
    # ============================================================

    u = 0b101100111000110101101

    message = int_to_bit_array(u, K)

    codeword_poly = int_to_bit_array(systematic_bch_encoder(u, gf32, g, N, K), N)
    codeword_matrix = matrix_bch_encoder(G, message)

    assert np.array_equal(codeword_poly, codeword_matrix)

    codeword = codeword_matrix

    print("\n========================================")
    print("BCH(31,21) decoder exhaustive test")
    print("========================================")


    # ============================================================
    # 3. WEIGHT 0, 1 AND 2
    # ============================================================

    print("\nCorrectable error patterns:")

    for weight in (0, 1, 2):

        n_patterns = 0

        for positions in combinations(range(N), weight):

            received = codeword.copy()

            for position in positions:
                received[position] ^= 1

            corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
            corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

            # Both decoders must succeed
            assert success_lut
            assert success_pc

            # Both decoders must recover the transmitted codeword
            assert np.array_equal(corrected_lut, codeword)
            assert np.array_equal(corrected_pc, codeword)

            # Peterson + Chien must report the correct error weight
            assert n_corrected == weight

            n_patterns += 1

        print(f"Weight {weight}: {n_patterns} patterns PASS")


    # ============================================================
    # 4. WEIGHT 3
    # ============================================================

    print("\nWeight 3 characterization:")

    total = 0
    uncorrectable = 0
    miscorrection = 0

    for positions in combinations(range(N), 3):

        received = codeword.copy()

        for position in positions:
            received[position] ^= 1

        corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
        corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

        # Both decoder implementations must behave identically
        assert success_lut == success_pc
        assert np.array_equal(corrected_lut, corrected_pc)

        if not success_pc:

            # Uncorrectable:
            # decoder must leave received word unchanged
            assert np.array_equal(corrected_pc, received)
            assert n_corrected == 0

            uncorrectable += 1

        else:

            # Weight 3 is outside t=2.
            # If decoder reports success, it must be a miscorrection.
            assert not np.array_equal(corrected_pc, codeword)
            assert n_corrected == 2

            miscorrection += 1

        total += 1

    assert total == comb(N, 3)
    assert uncorrectable + miscorrection == total

    print(f"Total patterns : {total}")
    print(f"Uncorrectable  : {uncorrectable}")
    print(f"Miscorrection  : {miscorrection}")

    # ============================================================
    # 5. WEIGHT 4
    # ============================================================

    print("\nWeight 4 characterization:")

    total = 0
    uncorrectable = 0
    miscorrection = 0
    miscorrection_1 = 0
    miscorrection_2 = 0

    for positions in combinations(range(N), 4):

        received = codeword.copy()

        for position in positions:
            received[position] ^= 1

        corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
        corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

        # Both decoder implementations must behave identically
        assert success_lut == success_pc
        assert np.array_equal(corrected_lut, corrected_pc)

        if not success_pc:

            # Uncorrectable:
            # decoder must leave received word unchanged
            assert np.array_equal(corrected_pc, received)
            assert n_corrected == 0

            uncorrectable += 1

        else:
            # If decoder reports success, it must be a miscorrection.
            assert not np.array_equal(corrected_pc, codeword)

            miscorrection += 1

            # Coset leader of weight 4 error can be either weight 1 or weight 2.
            if n_corrected == 1:
                miscorrection_1 += 1

            elif n_corrected == 2:
                miscorrection_2 += 1

        total += 1

    assert total == comb(N, 4)
    assert miscorrection_1 + miscorrection_2 == miscorrection
    assert uncorrectable + miscorrection == total

    print(f"Total patterns : {total}")
    print(f"Uncorrectable  : {uncorrectable}")
    print(f"Miscorrection  : {miscorrection} ({miscorrection_1} (weight 1) + {miscorrection_2} (weight 2))")

    # ============================================================
    # 6. WEIGHT 5
    # ============================================================

    print("\nWeight 5 characterization:")

    total = 0
    uncorrectable = 0
    undetected = 0
    miscorrection = 0
    miscorrection_1 = 0
    miscorrection_2 = 0

    for positions in combinations(range(N), 5):

        received = codeword.copy()

        for position in positions:
            received[position] ^= 1

        corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
        corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

        # Both decoder implementations must behave identically
        assert success_lut == success_pc
        assert np.array_equal(corrected_lut, corrected_pc)

        if not success_pc:

            # Uncorrectable:
            # decoder must leave received word unchanged
            assert np.array_equal(corrected_pc, received)
            assert n_corrected == 0

            uncorrectable += 1

        else:
            assert not np.array_equal(corrected_pc, codeword)

            if n_corrected == 0:

                # Undetected error:
                # received is already another valid codeword.
                assert np.array_equal(corrected_pc, received)
                undetected += 1

            elif n_corrected == 1:

                miscorrection += 1
                miscorrection_1 += 1

            elif n_corrected == 2:

                miscorrection += 1
                miscorrection_2 += 1

        total += 1

    assert total == comb(N, 5)
    assert miscorrection_1 + miscorrection_2 == miscorrection
    assert uncorrectable + miscorrection + undetected == total

    print(f"Total patterns : {total}")
    print(f"Uncorrectable  : {uncorrectable}")
    print(f"Miscorrection  : {miscorrection} ({miscorrection_1} weight-1 + {miscorrection_2} weight-2)")
    print(f"Undetected     : {undetected}")

    print("\nAll decoder tests passed")


if __name__ == "__main__":
    main()