import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional

# Date format: YYYY-MM-DD
DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date_format(v: Optional[str], field_name: str) -> Optional[str]:
    """Validate date format is YYYY-MM-DD."""
    if v is not None:
        if not DATE_REGEX.match(v):
            raise ValueError(f"Invalid date format for {field_name}. Expected format: YYYY-MM-DD (e.g., 2024-01-15)")
        # Additional validation for valid date values
        try:
            year, month, day = map(int, v.split("-"))
            if month < 1 or month > 12:
                raise ValueError(f"Invalid month in {field_name}. Month must be between 01 and 12")
            if day < 1 or day > 31:
                raise ValueError(f"Invalid day in {field_name}. Day must be between 01 and 31")
        except ValueError as e:
            if "Invalid" in str(e):
                raise
            raise ValueError(f"Invalid date format for {field_name}. Expected format: YYYY-MM-DD (e.g., 2024-01-15)")
    return v


class AllergyCreate(BaseModel):
    allergy_name: str = Field(..., examples=["Peanuts"])
    severity: Optional[str] = Field(None, examples=["High"])
    notes: Optional[str] = Field(None, examples=["Carries EpiPen"])


class AllergyResponse(BaseModel):
    allergy_id: int
    student_id: int
    allergy_name: str
    severity: Optional[str] = None
    notes: Optional[str] = None
    created_date: str


class HWInfoCreate(BaseModel):
    height: float = Field(..., examples=[95.5], description="Height in centimeters")
    weight: float = Field(..., examples=[14.2], description="Weight in kilograms")
    measurement_date: str = Field(..., examples=["2024-01-15"], description="Date in YYYY-MM-DD format")

    @field_validator("measurement_date")
    @classmethod
    def validate_measurement_date(cls, v: str) -> str:
        result = validate_date_format(v, "measurement_date")
        if result is None:
            raise ValueError("measurement_date is required")
        return result


class HWInfoResponse(BaseModel):
    hw_id: int
    student_id: int
    height: float
    weight: float
    measurement_date: str
    created_date: str


class StudentCreate(BaseModel):
    first_name: str = Field(..., examples=["Charlie"])
    last_name: str = Field(..., examples=["Smith"])
    school_id: int = Field(..., examples=[1], description="ID of the school this student belongs to")
    class_id: Optional[int] = Field(None, examples=[1])
    student_photo: Optional[str] = Field(None, examples=["https://photos.example.com/charlie.jpg"])
    date_of_birth: Optional[str] = Field(None, examples=["2021-03-15"], description="Date in YYYY-MM-DD format")
    parent_ids: list[int] = Field(default=[], examples=[[1, 2]])
    allergies: list[AllergyCreate] = []
    hw_info: list[HWInfoCreate] = []

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[str]) -> Optional[str]:
        return validate_date_format(v, "date_of_birth")


class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, examples=["Charlie"])
    last_name: Optional[str] = Field(None, examples=["Smith"])
    school_id: Optional[int] = Field(None, examples=[1], description="ID of the school this student belongs to")
    class_id: Optional[int] = Field(None, examples=[1])
    student_photo: Optional[str] = Field(None, examples=["https://photos.example.com/charlie.jpg"])
    date_of_birth: Optional[str] = Field(None, examples=["2021-03-15"], description="Date in YYYY-MM-DD format")
    parent_ids: Optional[list[int]] = Field(None, examples=[[1, 2]])
    allergies: Optional[list[AllergyCreate]] = None
    hw_info: Optional[list[HWInfoCreate]] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: Optional[str]) -> Optional[str]:
        return validate_date_format(v, "date_of_birth")


class StudentResponse(BaseModel):
    student_id: int
    first_name: str
    last_name: str
    school_id: int
    class_id: Optional[int] = None
    student_photo: Optional[str] = None
    date_of_birth: Optional[str] = None
    created_date: str
    parents: list[int] = []
    student_allergies: list[AllergyResponse] = []
    student_hw_info: list[HWInfoResponse] = []
