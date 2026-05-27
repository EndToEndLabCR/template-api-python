from src.app.features.domain.entities.user_entity import UserEntity
from src.app.features.domain.value_objects.email import Email
from src.app.features.infrastructure.models.user_model import UserModel
from src.shared.domain.value_objects.entity_id import EntityId


def map_model_to_entity(user_model: UserModel):
    """Maps a user model to a user entity."""

    return UserEntity(
        id=EntityId(user_model.id),
        email=Email(user_model.email),
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        password_hash=user_model.password_hash,
        password_reset_token_hash=user_model.password_reset_token_hash,
        password_reset_expires_at=user_model.password_reset_expires_at,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )
