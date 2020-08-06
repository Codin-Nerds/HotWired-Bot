class Plural:
    """If the amount is many, change singular to plural form."""

    def __init__(self, value: int) -> None:
        """Get the amount."""
        self.value = value

    def __format__(self, format_spec: str) -> str:
        """Format a message with the stored amount."""
        singular, _, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(self.value) != 1:
            return f"{self.value} {plural}"
        return f"{self.value} {singular}"
