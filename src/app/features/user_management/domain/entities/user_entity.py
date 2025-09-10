from datetime import datetime

from src.app.features.user_management.domain.entities.user_enums import UserRole, UserStatus
from src.app.features.user_management.domain.value_objects.email import Email
from src.app.features.user_management.domain.value_objects.user_id import UserId
from src.shared.utils.date_util import get_current_datetime

from typing import Optional
from pydantic import BaseModel, Field


class UserEntity(BaseModel):
    id: UserId = Field(default_factory=UserId.generate)

    first_name: str
    last_name: str
    email: Email
    role: UserRole
    user_status: UserStatus = UserStatus.ACTIVE
    password_hash: Optional[str] = None

    created_at: datetime = Field(default_factory=get_current_datetime)
    updated_at: datetime = Field(default_factory=get_current_datetime)

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
        """Update user's personal information"""
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name

        self.updated_at = get_current_datetime()

    def change_status(self, new_status: UserStatus):
        """Change user status"""
        if self.user_status != new_status:
            self.user_status = new_status
            self.updated_at = get_current_datetime()
