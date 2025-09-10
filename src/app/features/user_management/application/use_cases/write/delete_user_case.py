from src.app.features.user_management.application.exceptions.user_exceptions import UserDoesNotExistException
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.shared.utils.log_util import log
from src.shared.utils.uuid_util import convert_str_to_uuid


class DeleteUserUseCase:

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> bool:
        """
        Deletes a user by their user_id.
        Raises UserDoesNotExistException if user is not found.
        """
        log.info(f"Executing DeleteUserUseCase for user_id: '{user_id}'")

        try:
            log.debug(f"Converting user_id string '{user_id}' to UUID")
            uuid = convert_str_to_uuid(user_id)
            user_uuid = UserId(uuid)
            log.debug(f"Successfully created UserId from UUID: {user_uuid}")

        except ValueError as e:
            log.error(f"Invalid UUID format for user_id '{user_id}': {str(e)}")
            raise

        log.info(f"Checking if user exists with ID: {user_uuid}")
        existing_user = await self.user_repository.find_by_id(user_uuid)

        if not existing_user:
            log.warning(f"User with id {user_uuid} does not exist, cannot delete")
            raise UserDoesNotExistException(f"User with id {user_uuid} does not exist.")

        log.debug(f"User found, proceeding with deletion for ID: {user_uuid}")

        try:
            await self.user_repository.delete(user_uuid)
            log.info(f"Successfully deleted user with ID: {user_uuid}")

        except Exception as e:
            log.error(f"Error occurred while deleting user with ID {user_uuid}: {str(e)}")
            raise

        return True
