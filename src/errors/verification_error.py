# Path: src/errors/verification_error.py
class VerificationError(Exception):
    """Exception raised for errors in the input."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
