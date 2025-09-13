from uuid import UUID

from src.app.features.user_management.application.dtos.user_dto import UserResponse
from src.app.features.user_management.application.exceptions.user_exceptions import UserDoesNotExistException
from src.app.features.user_management.application.dtos.user_dto_mapper import map_entity_to_dto_user
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.shared.utils.log_util import log


class GetUserByIdUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> UserResponse:
        log.info(f"Starting get user by ID process for ID: {user_id}")

        try:
            # Validate and convert user ID to UUID
            log.debug(f"Converting user ID string to UUID: {user_id}")
            user_uuid = UUID(user_id)
            user_id_obj = UserId(user_uuid)

            log.debug(f"Searching for user in repository with ID: {user_id}")
            existing_user = await self.user_repository.find_by_id(user_id_obj)

            if not existing_user:
                log.warning(f"User not found with ID: {user_id}")
                raise UserDoesNotExistException(f"User with ID {user_id} does not exist.")

            log.info(f"User found successfully: {user_id}")
            log.debug(f"User details - Email: {existing_user.email.value}, Role: {existing_user.user_role}")

            # Create response DTO
            response_dto = map_entity_to_dto_user(existing_user)

            log.info(f"Get user by ID process completed successfully for ID: {user_id}")
            return response_dto

        except ValueError as e:
            log.error(f"Invalid UUID format for user ID {user_id}: {e}")
            raise ValueError(f"Invalid user ID format: {user_id}")
        except UserDoesNotExistException:
            log.error(f"User does not exist with ID: {user_id}")
            raise
        except Exception as e:
            log.error(f"Unexpected error during get user by ID for {user_id}: {str(e)}")
            raise
