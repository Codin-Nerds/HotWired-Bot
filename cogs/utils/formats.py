class Plural:
    """"If the amount is many, Change singular to plural Form."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __format__(self, format_spec: str) -> str:
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(self.value) != 1:
            return f"{self.value} {plural}"
        return f"{self.value} {singular}"
