from typing import List

from src.app.features.user_management.application.dtos.user_dto import CreateUserRequest, UserResponse, UpdateUserRequest
from src.app.features.user_management.application.use_cases.write.delete_user_case import DeleteUserUseCase
from src.app.features.user_management.application.use_cases.write.create_user_case import CreateUserUseCase
from src.app.features.user_management.application.use_cases.write.update_user_case import UpdateUserUseCase
from src.app.features.user_management.application.use_cases.read.get_all_users_case import GetAllUsersUseCase
from src.app.features.user_management.application.use_cases.read.get_user_by_id_case import GetUserByIdUseCase
from src.app.features.user_management.application.use_cases.read.get_users_by_role_case import GetUsersByRoleUseCase
from src.app.features.user_management.domain.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, create_user_dto: CreateUserRequest) -> UserResponse:
        use_case = CreateUserUseCase(self.user_repository)

        return await use_case.execute(create_user_dto)

    async def update_user(self, user_id: str, update_user: UpdateUserRequest):
        use_case = UpdateUserUseCase(self.user_repository)

        return await use_case.execute(user_id, update_user)

    async def delete_user(self, user_id: str):
        use_case = DeleteUserUseCase(self.user_repository)

        await use_case.execute(user_id)

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        use_case = GetUserByIdUseCase(self.user_repository)

        return await use_case.execute(user_id)

    async def get_users_by_role(self, role: str, limit: int = 10, offset: int = 0) -> List[UserResponse]:
        use_case = GetUsersByRoleUseCase(self.user_repository)

        return await use_case.execute(role, limit, offset)

    async def get_all_users(self, limit: int = 10, offset: int = 0) -> List[UserResponse]:
        use_case = GetAllUsersUseCase(self.user_repository)

        return await use_case.execute(limit, offset)
