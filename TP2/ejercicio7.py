from itertools import combinations
from pathlib import Path

from TP1.GF2m import GF2m
from TP2.ejercicio5 import gf2_vector_to_int
from TP2.ejercicio6 import build_matrices, decode, encode


ERROR_PATTERN_PATH = Path(__file__).parent / "vectors" / "golay_errors_w0_w4.hex"
ROW_SEARCH_PATH    = Path(__file__).parent / "vectors" / "golay_row_search.hex"


def generate_row_search_golden(B, export_vectors=False):
    """Genera la referencia de golay_row_search para las 4096 entradas."""

    vectors = []

    for i_vec in range(4096):
        found = 0
        idx = 0
        residual = 0

        for row, b_row in enumerate(B):
            candidate = i_vec ^ gf2_vector_to_int(b_row)

            if candidate.bit_count() <= 2:
                found = 1
                idx = 11 - row
                residual = candidate
                break

        # Palabra de 17 bits: {o_found, o_idx[3:0], o_res[11:0]}.
        vectors.append((found << 16) | (idx << 12) | residual)

    if export_vectors:
        ROW_SEARCH_PATH.parent.mkdir(parents=True, exist_ok=True)

        with ROW_SEARCH_PATH.open("w", encoding="ascii", newline="\n") as vectors_file:
            for vector in vectors:
                vectors_file.write(f"{vector:05X}\n")

    return vectors


def characterize_decoder(n, k, B, G, H, field, export_vectors=False):
    """Clasifica todos los patrones de error de peso 0 a 4"""

    codeword = encode(0, k, G, field)
    results = []
    vectors_file = None

    if export_vectors:
        ERROR_PATTERN_PATH.parent.mkdir(parents=True, exist_ok=True)
        vectors_file = ERROR_PATTERN_PATH.open("w", encoding="ascii", newline="\n")

    for weight in range(5):
        total = 0
        corrected = 0
        miscorrected = 0
        detected = 0

        # Se evaluan todas las combinaciones posibles de error para N bits, para un peso weight
        for positions in combinations(range(n), weight):

            # Se genera el patron de error
            error = [field.element(0) for _ in range(n)]
            for position in positions:
                error[position] = field.element(1)

            if vectors_file is not None:
                vectors_file.write(f"{gf2_vector_to_int(error):06X}\n")

            # Se agrega el error a una codeword cualquiera
            received = []
            for i in range(n):
                received.append(codeword[i] + error[i])

            # Se decodifica el error
            _, decoded_error, _, uncorrectable = decode(received, B, H, k, field)
            total += 1

            if uncorrectable:
                detected += 1
            else:
                corrected_word = []

                for i in range(n):
                    corrected_word.append(received[i] + decoded_error[i])

                if corrected_word == codeword:
                    corrected += 1
                else:
                    miscorrected += 1

        results.append((weight, total, corrected, miscorrected, detected))

    if vectors_file is not None:
        vectors_file.close()

    return results


def main():

    # Ejercicio 7a
    n = 24
    k = 12

    gf2 = GF2m(m=1, primitive_poly=0b1)
    B, G, H = build_matrices(n, k, gf2)
    results = characterize_decoder(n, k, B, G, H, gf2, export_vectors=True)

    print("Caracterizacion del decodificador")
    print()
    print("Weight | Total | Correction | Miscorrection | Detection")
    print("-----+----------+------------+--------------+-----------")

    for weight, total, corrected, miscorrected, detected in results:
        print(
            f"{weight:4d} | {total:8d} | {corrected:10d} | "
            f"{miscorrected:12d} | {detected:9d}"
        )

    # Ejercicio 7b
    generate_row_search_golden(B, export_vectors=True)


if __name__ == "__main__":
    main()
