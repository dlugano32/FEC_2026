from TP1.GF2m import GF2m
from TP1.GFPoly import GFPoly

def main():
    # GF(2^5) generado por : P(x) = x^5 + x^2 + 1

    gf32 = GF2m(m=5, primitive_poly=0b00101)

    zero   = gf32.element(0b00000)
    one    = gf32.element(0b00001)
    alpha  = gf32.element(0b00010)

    print("\n=========================================")
    print("GF(2^5) - Tabla de potencias de alpha")
    print("=========================================")

    current = one
    seen_values = set()

    for exponent in range(31):
        value = int(current)

        print(f"alpha^{exponent:2d} = {value:05b}")

        if value in seen_values:
            print(f"ERROR: el valor {value:05b} se repitió en alpha^{exponent}")

        seen_values.add(value)

        current = current * alpha

    print("\n=========================================")
    print("Pruebas del campo")
    print("=========================================")

    print("[Test 1]: Cantidad de elementos no nulos distintos:", len(seen_values))
    print("[Test 2]: alpha^31 == 1:", alpha ** 31 == one)

    is_order_31 = True

    for exponent in range(1,31):
        if alpha ** exponent == one:
            print(f"Error: alpha^{exponent} = 1. El polinomio no es primitivo")
            is_order_31 == False

    print("[Test 3]: El orden del polinomio es 31:", is_order_31)

    inverse_test_ok = True

    for value in range(1,gf32.order):
        element = gf32.element(value)

        if element * element.inverse() != one:
            inverse_test_ok = False
            print(f"ERROR en inverso para elemento {value:05b}")

    print("[Test 4]: a * inverse(a) == 1 para todo a != 0:", inverse_test_ok)

    multiplication_conmutative = True

    for a_value in range(gf32.order):
        for b_value in range(gf32.order):
            a = gf32.element(a_value)
            b = gf32.element(b_value)

            if a*b != b*a:
                print(f"ERROR de conmutatividad entre a={a_value:05b} y b={b_value:05b}")
                multiplication_conmutative = False

    print("[Test 5]: Conmutatividad en multiplicación : ", multiplication_conmutative)

    print("\n========================================")
    print("Pruebas de casos especiales")
    print("========================================")

    print("0 * alpha =", zero * alpha)
    print("alpha^0 =", alpha ** 0)

    try:
        zero.inverse()
    except ZeroDivisionError as error:
        print("Inverso de cero:", error)

if __name__ == "__main__":
    main()