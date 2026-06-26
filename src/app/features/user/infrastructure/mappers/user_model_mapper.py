"""Infrastructure mapper: UserModel ↔ UserEntity."""

from src.app.features.user.domain.entities.user_entity import UserEntity
from src.app.features.user.domain.value_objects.user_role import UserRole
from src.app.features.user.infrastructure.models.user_model import UserModel
from src.app.shared.domain.value_objects.email import Email
from src.app.shared.domain.value_objects.entity_id import EntityId


class UserModelMapper:
    """Maps between UserModel and UserEntity."""

    @staticmethod
    def to_entity(model: UserModel) -> UserEntity:
        return UserEntity(
            id=EntityId(model.id),
            email=Email(model.email),
            first_name=model.first_name,
            last_name=model.last_name,
            role=UserRole(model.role),
            password_hash=model.password_hash,
            password_reset_token_hash=model.password_reset_token_hash,
            password_reset_expires_at=model.password_reset_expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id.value,
            email=entity.email.value,
            first_name=entity.first_name,
            last_name=entity.last_name,
            role=entity.role.value,
            password_hash=entity.password_hash,
            password_reset_token_hash=entity.password_reset_token_hash,
            password_reset_expires_at=entity.password_reset_expires_at,
        )
