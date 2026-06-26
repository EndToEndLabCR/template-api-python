"""
User feature dependency factories — use cases wired directly (no service layer).
"""

from fastapi import Depends

from src.app.composition.repositories import get_user_repository
from src.app.features.user.application.use_cases.delete_user_by_id import (
    DeleteUserByIdUseCase,
)
from src.app.features.user.application.use_cases.get_user_by_id import (
    GetUserByIdUseCase,
)
from src.app.features.user.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


async def get_user_by_id_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(repo)


async def get_delete_user_use_case(
    repo: UserRepositoryImpl = Depends(get_user_repository),
) -> DeleteUserByIdUseCase:
    return DeleteUserByIdUseCase(repo)

