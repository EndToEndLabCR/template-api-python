"""
Application mapper: auth entities/DTOs → response DTOs.
"""

from datetime import UTC, datetime

from src.app.features.auth.application.dtos.auth_dto import (
    AdminLoginResponse,
    UserDetail,
)


def to_login_response(
    user_entity,
    token: str,
    refresh_token: str,
) -> AdminLoginResponse:
    """Build an AdminLoginResponse from a UserEntity and tokens."""
    display_name = user_entity.display_name
    logged_in_at = datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")

    return AdminLoginResponse(
        token=token,
        access_token=token,
        refresh_token=refresh_token,
        email=str(user_entity.email),
        display_name=display_name,
        logged_in_at=logged_in_at,
        role=str(user_entity.role.value),
        user=UserDetail(
            email=str(user_entity.email),
            display_name=display_name,
            name=display_name,
            role=str(user_entity.role.value),
        ),
    )
