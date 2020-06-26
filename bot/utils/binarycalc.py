import typing as t


def to_binary(number: int) -> str:
    """Convert any passed integer into binary string."""
    return bin(number).replace("0b", "")


def binaryop(num1: str, num2: str, operator: t.Literal["+", "-", "*", "/"]) -> str:
    try:
        num1 = int(num1, 2)
        num2 = int(num2, 2)
    except ValueError:
        return "Invalid Binary Number"

    operations = {
        "+": lambda n1, n2: to_binary(n1 + n2),
        "-": lambda n1, n2: to_binary(n1 - n2),
        "*": lambda n1, n2: to_binary(n1 * n2),
        "/": lambda n1, n2: to_binary(n1 / n2),
    }

    try:
        return operations[operator](num1, num2)
    except ZeroDivisionError:
        return "N/A (ZERO DIVISION)"
