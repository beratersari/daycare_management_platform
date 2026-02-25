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
    BulkAttendanceRequest,
    BulkAttendanceResponse,
    ClassEventCreate,
    ClassEventUpdate,
    ClassEventResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.schemas.student import StudentResponse
from app.auth.dependencies import (
    get_current_user,
    require_admin_or_director,
    require_admin_director_or_teacher,
    check_school_ownership,
)
from app.schemas.auth import UserRole

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/classes", tags=["Classes"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> ClassService:
    logger.trace("Creating ClassService dependency")
    return ClassService(db)


def _check_teacher_class_access(current_user: dict, class_id: int, service: ClassService) -> None:
    """Check that a TEACHER is assigned to the given class. ADMIN/DIRECTOR bypass."""
    if current_user.get("role") in (UserRole.ADMIN.value, UserRole.DIRECTOR.value):
        return
    if current_user.get("role") == UserRole.TEACHER.value:
        user_id = current_user.get("sub")
        class_ids = service.user_repo.get_teacher_class_ids(user_id)
        if class_id not in class_ids:
            raise HTTPException(
                status_code=403,
                detail="You can only manage classes you are assigned to",
            )


def _check_parent_class_access(current_user: dict, class_id: int, service: ClassService) -> None:
    """Check that a PARENT has a child enrolled in the given class."""
    if current_user.get("role") != UserRole.PARENT.value:
        return
    user_id = current_user.get("sub")
    student_ids = service.user_repo.get_student_ids_for_parent(user_id)
    for sid in student_ids:
        class_ids = service.student_repo.get_class_ids(sid)
        if class_id in class_ids:
            return
    raise HTTPException(
        status_code=403,
        detail="You can only view classes your children are enrolled in",
    )


