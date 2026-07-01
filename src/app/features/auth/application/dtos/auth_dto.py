from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel


class LoginRequest(BaseModel):
    """Request model for user login."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    access_token: str
    refresh_token: str
    expires_in: int


class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request model for reset password."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    token: str
    password: str


class ForgotPasswordResponse(BaseModel):
    """Response model for forgot password."""

    message: str


class ResetPasswordResponse(BaseModel):
    """Response model for reset password."""

    message: str


class ChangePasswordRequest(BaseModel):
    """Request model for changing password (authenticated user)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    """Response model for change password."""

    message: str


class LogoutResponse(BaseModel):
    """Response model for logout."""

    message: str


class UserDetail(BaseModel):
    """Nested user details in login response."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    email: str
    display_name: str
    name: str
    role: str


class AdminLoginResponse(BaseModel):
    """
    Response model for login / register.
    Matches frontend AdminLoginApiResponse interface.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    access_token: str
    refresh_token: str
    expires_in: int
    email: str
    display_name: str
    logged_in_at: str
    role: str
    user: UserDetail
