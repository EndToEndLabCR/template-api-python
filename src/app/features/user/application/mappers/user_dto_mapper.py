"""Application mappers: UserEntity ↔ DTO."""

from src.app.features.user.application.dtos.user_dto import (
    UserCreateRequest,
    UserResponse,
)
from src.app.features.user.domain.entities.user_entity import UserEntity


def to_user_response(entity: UserEntity) -> UserResponse:
    """Map a UserEntity to a UserResponse DTO."""
    return UserResponse(
        id=str(entity.id),
        display_name=entity.display_name,
        email=str(entity.email),
    )


def to_user_entity(request: UserCreateRequest, password_hash: str) -> UserEntity:
    """Map a CreateUserRequest DTO to a UserEntity using the factory method."""
    return UserEntity.create(
        email=str(request.email).lower().strip(),
        display_name=request.display_name.strip(),
        password_hash=password_hash,
    )
