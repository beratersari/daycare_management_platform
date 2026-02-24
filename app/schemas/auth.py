"""DTO schemas for authentication and authorization."""
import re
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from app.logger import get_logger

logger = get_logger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class UserRole(str, Enum):
    """User roles for role-based access control."""
    ADMIN = "ADMIN"
    DIRECTOR = "DIRECTOR"
    TEACHER = "TEACHER"
    PARENT = "PARENT"


class UserRegister(BaseModel):
    """Schema for user registration."""
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=6, examples=["securepass123"])
    first_name: str = Field(..., examples=["Alice"])
    last_name: str = Field(..., examples=["Smith"])
    role: UserRole = Field(default=UserRole.PARENT, examples=["PARENT"])
    school_id: Optional[int] = Field(None, examples=[1], description="Required for DIRECTOR, TEACHER, PARENT roles")
    phone: Optional[str] = Field(None, examples=["555-123-4567"])
    address: Optional[str] = Field(None, examples=["123 Main St, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        logger.trace("Validating registration email: %s", v)
        if not EMAIL_REGEX.match(v):
            logger.warning("Invalid registration email format: %s", v)
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v.lower()


class UserLogin(BaseModel):
    """Schema for user login."""
    email: str = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["securepass123"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower()


class TokenResponse(BaseModel):
    """Schema for token response (login / refresh)."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="The refresh token to exchange for a new pair")


class UserResponse(BaseModel):
    """Schema for user response (public info)."""
    user_id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    school_id: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_date: str


class TokenPayload(BaseModel):
    """Internal schema representing decoded JWT payload."""
    sub: int  # user_id
    role: UserRole
    school_id: Optional[int] = None
    exp: int
