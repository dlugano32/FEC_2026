from GF2m import GF2m
from GFPoly import GFPoly


def main():
    # GF(2^4) generado por:
    # P(x) = x^4 + x + 1
    # El término x^4 es implícito:
    # x + 1 -> 0b0011

    gf16 = GF2m(m=4, primitive_poly=0b0011)

    # Elementos del campo.
    zero     = gf16.element(0b0000)
    one      = gf16.element(0b0001)
    alpha    = gf16.element(0b0010)
    alpha_2  = gf16.element(0b0100)
    alpha_3  = gf16.element(0b1000)
    alpha_4  = gf16.element(0b0011)
    alpha_5  = gf16.element(0b0110)
    alpha_6  = gf16.element(0b1100)
    alpha_7  = gf16.element(0b1011)
    alpha_8  = gf16.element(0b0101)
    alpha_9  = gf16.element(0b1010)
    alpha_10 = gf16.element(0b0111)
    alpha_11 = gf16.element(0b1110)
    alpha_12 = gf16.element(0b1111)
    alpha_13 = gf16.element(0b1101)
    alpha_14 = gf16.element(0b1001)

    print("\n==== Operaciones básicas en GF(2^m) ====")

    print("alpha^3 + alpha^9 =", alpha_3 + alpha_9)
    print("alpha^3 - alpha^9 =", alpha_3 - alpha_9)
    print("alpha^6 * alpha^11 =", alpha_6 * alpha_11)
    print("alpha_14^3 =", alpha_14 ** 3)
    print("inverso de alpha_7 =", alpha_7.inverse())
    print("alpha^3 / alpha^10 =", alpha_3 / alpha_10)

    # Se utilizaron los resultados de la guia como referencia

    print("\n==== Polinomios sobre un GF(2^m) ====")

    # a(x) = x^2 + alpha*x + alpha^2
    a = GFPoly(gf16, [one, alpha, alpha_2])

    # b(x) = x + alpha
    b = GFPoly(gf16, [one, alpha])

    print("a(x) =", a.coefficients)
    print("b(x) =", b.coefficients)

    # Suma:
    # a(x) + b(x) = (x^2 + alpha*x + alpha^2) + (x + alpha)
    # = x^2 + (alpha + 1)x + (alpha^2 + alpha)
    # = x^2 + alpha^4*x + alpha^5
    print("\na(x) + b(x) =", (a + b).coefficients)


    # Multiplicación:
    # a(x) * b(x)
    #
    # = (x^2 + alpha*x + alpha^2)(x + alpha)
    #
    # = x^3 + alpha*x^2 + alpha*x^2 + alpha^2*x + alpha^2*x + alpha^3
    #
    # = x^3 + alpha^3
    print("a(x) * b(x) =", (a * b).coefficients)


    # División:
    # a(x) / b(x)
    #
    # a(x) = b(x) * q(x) + r(x)
    #
    # a(x) = (x + alpha)(x) + alpha^2
    #
    # q(x): x
    # r(x): alpha^2
    quotient, remainder = a.divide(b)

    print("a(x) / b(x)")
    print("  q(x) =", quotient.coefficients)
    print("  r(x) =", remainder.coefficients)

    # Escalado:
    #
    # = alpha*a(x)
    # = alpha*x^2 + alpha^2*x + alpha^3
    print("\nalpha * a(x) =", a.scale(alpha).coefficients)

    # Evaluación:
    #
    # = a(alpha)
    # = alpha^2 + alpha*alpha + alpha^2
    # = alpha^2 + alpha^2 + alpha^2
    # = alpha^2
    print("a(alpha) =", a.evaluate(alpha))

    # Construcción a partir de raíces:
    #
    # c(x) = (x + alpha)(x + alpha^2)
    #
    # = x^2 + (alpha + alpha^2)x + alpha^3
    # = x^2 + alpha^5*x + alpha^3
    roots_poly = GFPoly.from_roots(gf16, [alpha, alpha_2])

    print("\nPolinomio con raíces alpha y alpha^2 =", roots_poly.coefficients)

    # Evaluación del polinomio en raices: ambos deberian dar cero
    print("Evaluacion c(alpha) =", roots_poly.evaluate(alpha))

    print("Evaluacion c(alpha^2) =", roots_poly.evaluate(alpha_2))

    print("\n==== Pruebas de errores ====")

    try:
        zero.inverse()
    except ZeroDivisionError as error:
        print("Inverso de cero:", error)

    try:
        alpha / zero
    except ZeroDivisionError as error:
        print("División por cero:", error)

    try:
        alpha ** -1
    except ValueError as error:
        print("Exponente negativo:", error)

    try:
        alpha + 1
    except TypeError as error:
        print("Operación con un entero:", error)


if __name__ == "__main__":
    main()