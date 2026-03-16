"""
User and authentication models.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: str = "user"


class UserInDB(BaseModel):
    """User as stored in database (includes hashed password)."""

    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    role: str = "user"
    disabled: bool = False


class UserResponse(BaseModel):
    """User data returned in API responses (no password)."""

    id: Optional[str] = None
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    disabled: bool = False


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload extracted from JWT."""

    username: Optional[str] = None
    role: Optional[str] = None
    scopes: List[str] = []
