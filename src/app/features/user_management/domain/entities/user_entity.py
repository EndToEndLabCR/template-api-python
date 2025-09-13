from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from src.app.features.user_management.domain.entities.user_enums import UserRole, UserStatus
from src.app.features.user_management.domain.value_objects.email import Email
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.shared.utils.date_util import get_current_datetime


@dataclass
class UserEntity:
    first_name: str
    last_name: str
    email: Email
    user_role: UserRole
    id: UserId = None
    user_status: UserStatus = UserStatus.ACTIVE
    password_hash: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.id is None:
            self.id = UserId.generate()
        if self.created_at is None:
            self.created_at = get_current_datetime()
        if self.updated_at is None:
            self.updated_at = get_current_datetime()

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: Email,
        user_role: UserRole,
        user_id: Optional[UserId] = None,
        user_status: UserStatus = UserStatus.ACTIVE,
        password_hash: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> "UserEntity":
        return cls(
            id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_role=user_role,
            user_status=user_status,
            password_hash=password_hash,
            created_at=created_at,
            updated_at=updated_at,
        )

    @property
    def fullname(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        return self.user_status == UserStatus.ACTIVE

    def update_personal_info(
            self,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
    ):
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name

        self.updated_at = get_current_datetime()

    def change_status(self, new_status: UserStatus):
        if self.user_status != new_status:
            self.user_status = new_status
            self.updated_at = get_current_datetime()
