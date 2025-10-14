from abc import abstractmethod
from typing import Optional, List

from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.value_objects.email import Email
from src.shared.domain.repositories.base_repository import BaseRepository, ID, T
from src.shared.domain.value_objects.entity_id import EntityId


class UserRepository(BaseRepository[UserEntity, EntityId]):

    async def save(self, entity: T) -> T:
        pass

    async def find_by_id(self, entity_id: ID) -> Optional[T]:
        pass

    async def find_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        pass

    async def exists(self, entity_id: ID) -> bool:
        pass

    async def update(self, entity: T) -> Optional[T]:
        pass

    async def delete(self, entity_id: ID) -> bool:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        """
        Find a user by their email address.

        Args:
            email (Email): The email address to search for.

        Returns:
            Optional[UserEntity]: The user entity if found, otherwise None.
        """
        pass

    @abstractmethod
    async def find_by_name(self, record: str) -> Optional[UserEntity]:
        """
        Find a user by their name.

        Args:
            record (str): The name of the user to search for.

        Returns:
            Optional[UserEntity]: The user entity if found, otherwise None.
        """
        pass