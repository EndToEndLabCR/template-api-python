from datetime import datetime
import re

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional



class CreateUserRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: str
    password_hash: Optional[str] = None

    class Config:
        from_attributes = True  # Allows compatibility with ORM models such as SQLAlchemy


class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=8, max_length=20)

    class Config:
        from_attributes = True  # Allows compatibility with ORM models such as SQLAlchemy


class UserResponse(BaseModel):
    id: str
    fullname: str
    email: EmailStr
    role: str
    user_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows compatibility with ORM models such as SQLAlchemy
