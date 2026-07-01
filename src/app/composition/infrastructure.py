"""
Infrastructure dependencies: database session, JWT handler, etc.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config.app_config import AppConfig
from src.app.shared.infrastructure.security.jwt_handler import JWTHandler
from src.app.shared.persistence.engine_factory import get_engine

_config = AppConfig.instance()


@lru_cache(maxsize=1)
def get_jwt_handler() -> JWTHandler:
    """Singleton JWTHandler wired from config. Cached via lru_cache."""
    return JWTHandler(
        secret_key=_config.get_config("security.jwt.secret_key", ""),
        algorithm=_config.get_config("security.jwt.algorithm", "HS256"),
        expiration_minutes=int(
            _config.get_config("security.jwt.access_token_expire_minutes", 1440)
        ),
        refresh_expiration_minutes=10080,  # 7 days
    )


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session from the singleton engine."""
    engine = get_engine()
    async with engine.get_session() as session:
        yield session
