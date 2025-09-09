class UserAlreadyExistsException(Exception):
    """
    Exception raised when attempting to create a user that already exists.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UserDoesNotExistException(Exception):
    """
    Exception raised when a user does not exist in the repository.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InvalidRoleException(Exception):
    """
    Exception raised when an invalid role is provided.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
