import typing as t
import chardet


def celsius_to_fahrenheit(input: int) -> t.Union[float, int]:
    """Converts Celsius (input) into Fahrenheit (output)."""
    return (input * 1.8) + 32


def decode(content: bytes, codec: str = 'utf8') -> str or bytes:
    if not type(content) == bytes:
        return content
    try:
        content = content.decode()
    except UnicodeDecodeError:
        try:
            content = content.decode(codec)
        except UnicodeDecodeError:
            try:
                chardetres = chardet.detect(content)
                content = content.decode(chardetres['encoding'])
            except TypeError:
                return content
    return content
