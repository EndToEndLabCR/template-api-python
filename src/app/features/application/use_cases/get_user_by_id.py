from uuid import UUID

from src.app.features.application.dtos.user_dto_mapper import UserResponse, map_entity_to_dto_user
from src.app.features.domain.repositories.user_repository import UserRepository
from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class GetUserByIdUseCase:


    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository


    async def execute(self, user_id: str) -> UserResponse:

        # TODO add try/except with logging and custom exceptions
        user_uuid = UUID(user_id)
        user_obj_id = EntityId(user_uuid)

        existing_user = await self.user_repository.find_by_id(user_obj_id)

        if not existing_user:
            log.warning(f"User not found with ID: {existing_user.id}")
            raise Exception(f"User with ID {user_id} does not exist.")

        response_dto = map_entity_to_dto_user(existing_user)

        return response_dto