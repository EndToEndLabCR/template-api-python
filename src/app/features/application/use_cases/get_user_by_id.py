from uuid import UUID

from src.app.features.application.dtos.user_dto_mapper import UserResponse, map_entity_to_dto_user
from src.app.features.application.exceptions.user_exception import UserDoesNotExistException
from src.app.features.domain.repositories.user_repository import UserRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class GetUserByIdUseCase:
    """
    Use case for retrieving a user by their unique identifier.
    
    This class implements the business logic for fetching user details,
    including validation, error handling, and data mapping.
    """

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the use case with required dependencies.
        
        Args:
            user_repository (UserRepository): Repository for user data access.
        """
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> UserResponse:
        """
        Execute the get user by ID use case.
        
        Args:
            user_id (str): The user's unique identifier as a string.
            
        Returns:
            UserResponse: The user's details mapped to a response DTO.
            
        Raises:
            ValueError: If the user_id format is invalid.
            UserDoesNotExistException: If the user is not found.
            Exception: For any unexpected errors during execution.
        """
        try:
            # Parse and validate UUID using EntityId value object
            user_obj_id = EntityId.from_string(user_id)

            # Retrieve user from repository
            existing_user = await self.user_repository.find_by_id(user_obj_id)

            if not existing_user:
                log.warning(f"User not found with ID: {user_id}")
                raise UserDoesNotExistException(user_id)

            # Map entity to DTO
            response_dto = map_entity_to_dto_user(existing_user)

            return response_dto

        except ValueError as e:
            # UUID validation errors are propagated as-is
            raise
        except UserDoesNotExistException:
            # Re-raise user not found exceptions without additional logging
            raise
        except Exception as e:
            log.error(f"Unexpected error during get user by ID for {user_id}: {str(e)}")
            raise
