from datetime import datetime
from typing import Optional

from src.app.features.domain.value_objects.email import Email
from src.shared.domain.entities.base_entity import BaseEntity
from src.shared.domain.value_objects.entity_id import EntityId


class UserEntity(BaseEntity):

    def __init__(self, id: EntityId, email: Email, first_name: str, last_name: str, password_hash: str,
                 password_reset_token_hash: Optional[str] = None,
                 password_reset_expires_at: Optional[datetime] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):

        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password_hash = password_hash
        self.password_reset_token_hash = password_reset_token_hash
        self.password_reset_expires_at = password_reset_expires_at
        super().__init__(id, created_at, updated_at)
