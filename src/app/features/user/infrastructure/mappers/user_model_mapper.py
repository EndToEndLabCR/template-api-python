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
            display_name=model.display_name,
            role=UserRole(model.role),
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: UserEntity) -> UserModel:
        return UserModel(
            id=entity.id.value,
            email=entity.email.value,
            display_name=entity.display_name,
            role=entity.role.value,
            password_hash=entity.password_hash,
        )
