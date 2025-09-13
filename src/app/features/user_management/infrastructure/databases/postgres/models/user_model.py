from sqlalchemy import Column, String, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.app.features.user_management.domain.entities.user_enums import UserRole, UserStatus
from src.shared.domain.models.base_model import BaseModel
from src.shared.utils.date_util import get_current_datetime


class UserModel(BaseModel):
    """
    SQLAlchemy model for the User table.
    Maps the UserEntity to a PostgreSQL database table.
    """
    __tablename__ = "users"

    # Override the inherited id column
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    user_status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    password_hash = Column(Text, nullable=True)

    def update_user_model_data(self, first_name: str, last_name: str):
        """Update user's data"""
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name

        self.updated_at = get_current_datetime()

    def __repr__(self):
        return (
            f"<UserModel(id={self.id}, email={self.email}, role={self.user_role}, status={self.user_status})>"
        )
