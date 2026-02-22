import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from app.logger import get_logger

logger = get_logger(__name__)

# Regex patterns for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,20}$")


class TeacherCreate(BaseModel):
    first_name: str = Field(..., examples=["Jane"])
    last_name: str = Field(..., examples=["Johnson"])
    school_id: int = Field(..., examples=[1], description="ID of the school this teacher belongs to")
    class_id: Optional[int] = Field(None, examples=[1], description="ID of the class this teacher is assigned to")
    email: Optional[str] = Field(None, examples=["jane.johnson@school.com"])
    phone: Optional[str] = Field(None, examples=["555-987-6543"])
    address: Optional[str] = Field(None, examples=["456 School Ave, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating teacher email: %s", v)
        if v is not None and not EMAIL_REGEX.match(v):
            logger.warning("Invalid teacher email format: %s", v)
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating teacher phone: %s", v)
        if v is not None and not PHONE_REGEX.match(v):
            logger.warning("Invalid teacher phone format: %s", v)
            raise ValueError("Invalid phone format. Expected format: 555-123-4567 or +1 555 123 4567")
        return v


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = Field(None, examples=["Jane"])
    last_name: Optional[str] = Field(None, examples=["Johnson"])
    school_id: Optional[int] = Field(None, examples=[1], description="ID of the school this teacher belongs to")
    class_id: Optional[int] = Field(None, examples=[1], description="ID of the class this teacher is assigned to")
    email: Optional[str] = Field(None, examples=["jane.johnson@school.com"])
    phone: Optional[str] = Field(None, examples=["555-987-6543"])
    address: Optional[str] = Field(None, examples=["456 School Ave, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating teacher update email: %s", v)
        if v is not None and not EMAIL_REGEX.match(v):
            logger.warning("Invalid teacher update email format: %s", v)
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        logger.trace("Validating teacher update phone: %s", v)
        if v is not None and not PHONE_REGEX.match(v):
            logger.warning("Invalid teacher update phone format: %s", v)
            raise ValueError("Invalid phone format. Expected format: 555-123-4567 or +1 555 123 4567")
        return v


class TeacherResponse(BaseModel):
    teacher_id: int
    first_name: str
    last_name: str
    school_id: int
    class_id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_date: str
