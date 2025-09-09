from typing import List

from src.app.features.user_management.application.dtos.user_dto import UserResponse
from src.app.features.user_management.application.dtos.user_dto_mapper import map_entity_to_dto_user
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.shared.application.base_use_case import BaseUseCase
from src.shared.utils.log_util import log


class GetAllUsersUseCase(BaseUseCase):

    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self.user_repository = user_repository

    async def execute(self, limit: int = 10, offset: int = 0) -> List[UserResponse]:
        log.info("Getting all users with limit %d and offset %d", limit, offset)

        self.validate_pagination(limit, offset)

        users_db = await self.user_repository.find_all(limit, offset)

        log.info("Found %d users", len(users_db))

        users_response = []
        for user in users_db:
            users_response.append(map_entity_to_dto_user(user))

        return users_response
