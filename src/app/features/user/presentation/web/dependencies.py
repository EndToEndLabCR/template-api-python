from typing import AsyncGenerator, Any

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config.app_config import AppConfig
from app.features.user.application.services.password_service import PasswordService
from app.features.user.application.services.user_service import UserService
from app.features.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from src.shared.infrastructure.config.postgres_db_conn import PostgresDbConnection
from app.shared.utils.config_util import get_config_value

app_config: dict = AppConfig.instance().config


async def get_database_session() -> AsyncGenerator[Any, Any]:
    """
    Dependency to get a database session.
    """
    postgres_config = get_config_value(app_config, "postgres", {})
    postgres_db_session_manager = PostgresDbConnection(postgres_config)

    async with postgres_db_session_manager.get_session() as session:
        yield session



async def get_user_service(session: AsyncSession = Depends(get_database_session)) -> UserService:
    """
    Dependency to get UserService with proper session management.
    """

    user_repository = UserRepositoryImpl(session)

    return UserService(user_repository)


async def get_password_service(session: AsyncSession = Depends(get_database_session)) -> PasswordService:
    """
    Dependency to get PasswordService with proper session management.
    """

    user_repository = UserRepositoryImpl(session)

    return PasswordService(user_repository)