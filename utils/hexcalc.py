import typing as t


def to_hex(number: int) -> str:
    """Convert any passed integer into hexadecimal string."""
    return hex(number).replace("0x", "")


def hexop(num1: str, num2: str, operator: t.Literal["+", "-", "*", "/"]) -> str:
    try:
        num1 = int(num1, 16)
        num2 = int(num2, 16)
    except ValueError:
        return "Invalid Hexadecimal Number"

    operations = {
        "+": lambda n1, n2: to_hex(n1 + n2),
        "-": lambda n1, n2: to_hex(n1 - n2),
        "*": lambda n1, n2: to_hex(n1 * n2),
        "/": lambda n1, n2: to_hex(n1 / n2),
    }

    try:
        return operations[operator](num1, num2)
    except ZeroDivisionError:
        return "N/A (ZERO DIVISION)"
