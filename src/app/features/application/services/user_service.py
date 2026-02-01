from src.app.features.application.use_cases.get_user_by_id import GetUserByIdUseCase
from src.app.features.application.dtos.user_dto import UserResponse
from src.app.features.domain.repositories.user_repository import UserRepository


class UserService:
    """
    Service layer for user-related operations.
    
    This class coordinates between the presentation layer and use cases,
    following dependency injection best practices.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize UserService with required dependencies.
        
        Args:
            user_repository (UserRepository): Repository for user data access.
        """
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """
        Retrieve a user by their unique identifier.
        
        Args:
            user_id (str): The user's unique identifier as a string.
            
        Returns:
            UserResponse: The user's details.
            
        Raises:
            ValueError: If the user_id format is invalid.
            UserDoesNotExistException: If the user is not found.
        """
        use_case = GetUserByIdUseCase(self.user_repository)

        return await use_case.execute(user_id)


