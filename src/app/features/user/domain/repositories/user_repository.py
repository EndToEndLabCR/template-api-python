from abc import ABC, abstractmethod
from typing import Optional

from src.app.features.user.domain.entities.user_entity import UserEntity
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId


class UserRepository(ABC):
    """Contract for user persistence operations."""

    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[UserEntity]:
        """Retrieve a user by their unique identifier."""

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        """Retrieve a user by email address."""

    @abstractmethod
    async def find_by_reset_token_hash(self, token_hash: str) -> Optional[UserEntity]:
        """Retrieve a user by the SHA-256 hash of their password-reset token."""

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 20) -> list[UserEntity]:
        """Retrieve a paginated list of user entities."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of users."""

    @abstractmethod
    async def save(self, user: UserEntity) -> UserEntity:
        """Persist a new user entity."""

    @abstractmethod
    async def update(self, entity: UserEntity) -> Optional[UserEntity]:
        """Persist changes to an existing user entity."""

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        """Remove a user by identifier. Returns True if deleted, False if not found."""
