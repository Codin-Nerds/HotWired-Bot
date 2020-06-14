import typing as t


def to_octal(number: int) -> str:
    """Convert any passed integer into octal string."""
    return oct(number).replace("0o", "")


def octop(num1: str, num2: str, operator: t.Literal["+", "-", "*", "/"]) -> str:
    try:
        num1 = int(num1, 8)
        num2 = int(num2, 8)
    except ValueError:
        return "Invalid Octal Number"

    operations = {
        "+": lambda n1, n2: to_octal(n1 + n2),
        "-": lambda n1, n2: to_octal(n1 - n2),
        "*": lambda n1, n2: to_octal(n1 * n2),
        "/": lambda n1, n2: to_octal(n1 / n2),
    }

    try:
        return operations[operator](num1, num2)
    except ZeroDivisionError:
        return "N/A (ZERO DIVISION)"
