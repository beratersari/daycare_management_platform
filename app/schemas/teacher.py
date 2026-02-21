import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Regex patterns for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,20}$")


class TeacherCreate(BaseModel):
    first_name: str = Field(..., examples=["Jane"])
    last_name: str = Field(..., examples=["Johnson"])
    email: Optional[str] = Field(None, examples=["jane.johnson@school.com"])
    phone: Optional[str] = Field(None, examples=["555-987-6543"])
    address: Optional[str] = Field(None, examples=["456 School Ave, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone format. Expected format: 555-123-4567 or +1 555 123 4567")
        return v


class TeacherUpdate(BaseModel):
    first_name: Optional[str] = Field(None, examples=["Jane"])
    last_name: Optional[str] = Field(None, examples=["Johnson"])
    email: Optional[str] = Field(None, examples=["jane.johnson@school.com"])
    phone: Optional[str] = Field(None, examples=["555-987-6543"])
    address: Optional[str] = Field(None, examples=["456 School Ave, City"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format. Expected format: user@example.com")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone format. Expected format: 555-123-4567 or +1 555 123 4567")
        return v


class TeacherResponse(BaseModel):
    teacher_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_date: str
