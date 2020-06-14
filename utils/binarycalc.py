import typing as t


def to_binary(number: int) -> str:
    """Convert any passed integer into binary string."""
    return bin(number).replace("0b", "")


def binary_to_decimal(number: str) -> int:
    """Convert any binary string into integer."""
    return int(number, 2)


def is_binary(*args: t.List[str]) -> bool:
    """Check if all passed strings only consists of 1s or 0s."""
    all("1" == char or "0" == char for string in args for char in string)


def binaryop(num1: str, num2: str, op: t.Literal["+", "-", "*", "/"]) -> str:
    if is_binary(num1, num2):
        num1 = binary_to_decimal(num1)
        num2 = binary_to_decimal(num2)

        if op == "+":
            return to_binary(num1 + num2)
        elif op == "-":
            return to_binary(num1 - num2)
        elif op == "*":
            return to_binary(num1 * num2)
        elif op == "/":
            try:
                return to_binary(num1 / num2)
            except ZeroDivisionError:
                return "N/A (ZERO DIVISION)"
        else:
            return "Invalid Binary Number"
