from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.student import StudentResponse
from app.schemas.teacher import TeacherResponse


class ClassCreate(BaseModel):
    class_name: str = Field(..., examples=["Sunflower Room"])
    capacity: Optional[int] = Field(None, examples=[20])
    teacher_ids: list[int] = Field(default=[], examples=[[1, 2]])


class ClassUpdate(BaseModel):
    class_name: Optional[str] = Field(None, examples=["Sunflower Room"])
    capacity: Optional[int] = Field(None, examples=[20])
    teacher_ids: Optional[list[int]] = Field(None, examples=[[1, 2]])


class ClassResponse(BaseModel):
    class_id: int
    class_name: str
    capacity: Optional[int] = None
    created_date: str
    students: list[StudentResponse] = []
    teachers: list[TeacherResponse] = []
