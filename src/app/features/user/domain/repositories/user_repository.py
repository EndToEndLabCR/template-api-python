from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.app.features.user.domain.entities.user_entity import UserEntity
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: EntityId) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def find_by_reset_token_hash(self, token_hash: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def save(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    async def update(self, entity: UserEntity) -> Optional[UserEntity]:
        pass

    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        pass

    # ── Password reset (operates at persistence level, not entity level) ──

    @abstractmethod
    async def set_password_reset_token(
        self, email: Email, token_hash: str, expires_at: datetime
    ) -> bool:
        pass

    @abstractmethod
    async def reset_password(
        self, token_hash: str, new_password_hash: str
    ) -> bool:
        pass
