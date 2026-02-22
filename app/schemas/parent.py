import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from app.logger import get_logger

logger = get_logger(__name__)

# Regex patterns for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,20}$")


class ParentCreate(BaseModel):
    first_name: str = Field(..., examples=["Alice"])
    last_name: str = Field(..., examples=["Smith"])
    school_id: int = Field(..., examples=[1], description="ID of the school this parent belongs to")
    email: Optional[str] = Field(None, examples=["alice@example.com"])
    phone: Optional[str] = Field(None, examples=["555-123-4567"])
    address: Optional[str] = Field(None, examples=["123 Main St, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating parent email: %s", v)
        if v is not None and not EMAIL_REGEX.match(v):
            logger.warning("Invalid parent email format: %s", v)
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating parent phone: %s", v)
        if v is not None and not PHONE_REGEX.match(v):
            logger.warning("Invalid parent phone format: %s", v)
            raise ValueError("Invalid phone format. Expected format: 555-123-4567 or +1 555 123 4567")
        return v


class ParentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, examples=["Alice"])
    last_name: Optional[str] = Field(None, examples=["Smith"])
    school_id: Optional[int] = Field(None, examples=[1], description="ID of the school this parent belongs to")
    email: Optional[str] = Field(None, examples=["alice@example.com"])
    phone: Optional[str] = Field(None, examples=["555-123-4567"])
    address: Optional[str] = Field(None, examples=["123 Main St, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating parent update email: %s", v)
        if v is not None and not EMAIL_REGEX.match(v):
            logger.warning("Invalid parent update email format: %s", v)
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating parent update phone: %s", v)
        if v is not None and not PHONE_REGEX.match(v):
            logger.warning("Invalid parent update phone format: %s", v)
            raise ValueError("Invalid phone format. Expected format: 555-123-4567 or +1 555 123 4567")
        return v


class ParentResponse(BaseModel):
    parent_id: int
    first_name: str
    last_name: str
    school_id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_date: str


class ParentWithStudents(ParentResponse):
    student_ids: list[int] = []
