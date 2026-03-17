from decimal import Decimal


def is_positive(value: int | float | Decimal) -> bool:
    #Regresa True cuando el valor es mayor que cero.
    return value > 0


def is_non_negative(value: int | float | Decimal) -> bool:
    #Regresa True cuando el valor es cero o más.
    return value >= 0