from pydantic import BaseModel
from typing import Union

from src.app.features.user_management.application.dtos.user_dto import UserResponse
from src.app.features.user_management.application.dtos.user_dto_builder import UserResponseBuilder
from src.app.features.user_management.domain.entities.user_entity_builder import UserEntityBuilder
from src.app.features.user_management.domain.entities.user_entity import UserEntity


def map_dto_to_entity_user(user_dto: BaseModel) -> UserEntity:
    """
    Convert a User DTO (Data Transfer Object) to a User Entity using the Builder Pattern.
    """
    return (
        UserEntityBuilder()
        .with_first_name(user_dto.first_name)
        .with_last_name(user_dto.last_name)
        .with_email(user_dto.email)
        .with_role(user_dto.role)
        .with_password_hash(user_dto.password_hash)
        .build()
    )


def map_entity_to_dto_user(user_entity: Union[BaseModel, UserEntity]) -> UserResponse:
    """
    Convert a User Entity to a User DTO (Data Transfer Object) using the Builder Pattern.
    """
    return (
        UserResponseBuilder()
        .with_id(str(user_entity.id.value))
        .with_fullname(user_entity.fullname)
        .with_email(user_entity.email.value)
        .with_role(user_entity.role)
        .with_user_status(user_entity.user_status)
        .with_created_at(user_entity.created_at)
        .with_updated_at(user_entity.updated_at)
        .build()
    )
