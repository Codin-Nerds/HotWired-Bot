import typing as t


def celsius_to_fahrenheit(input: int) -> t.Union[float, int]:
    """Converts Celsius (input) into Fahrenheit (output)."""
    return (input * 1.8) + 32
