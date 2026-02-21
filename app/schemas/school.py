import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Regex patterns for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-\(\)]{7,20}$")


class SchoolCreate(BaseModel):
    school_name: str = Field(..., examples=["Sunshine Daycare Center"])
    address: str = Field(..., examples=["123 Daycare Lane, City, State 12345"])
    phone: Optional[str] = Field(None, examples=["555-123-4567"])
    email: Optional[str] = Field(None, examples=["info@sunshinedaycare.com"])
    director_name: Optional[str] = Field(None, examples=["Dr. Sarah Johnson"])
    license_number: Optional[str] = Field(None, examples=["DC-2024-001"])
    capacity: Optional[int] = Field(None, examples=[100], description="Total capacity of the school")

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


class SchoolUpdate(BaseModel):
    school_name: Optional[str] = Field(None, examples=["Sunshine Daycare Center"])
    address: Optional[str] = Field(None, examples=["123 Daycare Lane, City, State 12345"])
    phone: Optional[str] = Field(None, examples=["555-123-4567"])
    email: Optional[str] = Field(None, examples=["info@sunshinedaycare.com"])
    director_name: Optional[str] = Field(None, examples=["Dr. Sarah Johnson"])
    license_number: Optional[str] = Field(None, examples=["DC-2024-001"])
    capacity: Optional[int] = Field(None, examples=[100], description="Total capacity of the school")

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


class SchoolResponse(BaseModel):
    school_id: int
    school_name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    director_name: Optional[str] = None
    license_number: Optional[str] = None
    capacity: Optional[int] = None
    created_date: str


class SchoolWithStats(SchoolResponse):
    total_students: int = 0
    total_teachers: int = 0
    total_classes: int = 0
    total_parents: int = 0