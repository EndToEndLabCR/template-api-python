from src.shared.domain.value_objects.entity_id import EntityId


class UserDoesNotExistException(Exception):
    """Exception raised when a user does not exist."""

    def __init__(self, user_id: EntityId):
        self.user_id = user_id
        self.message = f"User with ID {self.user_id} does not exist."
        super().__init__(self.message)