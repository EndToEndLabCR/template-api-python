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
        first_name=entity.first_name,
        last_name=entity.last_name,
        display_name=entity.display_name,
        email=str(entity.email),
        role=entity.role.value,
    )


def to_user_entity(request: UserCreateRequest, password_hash: str) -> UserEntity:
    """Map a CreateUserRequest DTO to a UserEntity using the factory method."""
    return UserEntity.create(
        email=str(request.email).lower().strip(),
        first_name=request.first_name.strip(),
        last_name=request.last_name.strip(),
        password_hash=password_hash,
        role=request.role,
    )
