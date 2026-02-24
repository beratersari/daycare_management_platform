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


class AttendanceRecord(BaseModel):
    """Schema for recording attendance for a student."""
    student_id: int = Field(..., description="ID of the student")
    status: str = Field(default="present", description="Attendance status: present, absent, late, or excused")
    notes: Optional[str] = Field(None, description="Optional notes about the attendance")


class AttendanceRecordResponse(BaseModel):
    """Schema for attendance record response."""
    attendance_id: int
    class_id: int
    student_id: int
    student_name: Optional[str] = Field(None, description="Full name of the student")
    attendance_date: str
    status: str
    recorded_by: Optional[int] = None
    recorded_at: str
    notes: Optional[str] = None


class AttendanceDateRequest(BaseModel):
    """Schema for requesting attendance data for a specific date."""
    attendance_date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2024-01-15"])


class AttendanceHistoryRequest(BaseModel):
    """Schema for requesting attendance history with date range."""
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format", examples=["2024-01-01"])
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format", examples=["2024-01-31"])
