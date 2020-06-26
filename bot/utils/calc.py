import typing as t


def to_base(base: t.Literal[2, 8, 16], number: int) -> str:
    """Convert any passed integer into given base as string."""
    if base == 2:
        return bin(number).replace("0b", "")
    elif base == 8:
        return oct(number).replace("0o", "")
    elif base == 16:
        return hex(number).replace("0x", "")


def base_calculator(base: int, num1: str, num2: str, operator: t.Literal["+", "-", "*", "/"]) -> str:
    try:
        num1 = int(num1, base)
        num2 = int(num2, base)
    except ValueError:
        return f"Invalid Base-{base} Number"

    operations = {
        "+": lambda n1, n2: to_base(base, n1 + n2),
        "-": lambda n1, n2: to_base(base, n1 - n2),
        "*": lambda n1, n2: to_base(base, n1 * n2),
        "/": lambda n1, n2: to_base(base, n1 / n2),
    }

    try:
        return operations[operator](num1, num2)
    except ZeroDivisionError:
        return "N/A (ZERO DIVISION)"
