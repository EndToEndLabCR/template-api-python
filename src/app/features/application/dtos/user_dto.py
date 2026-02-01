from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UserResponse(BaseModel):
    """
    Data Transfer Object for user response.
    
    This DTO is used to transfer user data from the API to clients.
    Field names are automatically converted to camelCase for JSON responses.
    
    Attributes:
        id (str): The user's unique identifier.
        fullname (str): The user's full name.
        email (str): The user's email address.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

    id: str
    fullname: str
    email: str
