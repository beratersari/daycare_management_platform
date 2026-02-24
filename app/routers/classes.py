"""Router layer for Class endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.database.connection import get_db
from app.logger import get_logger
from app.services.class_service import ClassService
from app.schemas.class_dto import (
    ClassCreate, 
    ClassResponse, 
    ClassUpdate,
    AttendanceRecord,
    AttendanceRecordResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.schemas.student import StudentResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/classes", tags=["Classes"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> ClassService:
    logger.trace("Creating ClassService dependency")
    return ClassService(db)


@router.post("/", response_model=ClassResponse, status_code=201)
def create_class(
    cls: ClassCreate,
    service: ClassService = Depends(get_service),
):
    """Create a new class."""
    logger.info("POST /api/v1/classes — create class request")
    result, error = service.create(cls)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/classes — 404: %s", error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("POST /api/v1/classes — 400: %s", error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=PaginatedResponse[ClassResponse])
def list_classes(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    search: str | None = Query(None, description="Search by class name"),
    service: ClassService = Depends(get_service),
):
    """List all classes with pagination."""
    logger.info(
        "GET /api/v1/classes — list classes request (page=%d, page_size=%d, search=%s)",
        page,
        page_size,
        search,
    )
    classes, total = service.get_all_paginated(page, page_size, search)
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    return PaginatedResponse(
        data=classes,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, service: ClassService = Depends(get_service)):
    """Get a class by ID with students and teachers."""
    logger.info("GET /api/v1/classes/%s — get class request", class_id)
    result = service.get_by_id(class_id)
    if not result:
        logger.warning("GET /api/v1/classes/%s — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    return result


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    cls: ClassUpdate,
    service: ClassService = Depends(get_service),
):
    """Update a class."""
    logger.info("PUT /api/v1/classes/%s — update class request", class_id)
    result, error = service.update(class_id, cls)
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/classes/%s — 404: %s", class_id, error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("PUT /api/v1/classes/%s — 400: %s", class_id, error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{class_id}", status_code=204)
def delete_class(class_id: int, service: ClassService = Depends(get_service)):
    """Soft delete a class."""
    logger.info("DELETE /api/v1/classes/%s — delete class request", class_id)
    success, error = service.delete(class_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/classes/%s — 404 not found", class_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/classes/%s — 409 conflict: %s", class_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.get("/{class_id}/capacity")
def get_class_capacity_info(class_id: int, service: ClassService = Depends(get_service)):
    """Get class capacity information."""
    logger.info("GET /api/v1/classes/%s/capacity — capacity info request", class_id)
    result = service.get_capacity_info(class_id)
    if not result:
        logger.warning("GET /api/v1/classes/%s/capacity — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    return result


# --- Attendance endpoints ---


@router.get("/{class_id}/attendance/pending", response_model=list[StudentResponse])
def get_students_without_attendance(
    class_id: int,
    attendance_date: str = Query(..., description="Date in YYYY-MM-DD format"),
    service: ClassService = Depends(get_service),
):
    """
    Get students in class who don't have attendance recorded for the given date.
    These are the students whose attendance still needs to be recorded.
    """
    logger.info(
        "GET /api/v1/classes/%s/attendance/pending — get students without attendance for date=%s",
        class_id,
        attendance_date,
    )
    
    # Verify class exists
    if not service.exists(class_id):
        logger.warning("GET /api/v1/classes/%s/attendance/pending — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    
    students = service.get_students_without_attendance(class_id, attendance_date)
    logger.info(
        "GET /api/v1/classes/%s/attendance/pending — returning %d students without attendance",
        class_id,
        len(students),
    )
    return students


@router.post("/{class_id}/attendance", response_model=AttendanceRecordResponse)
def record_attendance(
    class_id: int,
    attendance_record: AttendanceRecord,
    attendance_date: str = Query(..., description="Date in YYYY-MM-DD format"),
    recorded_by: Optional[int] = Query(None, description="ID of the teacher recording attendance"),
    service: ClassService = Depends(get_service),
):
    """
    Record attendance for a student on a specific date.
    Status can be: present, absent, late, or excused.
    """
    logger.info(
        "POST /api/v1/classes/%s/attendance — record attendance for student_id=%s on date=%s",
        class_id,
        attendance_record.student_id,
        attendance_date,
    )
    
    result, error = service.record_attendance(
        class_id=class_id,
        student_id=attendance_record.student_id,
        attendance_date=attendance_date,
        status=attendance_record.status,
        recorded_by=recorded_by,
        notes=attendance_record.notes,
    )
    
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/classes/%s/attendance — 404: %s", class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/classes/%s/attendance — 400: %s", class_id, error)
        raise HTTPException(status_code=400, detail=error)
    
    # Build response with student name
    student = service.student_repo.get_by_id(attendance_record.student_id)
    student_name = f"{student['first_name']} {student['last_name']}" if student else None
    
    logger.info("POST /api/v1/classes/%s/attendance — attendance recorded successfully", class_id)
    return AttendanceRecordResponse(
        attendance_id=result["attendance_id"],
        class_id=result["class_id"],
        student_id=result["student_id"],
        student_name=student_name,
        attendance_date=result["attendance_date"],
        status=result["status"],
        recorded_by=result["recorded_by"],
        recorded_at=result["recorded_at"],
        notes=result["notes"],
    )


@router.get("/{class_id}/attendance", response_model=list[AttendanceRecordResponse])
def get_attendance_for_date(
    class_id: int,
    attendance_date: str = Query(..., description="Date in YYYY-MM-DD format"),
    service: ClassService = Depends(get_service),
):
    """Get all attendance records for a class on a specific date."""
    logger.info(
        "GET /api/v1/classes/%s/attendance — get attendance for date=%s",
        class_id,
        attendance_date,
    )
    
    if not service.exists(class_id):
        logger.warning("GET /api/v1/classes/%s/attendance — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    
    records = service.get_attendance_for_date(class_id, attendance_date)
    
    # Convert to response model with student_name
    response_records = []
    for record in records:
        student_name = f"{record['first_name']} {record['last_name']}"
        response_records.append(
            AttendanceRecordResponse(
                attendance_id=record["attendance_id"],
                class_id=record["class_id"],
                student_id=record["student_id"],
                student_name=student_name,
                attendance_date=record["attendance_date"],
                status=record["status"],
                recorded_by=record["recorded_by"],
                recorded_at=record["recorded_at"],
                notes=record["notes"],
            )
        )
    
    logger.info("GET /api/v1/classes/%s/attendance — returning %d records", class_id, len(response_records))
    return response_records


@router.get("/{class_id}/attendance/history", response_model=list[AttendanceRecordResponse])
def get_attendance_history(
    class_id: int,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    service: ClassService = Depends(get_service),
):
    """Get attendance history for a class with optional date range."""
    logger.info(
        "GET /api/v1/classes/%s/attendance/history — get history from %s to %s",
        class_id,
        start_date,
        end_date,
    )
    
    if not service.exists(class_id):
        logger.warning("GET /api/v1/classes/%s/attendance/history — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    
    records = service.get_attendance_history(class_id, start_date, end_date)
    
    # Convert to response model with student_name
    response_records = []
    for record in records:
        student_name = f"{record['first_name']} {record['last_name']}"
        response_records.append(
            AttendanceRecordResponse(
                attendance_id=record["attendance_id"],
                class_id=record["class_id"],
                student_id=record["student_id"],
                student_name=student_name,
                attendance_date=record["attendance_date"],
                status=record["status"],
                recorded_by=record["recorded_by"],
                recorded_at=record["recorded_at"],
                notes=record["notes"],
            )
        )
    
    logger.info("GET /api/v1/classes/%s/attendance/history — returning %d records", class_id, len(response_records))
    return response_records