@router.post("/", response_model=ClassResponse, status_code=201)
def create_class(
    cls: ClassCreate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """Create a new class. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("POST /api/v1/classes — create class request")
    check_school_ownership(current_user, cls.school_id)
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
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """List all classes with pagination. ADMIN, DIRECTOR, or TEACHER."""
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
def get_class(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    service: ClassService = Depends(get_service),
):
    """Get a class by ID. PARENT can only view classes their children are in."""
    logger.info("GET /api/v1/classes/%s — get class request", class_id)
    # Parents can only see classes their children are enrolled in
    if current_user.get("role") == UserRole.PARENT.value:
        _check_parent_class_access(current_user, class_id, service)
    result = service.get_by_id(class_id)
    if not result:
        logger.warning("GET /api/v1/classes/%s — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    if current_user.get("role") != UserRole.PARENT.value:
        check_school_ownership(current_user, result.school_id)
    return result


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    cls: ClassUpdate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """Update a class. TEACHER can only edit classes they are assigned to."""
    logger.info("PUT /api/v1/classes/%s — update class request", class_id)
    _check_teacher_class_access(current_user, class_id, service)
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
def delete_class(
    class_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: ClassService = Depends(get_service),
):
    """Soft delete a class. ADMIN or DIRECTOR only."""
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
def get_class_capacity_info(
    class_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """Get class capacity information. ADMIN, DIRECTOR, or TEACHER."""
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
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """
    Get students in class who don't have attendance recorded for the given date.
    ADMIN, DIRECTOR, or TEACHER.
    """
    logger.info(
        "GET /api/v1/classes/%s/attendance/pending — get students without attendance for date=%s",
        class_id,
        attendance_date,
    )
    
    if not service.exists(class_id):
        logger.warning("GET /api/v1/classes/%s/attendance/pending — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    
    _check_teacher_class_access(current_user, class_id, service)
    
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
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """
    Record attendance for a student on a specific date.
    ADMIN, DIRECTOR, or TEACHER (must be assigned to the class).
    The recording user is automatically captured from the authenticated session.
    """
    recorded_by = current_user.get("sub")
    logger.info(
        "POST /api/v1/classes/%s/attendance — record attendance for student_id=%s on date=%s by user_id=%s",
        class_id,
        attendance_record.student_id,
        attendance_date,
        recorded_by,
    )
    
    _check_teacher_class_access(current_user, class_id, service)
    
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


@router.put("/{class_id}/attendance/bulk", response_model=BulkAttendanceResponse)
def bulk_set_attendance(
    class_id: int,
    bulk_request: BulkAttendanceRequest,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """
    Set attendance for a list of students at once (bulk edit).
    Creates or updates attendance records for each student in the list.
    ADMIN, DIRECTOR, or TEACHER (must be assigned to the class).
    The recording user is automatically captured from the authenticated session.
    """
    recorded_by = current_user.get("sub")
    logger.info(
        "PUT /api/v1/classes/%s/attendance/bulk — bulk set attendance for %d students on date=%s by user_id=%s",
        class_id,
        len(bulk_request.records),
        bulk_request.attendance_date,
        recorded_by,
    )

    _check_teacher_class_access(current_user, class_id, service)

    entries = [entry.model_dump() for entry in bulk_request.records]
    results, error = service.bulk_record_attendance(
        class_id=class_id,
        attendance_date=bulk_request.attendance_date,
        entries=entries,
        recorded_by=recorded_by,
    )

    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/classes/%s/attendance/bulk — 404: %s", class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("PUT /api/v1/classes/%s/attendance/bulk — 400: %s", class_id, error)
        raise HTTPException(status_code=400, detail=error)

    # Build response records with student names
    response_records = []
    for record in results:
        student = service.student_repo.get_by_id(record["student_id"])
        student_name = f"{student['first_name']} {student['last_name']}" if student else None
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

    logger.info(
        "PUT /api/v1/classes/%s/attendance/bulk — %d records set successfully",
        class_id, len(response_records),
    )
    return BulkAttendanceResponse(
        class_id=class_id,
        attendance_date=bulk_request.attendance_date,
        total_recorded=len(response_records),
        records=response_records,
    )


@router.get("/{class_id}/attendance", response_model=list[AttendanceRecordResponse])
def get_attendance_for_date(
    class_id: int,
    attendance_date: str = Query(..., description="Date in YYYY-MM-DD format"),
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """Get all attendance records for a class on a specific date. ADMIN, DIRECTOR, or TEACHER."""
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
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """Get attendance history for a class with optional date range. ADMIN, DIRECTOR, or TEACHER."""
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


# --- Event endpoints ---


@router.post("/{class_id}/events", response_model=ClassEventResponse, status_code=201)
def create_class_event(
    class_id: int,
    event_data: ClassEventCreate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """
    Create a new event for a class.
    ADMIN, DIRECTOR, or TEACHER (must be assigned to the class).
    """
    created_by = current_user.get("sub")
    logger.info(
        "POST /api/v1/classes/%s/events — create event by user_id=%s",
        class_id,
        created_by,
    )
    
    _check_teacher_class_access(current_user, class_id, service)
    
    result, error = service.create_event(
        class_id=class_id,
        data=event_data,
        created_by=created_by,
    )
    
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/classes/%s/events — 404: %s", class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/classes/%s/events — 400: %s", class_id, error)
        raise HTTPException(status_code=400, detail=error)
    
    logger.info("POST /api/v1/classes/%s/events — event created: event_id=%s", class_id, result.event_id)
    return result


@router.get("/{class_id}/events", response_model=list[ClassEventResponse])
def get_class_events(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    service: ClassService = Depends(get_service),
):
    """
    Get all events for a class.
    All authenticated users can view events for classes they have access to.
    PARENT can only view events for classes their children are enrolled in.
    """
    logger.info("GET /api/v1/classes/%s/events — get events request", class_id)
    
    # Parents can only see events for classes their children are enrolled in
    if current_user.get("role") == UserRole.PARENT.value:
        _check_parent_class_access(current_user, class_id, service)
    
    events, error = service.get_events_by_class_id(class_id)
    
    if error:
        if "not found" in error.lower():
            logger.warning("GET /api/v1/classes/%s/events — 404: %s", class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("GET /api/v1/classes/%s/events — 400: %s", class_id, error)
        raise HTTPException(status_code=400, detail=error)
    
    logger.info("GET /api/v1/classes/%s/events — returning %d events", class_id, len(events))
    return events


@router.get("/{class_id}/events/{event_id}", response_model=ClassEventResponse)
def get_class_event_by_id(
    class_id: int,
    event_id: int,
    current_user: dict = Depends(get_current_user),
    service: ClassService = Depends(get_service),
):
    """
    Get a specific event by ID.
    All authenticated users can view events for classes they have access to.
    PARENT can only view events for classes their children are enrolled in.
    """
    logger.info("GET /api/v1/classes/%s/events/%s — get event request", class_id, event_id)
    
    # Parents can only see events for classes their children are enrolled in
    if current_user.get("role") == UserRole.PARENT.value:
        _check_parent_class_access(current_user, class_id, service)
    
    result, error = service.get_event_by_id(class_id, event_id)
    
    if error:
        if "not found" in error.lower():
            logger.warning("GET /api/v1/classes/%s/events/%s — 404: %s", class_id, event_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("GET /api/v1/classes/%s/events/%s — 400: %s", class_id, event_id, error)
        raise HTTPException(status_code=400, detail=error)
    
    logger.info("GET /api/v1/classes/%s/events/%s — event found", class_id, event_id)
    return result


@router.put("/{class_id}/events/{event_id}", response_model=ClassEventResponse)
def update_class_event(
    class_id: int,
    event_id: int,
    event_data: ClassEventUpdate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """
    Update a class event.
    ADMIN, DIRECTOR, or TEACHER (must be assigned to the class).
    """
    updated_by = current_user.get("sub")
    logger.info(
        "PUT /api/v1/classes/%s/events/%s — update event by user_id=%s",
        class_id,
        event_id,
        updated_by,
    )
    
    _check_teacher_class_access(current_user, class_id, service)
    
    result, error = service.update_event(
        class_id=class_id,
        event_id=event_id,
        data=event_data,
        updated_by=updated_by,
    )
    
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/classes/%s/events/%s — 404: %s", class_id, event_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("PUT /api/v1/classes/%s/events/%s — 400: %s", class_id, event_id, error)
        raise HTTPException(status_code=400, detail=error)
    
    logger.info("PUT /api/v1/classes/%s/events/%s — event updated", class_id, event_id)
    return result


@router.delete("/{class_id}/events/{event_id}", status_code=204)
def delete_class_event(
    class_id: int,
    event_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: ClassService = Depends(get_service),
):
    """
    Delete (soft delete) a class event.
    ADMIN, DIRECTOR, or TEACHER (must be assigned to the class).
    """
    deleted_by = current_user.get("sub")
    logger.info(
        "DELETE /api/v1/classes/%s/events/%s — delete event by user_id=%s",
        class_id,
        event_id,
        deleted_by,
    )
    
    _check_teacher_class_access(current_user, class_id, service)
    
    success, error = service.delete_event(
        class_id=class_id,
        event_id=event_id,
        deleted_by=deleted_by,
    )
    
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/classes/%s/events/%s — 404: %s", class_id, event_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/classes/%s/events/%s — 400: %s", class_id, event_id, error)
        raise HTTPException(status_code=400, detail=error)
    
    logger.info("DELETE /api/v1/classes/%s/events/%s — event deleted", class_id, event_id)
    return None
