from typing import Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config.app_config import AppConfig
from src.app.features.user_management.application.services.user_service import UserService
from src.app.features.user_management.infrastructure.persistence.postgres.repository.user_repository_impl import \
    UserRepositoryImpl
from src.shared.infrastructure.database.postgres.postgres_db_session_manager import PostgresDbSessionManager

# Create a global session manager instance
postgres_config = AppConfig.instance().get_config("postgres", {})
postgres_db_session_manager = PostgresDbSessionManager(postgres_config)


async def get_database_session() -> AsyncGenerator[Any, Any]:
    """
    Dependency to get a database session.
    """
    async with postgres_db_session_manager.get_session() as session:
        yield session


async def get_user_service(session: AsyncSession = Depends(get_database_session)) -> UserService:
    """
    Dependency to get UserService with proper session management.
    """
    user_repository = UserRepositoryImpl(session)

    return UserService(user_repository)
