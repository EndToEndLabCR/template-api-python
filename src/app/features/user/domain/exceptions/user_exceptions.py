"""Domain-level exceptions for the user feature."""


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""

    def __init__(self, email: str):
        self.email = email
        self.message = f"User with email {email} already exists."
        super().__init__(self.message)


class UserNotFoundError(Exception):
    """Raised when a user is not found by ID or email."""

    def __init__(self, identifier: str):
        self.identifier = identifier
        self.message = f"User not found: {identifier}"
        super().__init__(self.message)
