from datetime import datetime

from src.app.features.user.domain.value_objects.user_role import UserRole
from src.app.shared.domain.entities.base_entity import BaseEntity
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId


class UserEntity(BaseEntity):
    def __init__(
        self,
        id: EntityId,
        email: Email,
        first_name: str,
        last_name: str,
        password_hash: str,
        role: UserRole = UserRole.VIEWER,
        is_active: bool = True,
        password_reset_token_hash: str | None = None,
        password_reset_expires_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self._email = email
        self._first_name = first_name
        self._last_name = last_name
        self._password_hash = password_hash
        self._role = role
        self._is_active = is_active
        self._password_reset_token_hash = password_reset_token_hash
        self._password_reset_expires_at = password_reset_expires_at
        super().__init__(id, created_at, updated_at)

    # ── Read-only properties ──────────────────────────────────────
    @property
    def email(self) -> Email:
        return self._email

    @property
    def first_name(self) -> str:
        return self._first_name

    @property
    def last_name(self) -> str:
        return self._last_name

    @property
    def display_name(self) -> str:
        """Computed — not persisted."""
        return f"{self._first_name} {self._last_name}"

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def password_reset_token_hash(self) -> str | None:
        return self._password_reset_token_hash

    @property
    def password_reset_expires_at(self) -> datetime | None:
        return self._password_reset_expires_at

    @classmethod
    def create(
        cls,
        email: str,
        first_name: str,
        last_name: str,
        password_hash: str,
        role: UserRole | None = None,
    ) -> "UserEntity":
        return cls(
            id=EntityId.generate(),
            email=Email(email),
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            role=role or UserRole.default(),
        )

    def update_details(
        self,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        password_hash: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> None:
        if email is not None:
            self._email = Email(email)
        if first_name is not None:
            self._first_name = first_name
        if last_name is not None:
            self._last_name = last_name
        if password_hash is not None:
            self._password_hash = password_hash
        if role is not None:
            self._role = role
        if is_active is not None:
            self._is_active = is_active
        self.mark_as_updated()

    def is_admin(self) -> bool:
        return self._role == UserRole.ADMIN

    # ── Password reset token helpers ──────────────────────────────
    def set_password_reset_token(self, token_hash: str, expires_at: datetime) -> None:
        """Set a password reset token hash and its expiry on the entity."""
        self._password_reset_token_hash = token_hash
        self._password_reset_expires_at = expires_at
        self.mark_as_updated()

    def clear_password_reset_token(self) -> None:
        """Invalidate the current password reset token (single-use)."""
        self._password_reset_token_hash = None
        self._password_reset_expires_at = None
        self.mark_as_updated()
