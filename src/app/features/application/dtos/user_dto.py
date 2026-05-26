from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel


class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class ForgotPasswordResponse(BaseModel):
    message: str
    token: str


class ResetPasswordResponse(BaseModel):
    message: str


class LoginResponse(BaseModel):
    name: str


class UserResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

    id: str
    fullname: str
    email: str
    country_code: Optional[str] = None


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    first_name: str
    last_name: str
    email: EmailStr
    password: str
    country_code: Optional[str] = None
