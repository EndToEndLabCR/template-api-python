class InvalidCredentialsException(Exception):
    """Exception raised when login credentials are invalid."""

    def __init__(self):
        self.message = "Invalid email or password."
        super().__init__(self.message)
