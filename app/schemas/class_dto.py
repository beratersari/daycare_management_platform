from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.student import StudentResponse
from app.schemas.teacher import TeacherResponse


class ClassCreate(BaseModel):
    class_name: str = Field(..., examples=["Sunflower Room"])
    school_id: int = Field(..., examples=[1], description="ID of the school this class belongs to")
    capacity: Optional[int] = Field(None, examples=[20])


class ClassUpdate(BaseModel):
    class_name: Optional[str] = Field(None, examples=["Sunflower Room"])
    school_id: Optional[int] = Field(None, examples=[1], description="ID of the school this class belongs to")
    capacity: Optional[int] = Field(None, examples=[20])


class ClassResponse(BaseModel):
    class_id: int
    class_name: str
    school_id: int
    capacity: Optional[int] = None
    created_date: str
    students: list[StudentResponse] = []
    teachers: list[TeacherResponse] = []
