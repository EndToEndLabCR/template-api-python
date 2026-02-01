from typing import Optional, List

from sqlalchemy import select

from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.repositories.user_repository import UserRepository
from src.app.features.domain.value_objects.email import Email
from src.app.features.infrastructure.models.user_model import UserModel
from src.app.features.infrastructure.repository.user_model_mapper import map_model_to_entity
from src.shared.domain.repositories.base_repository import ID, T

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.value_objects.entity_id import EntityId
from src.shared.utils.log_util import log


class UserRepositoryImpl(UserRepository):

    def __init__(self, db_session: AsyncSession):
        """
        Initializes the UserRepositoryImpl with a SQLAlchemy AsyncSession.

        Args:
            db_session (AsyncSession): The SQLAlchemy session to use for database operations.
        """
        self.db_session = db_session

    async def find_by_id(self, entity_id: EntityId) -> Optional[UserEntity]:
        """
        Find a user by their unique identifier.
        
        Args:
            entity_id (EntityId): The user's unique identifier.
            
        Returns:
            Optional[UserEntity]: The user entity if found, None otherwise.
            
        Raises:
            Exception: For database-related errors.
        """
        try:
            log.debug(f"Fetching user by id: {entity_id.value}")
            user_model: Optional[UserModel] = await self.db_session.get(UserModel, entity_id.value)

            if user_model is None:
                log.debug(f"User with id {entity_id.value} not found")
                return None

            log.debug(f"User with id {entity_id.value} retrieved successfully")

            return map_model_to_entity(user_model)
        except Exception as e:
            log.error(f"Database error while fetching user by id {entity_id.value}: {str(e)}")
            raise

    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        result = await self.db_session.execute(select(UserModel.email == email.value))

        user_model = result.scalar_one_or_none()

        if user_model is None:
            log.info(f"User with email {email.value} not found.")
            return None

        log.info(f"User with email {email.value} found.")
        return map_model_to_entity(user_model)

    async def find_by_name(self, record: str) -> Optional[UserEntity]:
        pass

    async def save(self, entity: T) -> T:
        pass

    async def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        pass

    async def exists(self, entity_id: ID) -> bool:
        pass

    async def update(self, entity: T) -> Optional[T]:
        pass

    async def delete(self, entity_id: ID) -> bool:
        pass
