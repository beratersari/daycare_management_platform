from pydantic import BaseModel, Field
from typing import Optional

from app.schemas.student import StudentResponse
from app.schemas.auth import UserResponse


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
    teachers: list[UserResponse] = []


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


class BulkAttendanceEntry(BaseModel):
    """A single student attendance entry within a bulk request."""
    student_id: int = Field(..., description="ID of the student")
    status: str = Field(default="present", description="Attendance status: present, absent, late, or excused")
    notes: Optional[str] = Field(None, description="Optional notes about the attendance")


class BulkAttendanceRequest(BaseModel):
    """Schema for setting attendance for multiple students at once (bulk edit)."""
    attendance_date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2024-01-15"])
    records: list[BulkAttendanceEntry] = Field(
        ..., min_length=1, description="List of student attendance entries"
    )


class BulkAttendanceResponse(BaseModel):
    """Schema for the response after bulk attendance recording."""
    class_id: int
    attendance_date: str
    total_recorded: int = Field(description="Number of attendance records successfully set")
    records: list[AttendanceRecordResponse] = Field(description="List of attendance records that were set")


class ClassEventCreate(BaseModel):
    """Schema for creating a new class event."""
    title: str = Field(..., min_length=1, max_length=200, examples=["Field Trip to Zoo"])
    description: Optional[str] = Field(None, max_length=2000, examples=["We will visit the zoo on Friday. Please bring lunch."])
    photo_url: Optional[str] = Field(None, examples=["https://example.com/event-photo.jpg"])
    event_date: str = Field(..., description="Event date and time in ISO format (YYYY-MM-DDTHH:MM:SS)", examples=["2024-02-25T14:30:00"])


class ClassEventUpdate(BaseModel):
    """Schema for updating a class event."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, examples=["Field Trip to Zoo - Updated"])
    description: Optional[str] = Field(None, max_length=2000, examples=["Updated description."])
    photo_url: Optional[str] = Field(None, examples=["https://example.com/new-photo.jpg"])
    event_date: Optional[str] = Field(None, description="Event date and time in ISO format (YYYY-MM-DDTHH:MM:SS)", examples=["2024-02-25T14:30:00"])


class ClassEventResponse(BaseModel):
    """Schema for class event response."""
    event_id: int
    class_id: int
    title: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    event_date: str
    created_by: int
    created_at: str
    updated_at: str
