## GF2m.py

class GF2m:
    """
    Representa un campo de Galois GF(2^m).

    primitive_poly contiene únicamente los m bits inferiores
    del polinomio primitivo. El término x^m queda implícito.

    Ejemplo:
        P(x) = x^4 + x + 1
        primitive_poly = 0b0011
    """

    def __init__(self, m: int, primitive_poly: int):
        if m <= 0:
            raise ValueError("m debe ser un entero positivo")

        if not 0 <= primitive_poly < (1 << m):
            raise ValueError(
                f"El polinomio debe representarse con exactamente {m} bits"
            )

        # Un polinomio primitivo debe tener término independiente 1.
        if primitive_poly & 1 == 0:
            raise ValueError(
                "El polinomio primitivo debe tener término independiente igual a 1"
            )

        self.m = m
        self.primitive_poly = primitive_poly

        # Cantidad de elementos del campo: 2^m.
        self.order = 1 << m

        # Máscara para conservar solamente los m bits inferiores.
        self.mask = self.order - 1

    def element(self, value: int) -> "GFElement":
        """Crea un elemento perteneciente a este campo."""
        return GFElement(self, value)

    def add(self, a: int, b: int) -> int:
        """
        Suma modular en GF(2^m).
        """
        self._validate_value(a)
        self._validate_value(b)

        return a ^ b

    def multiply(self, a: int, b: int) -> int:
        """
        Producto polinómico con reducción módulo P(x):
            suma en GF(2)       → XOR
            multiplicar por x   → desplazamiento a la izquierda
            reducción módulo P  → XOR con primitive_poly
        """

        self._validate_value(a)
        self._validate_value(b)

        result = 0

        while b != 0:
            # Si el bit menos significativo de b es 1,
            # se agrega el polinomio a al resultado.
            if b & 1:
                result ^= a

            # Detecta si a contiene el término x^(m-1).
            # Al desplazarlo aparecería un término x^m.
            carry = a & (1 << (self.m - 1))

            # Multiplicación por x.
            a <<= 1

            # Si apareció x^m, se reduce usando el polinomio primitivo.
            if carry:
                a ^= self.primitive_poly

            # Conserva solamente los m bits inferiores.
            a &= self.mask

            # Avanza al siguiente bit del multiplicador.
            b >>= 1

        return result

    def power(self, a: int, n: int) -> int:
        """
        Calcula a^n mediante exponenciación binaria.

        Se recorren los bits de n desde el menos significativo:
            bit de n igual a 1 → acumular la potencia actual
            siguiente potencia → elevar la base al cuadrado
            siguiente bit      → desplazar n a la derecha

        Solo se admiten exponentes n >= 0.
        """
        self._validate_value(a)

        if n < 0:
            raise ValueError("El exponente debe ser mayor o igual que cero")

        result = 1
        base = a
        exponent = n

        while exponent != 0:
            if exponent & 1:
                result = self.multiply(result, base)

            base = self.multiply(base, base)
            exponent >>= 1

        return result

    def inverse(self, a: int) -> int:
        """
        Calcula el inverso multiplicativo de a.

        Para a != 0:

            a^(-k) = a^(2^m - 2)
        """
        self._validate_value(a)

        if a == 0:
            raise ZeroDivisionError(
                "El elemento 0 no tiene inverso multiplicativo"
            )

        return self.power(a, self.order - 2)

    def divide(self, a: int, b: int) -> int:
        """
        División en GF(2^m):

            a / b = a * b^(-1)
        """
        self._validate_value(a)
        self._validate_value(b)

        if b == 0:
            raise ZeroDivisionError("No se puede dividir por cero")

        return self.multiply(a, self.inverse(b))

    def _validate_value(self, value: int) -> None:
        """Verifica que el entero pertenezca al rango del campo."""
        if not isinstance(value, int):
            raise TypeError("Los elementos del campo deben ser enteros")

        if not 0 <= value < self.order:
            raise ValueError(
                f"El elemento debe estar en el rango [0, {self.order - 1}]"
            )

    def __repr__(self) -> str:
        return (
            f"GF(2^{self.m}, "
            f"P=0b{self.primitive_poly:0{self.m}b})"
        )



class GFElement:
    """Representa un elemento perteneciente a un campo GF(2^m)."""

    def __init__(self, field: GF2m, value: int):
        field._validate_value(value)

        self.field = field
        self.value = value

    def inverse(self) -> "GFElement":
        """Devuelve el inverso multiplicativo del elemento."""
        return GFElement(
            self.field,
            self.field.inverse(self.value)
        )

    def __add__(self, other: "GFElement") -> "GFElement":
        """Suma dos elementos pertenecientes al mismo campo."""
        self._validate_other(other)

        return GFElement(
            self.field,
            self.field.add(self.value, other.value)
        )

    def __sub__(self, other: "GFElement") -> "GFElement":
        """
        Resta dos elementos del mismo campo.

        En GF(2^m), suma y resta son la misma operación.
        """
        return self.__add__(other)

    def __mul__(self, other: "GFElement") -> "GFElement":
        """Multiplica dos elementos pertenecientes al mismo campo."""
        self._validate_other(other)

        return GFElement(
            self.field,
            self.field.multiply(self.value, other.value)
        )

    def __truediv__(self, other: "GFElement") -> "GFElement":
        """Divide dos elementos pertenecientes al mismo campo."""
        self._validate_other(other)

        return GFElement(
            self.field,
            self.field.divide(self.value, other.value)
        )

    def __pow__(self, exponent: int) -> "GFElement":
        """Eleva el elemento a una potencia entera no negativa."""
        return GFElement(
            self.field,
            self.field.power(self.value, exponent)
        )

    def __eq__(self, other) -> bool:
        """Compara dos elementos del mismo campo."""
        if not isinstance(other, GFElement):
            return False

        return (
            self.field is other.field
            and self.value == other.value
        )

    def __int__(self) -> int:
        """Devuelve la representación entera del elemento."""
        return self.value

    def __repr__(self) -> str:
        """Muestra el elemento en representación decimal y binaria."""
        binary = f"{self.value:0{self.field.m}b}"

        return f"GFElement({self.value}, 0b{binary})"

    def _validate_other(self, other: "GFElement") -> None:
        """
        Verifica que el otro operando sea un GFElement perteneciente al mismo campo.
        """
        if not isinstance(other, GFElement):
            raise TypeError(
                "Las operaciones solo se permiten entre elementos GFElement"
            )

        if self.field is not other.field:
            raise ValueError(
                "Los elementos deben pertenecer al mismo campo"
            )