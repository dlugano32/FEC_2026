from TP1.GF2m import GF2m
from TP1.GFPoly import GFPoly

def vector_matrix_product(vector, matrix):
    """Multiplica un vector fila por una matriz"""

    rows = len(matrix)
    columns = len(matrix[0])

    if len(vector) != rows:
        raise ValueError("Las dimensiones del vector y la matriz no coinciden")

    gf = vector[0].field
    result = []

    # result[j] = sum(vector[i] * matrix[i][j])
    for j in range(columns):
        value = gf.element(0)

        for i in range(rows):
            value = value + vector[i] * matrix[i][j]

        result.append(value)

    return result


def matrix_matrix_product(matrix_a, matrix_b):
    """Multiplica dos matrices."""

    rows_a = len(matrix_a)
    columns_a = len(matrix_a[0])
    rows_b = len(matrix_b)
    columns_b = len(matrix_b[0])

    if columns_a != rows_b:
        raise ValueError("Las dimensiones de las matrices no coinciden")

    gf = matrix_a[0][0].field
    result = []

    # result[i][j] = sum(matrix_a[i][k] * matrix_b[k][j])
    for i in range(rows_a):
        result_row = []

        for j in range(columns_b):
            value = gf.element(0)

            for k in range(columns_a):
                value = value + matrix_a[i][k] * matrix_b[k][j]

            result_row.append(value)

        result.append(result_row)

    return result


def hamming_weight(vector):
    """Cuenta la cantidad de elementos iguales a uno"""

    weight = 0

    for element in vector:
        if int(element) == 1:
            weight += 1

    return weight


def vector_to_int(vector):
    """Convierte un vector de GFElement a una lista de enteros"""

    result = []

    for element in vector:
        result.append(int(element))

    return result


def main():
    # P(x) = x + 1. GF2m recibe solamente el termino independiente, porque el termino x^m se encuentra implicito
    gf2 = GF2m(m=1, primitive_poly=0b1)

    zero = gf2.element(0)
    one = gf2.element(1)
    elements = [zero, one]

    addition_table = []
    product_table = []

    for a in elements:
        addition_row = []
        product_row = []

        for b in elements:
            addition_row.append(int(a + b))
            product_row.append(int(a * b))

        addition_table.append(addition_row)
        product_table.append(product_row)

    # El unico elemento no nulo de GF(2) es 1
    inverse_table = [int(one.inverse())]

    print("Tabla de suma:")
    print(addition_table)
    print("Tabla de producto:")
    print(product_table)
    print("Inverso de 1:")
    print(inverse_table)

    assert addition_table == [[0, 1], [1, 0]]
    assert product_table == [[0, 0], [0, 1]]
    assert inverse_table == [1]

    # Comprobacion de GFPoly sobre GF(2):
    # (x + 1)^2 = x^2 + 1.
    x_plus_one = GFPoly(gf2, [one, one])
    squared_polynomial = x_plus_one * x_plus_one

    assert squared_polynomial.to_int() == 0b101

    vector = [one, one, zero]
    matrix = [
        [one, zero],
        [one, one],
        [zero, one],
    ]

    vector_product = vector_matrix_product(vector, matrix)

    print("Producto vector-matriz:")
    print(vector_to_int(vector_product))
    print("Peso de Hamming:")
    print(hamming_weight(vector))

    assert vector_to_int(vector_product) == [0, 1]
    assert hamming_weight(vector) == 2

    identity = [
        [one, zero],
        [zero, one],
    ]

    matrix_product = matrix_matrix_product(matrix, identity)
    expected_matrix = [
        [1, 0],
        [1, 1],
        [0, 1],
    ]

    for i in range(len(matrix_product)):
        assert vector_to_int(matrix_product[i]) == expected_matrix[i]

    print("Producto matriz-matriz:")
    for row in matrix_product:
        print(vector_to_int(row))

if __name__ == "__main__":
    main()
