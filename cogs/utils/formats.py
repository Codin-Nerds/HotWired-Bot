class Plural:
    """"If the amount is many, Change singular to plural Form."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __format__(self, format_spec: str) -> str:
        val = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(val) != 1:
            return f"{val} {plural}"
        return f"{val} {singular}"
