from pydantic import EmailStr

from src.app.features.user_management.application.dtos.user_dto import UserResponse
from src.shared.utils.date_util import get_current_datetime


class UserResponseBuilder:
    """
    Builder for creating a UserResponseDto object.
    """

    def __init__(self):
        self._user_response_dto = UserResponse(
            id="",
            fullname="",
            email="default@example.com",
            role="",
            user_status="",
            created_at=get_current_datetime(),
            updated_at=get_current_datetime(),
        )

    def with_id(self, user_id):
        self._user_response_dto.id = user_id
        return self

    def with_fullname(self, fullname: str):
        self._user_response_dto.fullname = fullname
        return self

    def with_email(self, email: EmailStr):
        self._user_response_dto.email = email
        return self

    def with_role(self, role):
        self._user_response_dto.role = role
        return self

    def with_user_status(self, user_status):
        self._user_response_dto.user_status = user_status
        return self

    def with_created_at(self, created_at):
        self._user_response_dto.created_at = created_at
        return self

    def with_updated_at(self, updated_at):
        self._user_response_dto.updated_at = updated_at
        return self

    def build(self) -> UserResponse:
        return self._user_response_dto
