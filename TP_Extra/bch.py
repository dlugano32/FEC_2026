import numpy as np
from itertools import combinations

from TP1.GF2m import GF2m
from TP1.GFPoly import GFPoly

def cyclotomic_coset(start: int, n: int)-> list[int]:
    """
        Construye el coset ciclotómico binario:

            C_start = {start, 2*start, 4*start, ...} mod n

        El ciclo termina cuando se repite el exponente inicial.
    """

    coset = []
    current = start % n

    while current not in coset:
        coset.append(current)
        current = (2*current) % n

    return coset

def systematic_bch_encoder (message: int, gf: GF2m, g: GFPoly, n: int, k: int) -> int:
    """
        Encode a k-bit message using the systematic BCH(n, k) code

        Codeword convention:
            bits [n-1: n-k] -> message
            bits [n-k-1:0]   -> parity

        Polynomial convention:
            bit i = coefficient of x^i

        c(x) = m(x) * x^(n-k) + r(x)
        
        Being r(x) the remainder of the division of m(x) * x^(n-k) by g(x) to make c(x) divisible by g(x).
        
        """

    if not isinstance(message, int):
        raise TypeError("Message must be an integer")

    if not 0 <= message < (1 << k):
        raise ValueError(f"Message must fit in {k} bits")

    # Convert the message integer into a list of GF(32) elements (coefficients of the message polynomial)
    message_coefficients = [
            gf.element((message >>i) & 1) 
            for i in range(k-1, -1, -1)
        ]

    # Create the message polynomial from the message bits
    message_poly = GFPoly(gf, message_coefficients)

    # Shift the message polynomial by multiplying it by x^(n-k) to make room for the parity bits.
    shifted_message_poly = message_poly * GFPoly(gf, [gf.element(1)] + [gf.element(0)] * (n-k))

    # Divide the shifted message polynomial by the generator polynomial g(x) to find the remainder (parity bits).
    # The parity polynomial plus the shifted message polynomial will give us the systematic codeword.
    _, parity_poly = shifted_message_poly.divide(g)

    parity = parity_poly.to_int()

    # Systematic codeword:
    # [message (k bits) | parity (n-k bits)]
    codeword = (message << (n-k)) | parity

    return codeword

def int_to_bit_array(value: int, width: int) -> np.ndarray:
    return np.array(
        [(value >> i) & 1 for i in range(width - 1, -1, -1)],
        dtype=np.uint8
    )

