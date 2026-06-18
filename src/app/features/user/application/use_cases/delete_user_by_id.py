from app.features.user.application.exceptions.user_exception import UserDoesNotExistException
from app.shared.domain.value_objects.entity_id import EntityId
from app.shared.utils.log_util import log


class DeleteUserByIdUseCase:

    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> bool:

        try:
            user_obj_id = EntityId.from_string(user_id)

            deleting_user = await self.user_repository.delete(user_obj_id)

            if not deleting_user:
                log.warning(f"User not found for deletion with ID: {user_id}")
                raise UserDoesNotExistException(user_id)

            return True

        except Exception as e:
            log.error(f"Unexpected error during delete user by ID for {user_id}: {str(e)}")
            raise
