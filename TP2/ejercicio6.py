from itertools import combinations

from TP1.GF2m import GF2m
from TP2.ejercicio4 import hamming_weight, vector_matrix_product
from TP2.ejercicio5 import B_HEX, gf2_vector_to_int, identity_matrix, int_to_gf2_vector, transpose


def build_matrices(n, k, field):
    """Construye B, G=[I|B] y H=[B^T|I]"""

    redundancy = n - k
    B = []

    for value in B_HEX:
        B.append(int_to_gf2_vector(value, redundancy, field))

    identity = identity_matrix(k, field)
    B_transpose = transpose(B)
    G = []
    H = []

    for i in range(k):
        G.append(identity[i] + B[i])

    for i in range(redundancy):
        H.append(B_transpose[i] + identity[i])

    return B, G, H


def encode(message, k, G, field):
    """Codifica un mensaje mediante v = m * G"""

    message_vector = int_to_gf2_vector(message, k, field)
    return vector_matrix_product(message_vector, G)


def generate_syndrome_table(n, H, field):
    """Genera desde H los sindromes de todos los errores de peso 0 a 3"""

    table = {}
    H_transpose = transpose(H)

    for weight in range(4):
        for positions in combinations(range(n), weight):

            # Se crea el vector de error
            error = [field.element(0) for _ in range(n)]
            for position in positions:
                error[position] = field.element(1)

            # Se calcula el sindrome del error
            syndrome = vector_matrix_product(error, H_transpose)
            syndrome_value = gf2_vector_to_int(syndrome)

            if syndrome_value in table:
                raise ValueError("Dos errores corregibles tienen el mismo sindrome")

            table[syndrome_value] = error

    return table


def find_error_pattern(syndrome, B, k, field):
    """ Aplica en orden los cuatro casos del algoritmo de decodificacion
            Devuelve patron de error y caso
    """

    zero = field.element(0)
    one = field.element(1)

    # Caso 1: w(s) <= 3, e = (0 | s)
    if hamming_weight(syndrome) <= 3:
        return [zero for _ in range(k)] + syndrome, 1

    # Caso 2: existe i con w(s + b_i) <= 2 , e = (u_i | s + b_i)
    for i in range(k):
        residual = [syndrome[j] + B[i][j] for j in range(k)]

        if hamming_weight(residual) <= 2:
            unit = [zero for _ in range(k)]
            unit[i] = one
            return unit + residual, 2

    # q = s * B
    q = vector_matrix_product(syndrome, B)

    # Caso 3: w(q) <= 3, e = (q | 0)
    if hamming_weight(q) <= 3:
        return q + [zero for _ in range(k)], 3

    # Caso 4: existe i con w(q + b_i) <= 2, e = (q + b_i | u_i)
    for i in range(k):
        residual = [q[j] + B[i][j] for j in range(k)]

        if hamming_weight(residual) <= 2:
            unit = [zero for _ in range(k)]
            unit[i] = one
            return residual + unit, 4

    # Caso 5: error no corregible
    return None, 5


def decode(received, B, H, k, field):
    """Devuelve mensaje, error, corrected y uncorrectable"""

    syndrome = vector_matrix_product(received, transpose(H))
    error, case = find_error_pattern(syndrome, B, k, field)

    if case == 5:
        return None, None, False, True

    corrected_word = []
    for i in range(len(received)):
        corrected_word.append(received[i] + error[i])

    message = corrected_word[:k]
    corrected = hamming_weight(error) != 0

    return message, error, corrected, False


def main():
    # Extended Golay Code (24,12)
    n = 24
    k = 12

    gf2 = GF2m(m=1, primitive_poly=0b1)
    B, G, H = build_matrices(n, k, gf2)
    syndrome_table = generate_syndrome_table(n, H, gf2)

    expected_table_size = 1 + n + n * (n - 1) // 2 + n * (n - 1) * (n - 2) // (2 * 3)
    assert len(syndrome_table) == expected_table_size

    print(f"Entradas en la tabla de sindromes: {len(syndrome_table)}")

    # Vectores de prueba del Ejercicio 3
    original_message = 0xA5C
    received_words = [
        0xA5CBE7,   # Caso 1 (3 errores en redundancia)
        0xA5D9A6,   # Caso 2 (1 error en el mensaje y 2 en redundancia)
        0xFDC9A5,   # Caso 3 (3 errores en el mensaje)
        0xA5F9A4,   # Caso 4 (2 errores en el mensaje y 1 en redundancia)
        0xA5C9AA,   # Caso 5 (+ 3 errores)
    ]

    for received_value in received_words:
        received = int_to_gf2_vector(received_value, n, gf2)
        syndrome = vector_matrix_product(received, transpose(H))
        _, case = find_error_pattern(syndrome, B, k, gf2)
        
        message, error, corrected, uncorrectable = decode(received, B, H, k, gf2)

        print(f"\nr = 0x{received_value:06X}")
        print(f"s = 0x{gf2_vector_to_int(syndrome):03X}")
        print(f"caso = {case}")

        if uncorrectable:
            assert gf2_vector_to_int(syndrome) not in syndrome_table
            print("error no corregible")
        else:
            table_error = syndrome_table[gf2_vector_to_int(syndrome)]
            assert error == table_error
            assert corrected is True
            assert original_message == gf2_vector_to_int(message)
            print(f"e = 0x{gf2_vector_to_int(error):06X}")
            print(f"m = 0x{gf2_vector_to_int(message):03X}")

if __name__ == "__main__":
    main()