def matmul_gf2(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Matrix multiplication over GF(2).

    Computes:
        C = A @ B mod 2

    Parameters
    ----------
    A : np.ndarray
        Left matrix.
    B : np.ndarray
        Right matrix.

    Returns
    -------
    np.ndarray
        Matrix product over GF(2).
    """

    if A.ndim != 2 or B.ndim != 2:
        raise ValueError("A and B must be 2-dimensional matrices")

    if A.shape[1] != B.shape[0]:
        raise ValueError(
            "Incompatible matrix dimensions: "
            f"{A.shape} and {B.shape}"
        )

    return (A @ B) % 2

def build_generator_matrix(gf: GF2m, g: GFPoly, n: int, k: int) -> np.ndarray:
    """
    Build the systematic generator matrix:

        G = [I_k | P]

    Shape:
        (k, n)
    """

    G = np.zeros((k, n), dtype=np.uint8)

    for row_index in range(k):
        unit_message = 1 << (k - 1 - row_index)

        codeword = systematic_bch_encoder(
            message=unit_message,
            gf=gf,
            g=g,
            n=n,
            k=k
        )

        G[row_index] = int_to_bit_array(codeword, n)

    return G

def build_parity_check_matrix(G: np.ndarray, n: int, k: int) -> np.ndarray:
    """
        Build the parity-check matrix of n-k rows and n columns for the BCH(n, k) code:

            H = [P^T | I_(n-k)]

        The parity-check matrix is constructed from the generator matrix by taking the 
        transpose of the parity part and appending an identity matrix of size (n-k).
    """
    redundancy = n - k

    P = G[:, k:]

    H = np.concatenate(
        (
            P.T,
            np.eye(redundancy, dtype=np.uint8)
        ),
        axis=1
    )

    return H

def matrix_bch_encoder(G: np.ndarray, message: np.ndarray) -> np.ndarray:
    """
    Encode a 1-D message vector using:

        c = message @ G   over GF(2)
    """

    if message.ndim != 1:
        raise ValueError("message must be a 1-D array")

    if len(message) != G.shape[0]:
        raise ValueError(f"message must contain {G.shape[0]} bits")

    message_row = message.reshape(1, -1)

    codeword = matmul_gf2(message_row, G)

    return codeword.flatten()

def syndrome_bin(received: np.ndarray, H: np.ndarray) -> np.ndarray:
    """
    Calculate the binary syndrome:

        s = received @ H.T

    over GF(2).
    """

    if received.ndim != 1:
        raise ValueError("received must be a 1-D array")

    if len(received) != H.shape[1]:
        raise ValueError(f"received must contain {H.shape[1]} bits")

    received_row = received.reshape(1, -1)

    syndrome = matmul_gf2(received_row,H.T)

    return syndrome.flatten()

def build_syndrome_lut(H: np.ndarray) -> dict[tuple[int, ...], np.ndarray]:
    """
    Build the syndrome LUT for all correctable error patterns
    of weight 0, 1 and 2.

    LUT format:
        tuple(binary syndrome) -> binary error vector
    """

    n = H.shape[1]
    lut: dict[tuple[int, ...], np.ndarray] = {}

    for weight in (0, 1, 2):
        for positions in combinations(range(n), weight):
            error = np.zeros(n, dtype=np.uint8)

            for position in positions:
                error[position] = 1

            syndrome = syndrome_bin(error, H)
            syndrome_key = tuple(int(bit) for bit in syndrome)

            # All error patterns of weight <= 2 must have
            # different syndromes for a t=2 BCH code.
            assert syndrome_key not in lut

            lut[syndrome_key] = error.copy()

    return lut


def lut_bch_decoder(received: np.ndarray, H: np.ndarray, lut: dict[tuple[int, ...], np.ndarray]
) -> tuple[np.ndarray, bool]:
    """
    Decode a received BCH word using the binary syndrome LUT.

    Returns:
        corrected : np.ndarray
            Corrected n-bit codeword.
        success : bool
            True if the syndrome exists in the LUT.
            False otherwise.
    """

    if received.ndim != 1:
        raise ValueError("received must be a 1-D array")

    if len(received) != H.shape[1]:
        raise ValueError(f"received must contain {H.shape[1]} bits")

    syndrome = syndrome_bin(received, H)
    syndrome_key = tuple(int(bit) for bit in syndrome)

    error = lut.get(syndrome_key)

    if error is None:
        return received.copy(), False

    corrected = received ^ error

    # A successful correction must produce a valid codeword.
    assert np.all(syndrome_bin(corrected, H) == 0)

    return corrected, True

def syndrome_bch(received: np.ndarray, gf: GF2m) -> tuple[GF2m.element, GF2m.element]:
    """
        Compute BCH syndromes:

            S1 = r(alpha)
            S3 = r(alpha^3)

        For a primitive BCH code:
            n = gf.order - 1

        Convention:
            received[0]   -> coefficient of x^(n-1)
            received[n-1] -> coefficient of x^0
    """
    n = gf.order - 1

    alpha = gf.element(2)

    if received.ndim != 1:
        raise ValueError("received must be a 1-D array")

    if len(received) != n:
        raise ValueError(f"received must contain {n} bits")

    S1 = gf.element(0)
    S3 = gf.element(0)

    for array_index in range(n):
        if received[array_index]:
            exponent = n - 1 - array_index

            S1 += alpha ** exponent
            S3 += alpha ** (3 * exponent)

    return S1, S3

def chien_search(sigma1: GF2m.element, sigma2: GF2m.element, gf: GF2m) -> list[int]:
    """
        Search roots of:

            sigma(x) = 1 + sigma1*x + sigma2*x^2

        sigma^1 = S1
        sigma^2 = (S3 + S1^3) / S1

        evaluating x = alpha^(-i).

        Returns BCH polynomial positions i.
    """

    n = gf.order - 1

    zero  = gf.element(0)
    one   = gf.element(1)
    alpha = gf.element(2)

    error_positions = []

    for i in range(n):

        # alpha^(-i) = alpha^(n-i) in GF(2^m)^*
        x = alpha ** ((n - i) % n)

        sigma_x = (
            one
            + sigma1 * x
            + sigma2 * (x ** 2)
        )

        if sigma_x == zero:
            error_positions.append(i)

    return error_positions

def peterson_chien_decoder(received: np.ndarray, gf: GF2m) -> tuple[np.ndarray, int, bool]:
    """
    Decode BCH t=2 using Peterson + Chien.

    Returns:
        corrected:
            corrected codeword, or received unchanged if uncorrectable

        n_corrected:
            0, 1 or 2

        ok:
            True  -> decoder produced a valid correction
            False -> uncorrectable
    """

    n = gf.order - 1

    if received.ndim != 1:
        raise ValueError("received must be a 1-D array")

    if len(received) != n:
        raise ValueError(f"received must contain {n} bits")

    zero = gf.element(0)
    alpha = gf.element(2)

    S1, S3 = syndrome_bch(received, gf)

    # ------------------------------------------------------------
    # Case 0: no error
    # ------------------------------------------------------------
    if S1 == zero and S3 == zero:
        return received.copy(), 0, True

    # ------------------------------------------------------------
    # Case 1: one error
    # ------------------------------------------------------------
    if S1 != zero and S3 == (S1 ** 3):
        for i in range(n):
            if alpha ** i == S1:
                error_position = i
                break
            
        corrected = received.copy()

        array_index = n - 1 - error_position
        corrected[array_index] ^= 1

        return corrected, 1, True

    # ------------------------------------------------------------
    # Case 2: impossible with <= 2 errors
    # ------------------------------------------------------------
    if S1 == zero and S3 != zero:
        return received.copy(), 0, False

    # ------------------------------------------------------------
    # Case 3: Peterson + Chien
    # ------------------------------------------------------------

    sigma1 = S1
    sigma2 = (S3 + (S1 ** 3)) / S1

    error_positions = chien_search(sigma1,sigma2,gf)

    if len(error_positions) != 2:
        return received.copy(), 0, False

    corrected = received.copy()

    for position in error_positions:
        array_index = n - 1 - position
        corrected[array_index] ^= 1

    return corrected, 2, True

def main():

    # Convention for BCH codewords:
    # array index:    0    1    2   ...   29   30
    # coefficient:   c30  c29  c28  ...   c1   c0
    # exponent:       30   29   28  ...    1    0

    # ============================================================
    # 1. BCH(31,21) CONSTRUCTION
    # ============================================================

    N = 31
    K = 21

    # GF(32): p(x) = x^5 + x^2 + 1
    gf32 = GF2m(m=5, primitive_poly=0b00101)

    zero  = gf32.element(0)
    one   = gf32.element(1)
    alpha = gf32.element(2)

    g_reference = 0b11101101001

    # Cyclotomic cosets associated with roots:
    #
    # alpha, alpha^2, alpha^3, alpha^4
    c1 = cyclotomic_coset(1, N)
    c3 = cyclotomic_coset(3, N)

    roots_c1 = [alpha ** exponent for exponent in c1]

    roots_c3 = [alpha ** exponent for exponent in c3]

    # Minimal polynomials
    m1 = GFPoly.from_roots(gf32, roots_c1)
    m3 = GFPoly.from_roots(gf32, roots_c3)

    # BCH generator polynomial
    g = m1 * m3

    print("\n========================================")
    print("BCH(31,21) construction")
    print("========================================")

    print("C1 =", c1)
    print("C3 =", c3)

    print("m1(x) =", m1.to_string())
    print("m3(x) =", m3.to_string())
    print("g(x)  =", g.to_string())

    # Generator polynomial checks
    assert g.to_int() == g_reference

    x31_plus_1 = GFPoly(gf32, [one] + [zero] * 30 + [one])

    _, remainder = x31_plus_1.divide(g)

    assert remainder.to_int() == 0

    print("Generator polynomial checks: PASS")

    # ============================================================
    # 2. GENERATOR AND PARITY-CHECK MATRICES
    # ============================================================

    G = build_generator_matrix(gf=gf32, g=g, n=N, k=K)

    H = build_parity_check_matrix(G=G, n=N, k=K)

    print("\n========================================")
    print("Generator and parity-check matrices")
    print("========================================")

    print(f"G shape: {G.shape}")
    print(f"H shape: {H.shape}")

    # Check systematic form:
    #
    # G = [I_k | P]
    assert np.array_equal(G[:, :K], np.eye(K, dtype=np.uint8))

    # Check:
    #
    # G H^T = 0
    GHt = matmul_gf2(G, H.T)

    assert np.all(GHt == 0)

    print("G = [I_k | P]: PASS")
    print("G * H^T = 0: PASS")

    # ============================================================
    # 3. BCH ENCODER / DECODER BASIC CHECKS
    # ============================================================

    print("\n========================================")
    print("BCH encoder / decoder basic checks")
    print("========================================")

    # Reference message used for all tests
    u = 0b101100111000110101101
    c = 0b1011001110001101011011000011101

    message = int_to_bit_array(u, K)
    expected_codeword = int_to_bit_array(c, N)

    # ------------------------------------------------------------
    # Encoder check:
    # polynomial encoder vs matrix encoder
    # ------------------------------------------------------------

    codeword_poly = int_to_bit_array(
        systematic_bch_encoder(message=u, gf=gf32, g=g, n=N, k=K),
        N
    )

    codeword_matrix = matrix_bch_encoder(G, message)

    assert np.array_equal(codeword_poly, expected_codeword)

    assert np.array_equal(codeword_matrix, expected_codeword)

    codeword = codeword_matrix

    print("Polynomial vs matrix encoder: PASS")

    # ------------------------------------------------------------
    # Syndrome check for a valid codeword:
    # binary syndrome vs BCH syndrome
    # ------------------------------------------------------------

    syn_bin = syndrome_bin(
        codeword,
        H
    )

    S1, S3 = syndrome_bch(
        received=codeword,
        gf=gf32
    )

    assert np.all(syn_bin == 0)
    assert S1 == zero
    assert S3 == zero

    print("Binary and BCH syndrome: PASS")

    # ------------------------------------------------------------
    # Build binary syndrome LUT
    # ------------------------------------------------------------

    syndrome_lut = build_syndrome_lut(H)

    expected_entries = ( 1 + N + N * (N - 1) // 2)

    assert len(syndrome_lut) == expected_entries

    print(f"Syndrome LUT entries: {len(syndrome_lut)}")

    # ------------------------------------------------------------
    # Decoder checks:
    # LUT vs Peterson + Chien
    # ------------------------------------------------------------

    # Test 0 : no_error
    received = codeword.copy()

    corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
    corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

    assert success_lut
    assert success_pc
    assert np.array_equal(corrected_lut, codeword)
    assert np.array_equal(corrected_pc, codeword)
    assert np.array_equal(corrected_lut, corrected_pc)
    assert n_corrected == 0


    # Test 1 : one_error
    received = codeword.copy()
    received[30-7] ^= 1

    corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
    corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

    assert success_lut
    assert success_pc
    assert np.array_equal(corrected_lut, codeword)
    assert np.array_equal(corrected_pc, codeword)
    assert np.array_equal(corrected_lut, corrected_pc)
    assert n_corrected == 1


    # Test 2 : two_errors
    received = codeword.copy()
    received[30-3] ^= 1
    received[30-22] ^= 1

    corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
    corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

    assert success_lut
    assert success_pc
    assert np.array_equal(corrected_lut, codeword)
    assert np.array_equal(corrected_pc, codeword)
    assert np.array_equal(corrected_lut, corrected_pc)
    assert n_corrected == 2

    print("LUT vs Peterson + Chien decoder: PASS")


    # ------------------------------------------------------------
    # Test 3 : three_errors / uncorrectable
    # ------------------------------------------------------------

    received = codeword.copy()
    received[30-1] ^= 1
    received[30-9] ^= 1
    received[30-17] ^= 1

    corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
    corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

    assert not success_lut
    assert not success_pc
    assert np.array_equal(corrected_lut, received)
    assert np.array_equal(corrected_pc, received)
    assert n_corrected == 0

    print("Uncorrectable case: PASS")


    # ------------------------------------------------------------
    # Test 4 : miscorrection
    # ------------------------------------------------------------

    received = codeword.copy()
    received[30-0] ^= 1
    received[30-1] ^= 1
    received[30-4] ^= 1

    corrected_lut, success_lut = lut_bch_decoder(received, H, syndrome_lut)
    corrected_pc, n_corrected, success_pc = peterson_chien_decoder(received, gf32)

    assert success_lut
    assert success_pc
    assert not np.array_equal(corrected_lut, codeword)
    assert not np.array_equal(corrected_pc, codeword)
    assert np.array_equal(corrected_lut, corrected_pc)
    assert n_corrected == 2

    print("Miscorrection case: PASS")

    print("\nAll BCH basic checks passed")
    
if __name__ == "__main__":
    main()