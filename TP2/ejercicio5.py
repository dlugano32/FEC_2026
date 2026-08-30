from TP1.GF2m import GF2m
from TP2.ejercicio4 import hamming_weight, matrix_matrix_product, vector_matrix_product


B_HEX = [
    0x98F,
    0x4E7,
    0x357,
    0xBE2,
    0xDD1,
    0x7CC,
    0x53D,
    0x2BE,
    0x87B,
    0xE74,
    0xF1A,
    0xEA9,
]


def int_to_gf2_vector(value, width, field):
    """Convierte un entero en un vector de bits, comenzando por el MSB"""

    vector = []

    for i in range(width):
        bit = (value >> (width - 1 - i)) & 1
        vector.append(field.element(bit))

    return vector


def gf2_vector_to_int(vector):
    """Convierte un vector de elementos de GF(2) en un entero"""

    value = 0

    for element in vector:
        value = (value << 1) | int(element)

    return value


def identity_matrix(size, field):
    """Construye una matriz identidad sobre el campo recibido"""

    matrix = []

    for i in range(size):
        row = []

        for j in range(size):
            if i == j:
                row.append(field.element(1))
            else:
                row.append(field.element(0))

        matrix.append(row)

    return matrix


def transpose(matrix):
    """Devuelve la matriz transpuesta"""

    rows = len(matrix)
    columns = len(matrix[0])
    result = []

    for j in range(columns):
        result_row = []

        for i in range(rows):
            result_row.append(matrix[i][j])

        result.append(result_row)

    return result


def matrices_are_equal(matrix_a, matrix_b):
    """Compara dos matrices elemento por elemento"""

    if len(matrix_a) != len(matrix_b):
        return False

    if len(matrix_a[0]) != len(matrix_b[0]):
        return False

    for i in range(len(matrix_a)):
        for j in range(len(matrix_a[0])):
            if matrix_a[i][j] != matrix_b[i][j]:
                return False

    return True


def is_zero_matrix(matrix):
    """Indica si todos los elementos de una matriz son cero"""

    for row in matrix:
        for element in row:
            if int(element) != 0:
                return False

    return True


def encode(message, k, G, field):
    """Codifica un mensaje de k bits mediante v = m * G"""

    message_vector = int_to_gf2_vector(message, k, field)
    return vector_matrix_product(message_vector, G)


def main():

    # Extended Golay Code (24,12)
    # n = 24 , k = 12, m = 12
    n = 24
    k = 12
    redundancy = n - k

    gf2 = GF2m(m=1, primitive_poly=0b1)

    B = []

    for value in B_HEX:
        B.append(int_to_gf2_vector(value, redundancy, gf2))

    identity = identity_matrix(k, gf2)
    B_transpose = transpose(B)
    G = []
    H = []

    for i in range(k):
        G.append(identity[i] + B[i])

    for i in range(redundancy):
        H.append(B_transpose[i] + identity[i])

    # La matriz B debe ser simetrica e involutoria
    assert matrices_are_equal(B, transpose(B))
    assert matrices_are_equal(matrix_matrix_product(B, B), identity)

    # G * H^T debe ser la matriz nula
    G_times_H_transpose = matrix_matrix_product(G, transpose(H))
    assert is_zero_matrix(G_times_H_transpose)

    # Verificacion Ejercicio 1
    message = 0xA5C
    codeword = encode(message, k, G, gf2)
    syndrome = vector_matrix_product(codeword, transpose(H))

    assert hamming_weight(syndrome) == 0

    print("B es simetrica: OK")
    print("B^2 = I: OK")
    print("G * H^T = 0: OK")

    print(f"Mensaje: 0x{message:03X}")
    print(f"Codeword: 0x{gf2_vector_to_int(codeword):06X}")
    print("Sindrome nulo: OK")


    # Weight distribution
    distribution = {}

    for message in range(2**k):
        codeword = encode(message, k, G, gf2)
        weight = hamming_weight(codeword)

        #codeword_value = gf2_vector_to_int(codeword)
        #print(f"Codeword[{message:2d}] = "f"{codeword_value:024b}")

        if weight not in distribution:
            distribution[weight] = 0

        distribution[weight] += 1


    print("Distribucion de pesos:")
    for weight in distribution:
        print(f"  peso {weight:2d}: {distribution[weight]}")

if __name__ == "__main__":
    main()
