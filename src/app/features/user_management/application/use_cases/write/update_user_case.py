from src.app.features.user_management.application.dtos.user_dto import UpdateUserRequest, UserResponse
from src.app.features.user_management.application.exceptions.user_exceptions import UserDoesNotExistException
from src.app.features.user_management.application.dtos.user_dto_mapper import map_entity_to_dto_user
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.shared.utils.log_util import log
from src.shared.utils.uuid_util import convert_str_to_uuid


class UpdateUserUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str, update_user: UpdateUserRequest) -> UserResponse:
        log.info(f"Starting update user process for user ID: '{user_id}'")

        try:
            log.debug(f"Converting user ID string to UUID: '{user_id}'")
            uuid = convert_str_to_uuid(user_id)
            user_uuid = UserId(uuid)

            log.debug(f"Searching for user in repository with ID: {user_uuid}")
            existing_user = await self.user_repository.find_by_id(user_uuid)

            if not existing_user:
                log.warning(f"User not found with ID: {user_uuid}")
                raise UserDoesNotExistException(f"User with id {user_uuid} does not exist.")

            log.info(f"User found successfully with ID: {user_uuid}")

            existing_user.update_personal_info(
                first_name=update_user.first_name,
                last_name=update_user.last_name
            )
            log.debug("User personal information updated successfully")

            await self.user_repository.update(existing_user)
            log.info(f"User updated successfully in repository with ID: {user_uuid}")

            response_dto = map_entity_to_dto_user(existing_user)
            log.info(f"Update user process completed successfully for ID: '{user_id}'")

            return response_dto

        except ValueError as e:
            log.error(f"Invalid UUID format for user ID '{user_id}': {str(e)}")
            raise ValueError(f"Invalid user ID format: {user_id}")

        except Exception as e:
            log.error(f"Unexpected error during user update for ID '{user_id}': {str(e)}")
            raise
