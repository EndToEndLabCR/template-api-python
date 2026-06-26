"""
Shared repositories factories.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.composition.infrastructure import get_database_session
from src.app.features.user.infrastructure.repositories.user_repository_impl import (
    UserRepositoryImpl,
)


async def get_user_repository(
    session: AsyncSession = Depends(get_database_session),
) -> UserRepositoryImpl:
    """Factory for UserRepositoryImpl wired to the current DB session."""
    return UserRepositoryImpl(session)
