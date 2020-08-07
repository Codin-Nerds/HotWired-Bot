import typing as t

import requests

RESPONSES = {
    200: True,
    301: "Switching to a different endpoint",
    400: "Bad Request",
    401: "Not Authenticated",
    404: "The resource you tried to access wasn’t found on the server.",
    403: "The resource you’re trying to access is forbidden — you don’t have the right permissions to see it.",
}


def to_base(base: t.Literal[2, 8, 16], number: int) -> str:
    """Convert any passed integer into given base as string."""
    if base == 2:
        return bin(number).replace("0b", "")
    if base == 8:
        return oct(number).replace("0o", "")
    if base == 16:
        return hex(number).replace("0x", "")
    raise ValueError("Unkown based used.")


def base_calculator(base: int, num1: str, num2: str, operator: t.Literal["+", "-", "*", "/"]) -> str:
    """I love calculators."""
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


# TODO : use aiohttp
def get_math_results(equation: str) -> str:
    """Use `api.mathjs.org` to calculate any given equation."""
    params = {"expr": equation}
    url = "http://api.mathjs.org/v4/"
    r = requests.get(url, params=params)

    try:
        response = RESPONSES[r.status_code]
    except KeyError:
        response = "Invalid Equation"

    if response is True:
        return r.text
    return response
