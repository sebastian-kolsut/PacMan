class InvalidFileSufixError(Exception):
    """Raised when the config file path does not end in ".json"."""

    def __init__(self, message: str) -> None:
        """Initialize the error with a human-readable message.

        Args:
            message: Description of why the file suffix is invalid.
        """
        super().__init__(message)
        self.message = message
