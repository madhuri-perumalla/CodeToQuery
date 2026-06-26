"""User schemas for request/response validation."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    full_name: str | None = Field(None, max_length=255, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100, description="Password")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = Field(None, description="User email address")
    username: str | None = Field(None, min_length=3, max_length=100, description="Username")
    full_name: str | None = Field(None, max_length=255, description="Full name")
    password: str | None = Field(None, min_length=8, max_length=100, description="Password")


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Schema for token payload."""

    sub: str | None = None
    username: str | None = None
    exp: int | None = None
