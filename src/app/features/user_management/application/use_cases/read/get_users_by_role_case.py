from typing import List

from src.app.features.user_management.application.dtos.user_dto import UserResponse
from src.app.features.user_management.application.exceptions.user_exceptions import InvalidRoleException
from src.app.features.user_management.application.dtos.user_dto_mapper import map_entity_to_dto_user
from src.app.features.user_management.domain.entities.user_enums import UserRole
from src.app.features.user_management.domain.repositories.user_repository import UserRepository
from src.shared.application.base_use_case import BaseUseCase
from src.shared.utils.log_util import log


class GetUsersByRoleUseCase(BaseUseCase):

    def __init__(self, user_repository: UserRepository):
        super().__init__()
        self.user_repository = user_repository

    async def execute(self, role: str, limit: int = 10, offset: int = 0) -> List[UserResponse]:
        log.info(f"Executing GetUsersByRoleUseCase with role: '{role}', limit: {limit}, offset: {offset}")

        log.debug(f"Validating role: '{role}' against available roles: {list(UserRole.__members__.keys())}")
        if role not in UserRole.__members__:
            log.error(f"Invalid role provided: '{role}'. Valid roles are: {list(UserRole.__members__.keys())}")
            raise InvalidRoleException(f"Invalid role: {role}")

        log.debug(f"Role validation passed for: '{role}'")

        log.debug(f"Validating pagination parameters - limit: {limit}, offset: {offset}")
        self.validate_pagination(limit, offset)
        log.debug("Pagination validation passed")

        # Fetch users from the repository
        log.info(f"Fetching users from repository for role: '{role}' with limit: {limit}, offset: {offset}")
        users = []
        try:
            async for user in await self.user_repository.find_by_role(UserRole(role), limit=limit, offset=offset):
                users.append(map_entity_to_dto_user(user))
                log.debug(f"Mapped user entity to DTO for user ID: {getattr(user, 'id', 'unknown')}")

        except Exception as e:
            log.error(f"Error occurred while fetching users by role '{role}': {str(e)}")
            raise

        log.info(f"Successfully retrieved and mapped {len(users)} users for role: '{role}'")

        return users
