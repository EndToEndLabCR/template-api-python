from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel


class UserResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    id: str
    display_name: str
    email: str


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    display_name: str
    email: EmailStr
    password: str
