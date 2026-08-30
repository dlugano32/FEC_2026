from itertools import combinations

from TP1.GF2m import GF2m
from TP2.ejercicio6 import build_matrices, decode, encode


def characterize_decoder(n, k, B, G, H, field):
    """Clasifica todos los patrones de error de peso 0 a 4"""

    codeword = encode(0, k, G, field)
    results = []

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

    return results


def main():
    n = 24
    k = 12

    gf2 = GF2m(m=1, primitive_poly=0b1)
    B, G, H = build_matrices(n, k, gf2)
    results = characterize_decoder(n, k, B, G, H, gf2)

    print("Caracterizacion del decodificador")
    print()
    print("Weight | Total | Correction | Miscorrection | Detection")
    print("-----+----------+------------+--------------+-----------")

    for weight, total, corrected, miscorrected, detected in results:
        print(
            f"{weight:4d} | {total:8d} | {corrected:10d} | "
            f"{miscorrected:12d} | {detected:9d}"
        )


if __name__ == "__main__":
    main()
