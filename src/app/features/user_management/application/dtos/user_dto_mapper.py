from pydantic import BaseModel
from typing import Union

from src.app.features.user_management.application.dtos.user_dto import UserResponse
from src.app.features.user_management.domain.entities.user_entity import UserEntity
from src.app.features.user_management.domain.entities.user_enums import UserRole
from src.app.features.user_management.domain.value_objects.email import Email


def map_dto_to_entity_user(user_dto: BaseModel) -> UserEntity:
    """
    Convert a User DTO (Data Transfer Object) to a User Entity.
    """
    return UserEntity.create(
        first_name=user_dto.first_name,
        last_name=user_dto.last_name,
        email=Email(user_dto.email),
        user_role=UserRole(user_dto.user_role),
        password_hash=user_dto.password_hash,
    )


def map_entity_to_dto_user(user_entity: Union[BaseModel, UserEntity]) -> UserResponse:
    """
    Convert a User Entity to a User DTO (Data Transfer Object).
    """
    return UserResponse(
        id=str(user_entity.id.value),
        fullname=user_entity.fullname,
        email=user_entity.email.value,
        user_role=user_entity.user_role.value,
        user_status=user_entity.user_status.value,
        created_at=user_entity.created_at,
        updated_at=user_entity.updated_at,
    )
