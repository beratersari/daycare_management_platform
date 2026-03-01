"""Router layer for Student endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.services.student_service import StudentService
from app.schemas.student import (
    AllergyCreate,
    AllergyResponse,
    HWInfoCreate,
    HWInfoResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.auth.dependencies import (
    get_current_user,
    require_admin_or_director,
    require_admin_director_or_teacher,
    check_school_ownership,
)
from app.schemas.auth import UserRole

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/students", tags=["Students"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> StudentService:
    logger.trace("Creating StudentService dependency")
    return StudentService(db)


def _check_parent_student_access(current_user: dict, student_id: int, db: sqlite3.Connection) -> None:
    """Check that a PARENT can only access their own children."""
    if current_user.get("role") != UserRole.PARENT.value:
        return
    user_id = current_user.get("sub")
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(db)
    student_ids = user_repo.get_student_ids_for_parent(user_id)
    if student_id not in student_ids:
        raise HTTPException(
            status_code=403,
            detail="You can only view information about your own children",
        )


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Create a new student. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("POST /api/v1/students — create student request")
    check_school_ownership(current_user, student.school_id)
    result, error = service.create(student)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/students — 404: %s", error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("POST /api/v1/students — 400: %s", error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=PaginatedResponse[StudentResponse])
def list_students(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    search: str | None = Query(None, description="Search by student first or last name"),
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """List all students with pagination. ADMIN, DIRECTOR, or TEACHER."""
    logger.info(
        "GET /api/v1/students — list students request (page=%d, page_size=%d, search=%s)",
        page,
        page_size,
        search,
    )
    students, total = service.get_all_paginated(page, page_size, search)
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    return PaginatedResponse(
        data=students,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    service: StudentService = Depends(get_service),
):
    """Get a student by ID. PARENT can only view their own children."""
    logger.info("GET /api/v1/students/%s — get student request", student_id)
    _check_parent_student_access(current_user, student_id, service.db)
    result = service.get_by_id(student_id)
    if not result:
        logger.warning("GET /api/v1/students/%s — 404 not found", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Update a student. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("PUT /api/v1/students/%s — update student request", student_id)
    result, error = service.update(student_id, student)
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/students/%s — 404: %s", student_id, error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("PUT /api/v1/students/%s — 400: %s", student_id, error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{student_id}", status_code=204)
def delete_student(
    student_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: StudentService = Depends(get_service),
):
    """Soft delete a student. ADMIN or DIRECTOR only."""
    logger.info("DELETE /api/v1/students/%s — delete student request", student_id)
    success, error = service.delete(student_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/students/%s — 404 not found", student_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/students/%s — 409 conflict: %s", student_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None


# --- Class enrollment endpoints ---


@router.post("/{student_id}/classes/{class_id}", response_model=StudentResponse)
def enroll_in_class(
    student_id: int,
    class_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Enroll a student in a class. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("POST /api/v1/students/%s/classes/%s — enroll student in class", student_id, class_id)
    student = service.get_by_id(student_id)
    if not student:
        logger.warning("POST /api/v1/students/%s/classes/%s — 404 student not found", student_id, class_id)
        raise HTTPException(status_code=404, detail="Student not found")
    check_school_ownership(current_user, student.school_id)
    class_data = service.class_repo.get_by_id(class_id)
    if not class_data:
        logger.warning("POST /api/v1/students/%s/classes/%s — 404 class not found", student_id, class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    if class_data.get("school_id") != student.school_id:
        raise HTTPException(status_code=403, detail="Student and class must belong to the same school")
    result, error = service.enroll_in_class(student_id, class_id)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/students/%s/classes/%s — 404: %s", student_id, class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/students/%s/classes/%s — 409: %s", student_id, class_id, error)
        raise HTTPException(status_code=409, detail=error)
    return result


@router.delete("/{student_id}/classes/{class_id}", status_code=204)
def unenroll_from_class(
    student_id: int,
    class_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Unenroll a student from a class. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("DELETE /api/v1/students/%s/classes/%s — unenroll student from class", student_id, class_id)
    student = service.get_by_id(student_id)
    if not student:
        logger.warning("DELETE /api/v1/students/%s/classes/%s — 404 student not found", student_id, class_id)
        raise HTTPException(status_code=404, detail="Student not found")
    check_school_ownership(current_user, student.school_id)
    class_data = service.class_repo.get_by_id(class_id)
    if not class_data:
        logger.warning("DELETE /api/v1/students/%s/classes/%s — 404 class not found", student_id, class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    if class_data.get("school_id") != student.school_id:
        raise HTTPException(status_code=403, detail="Student and class must belong to the same school")
    success, error = service.unenroll_from_class(student_id, class_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/students/%s/classes/%s — 404: %s", student_id, class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/students/%s/classes/%s — 409: %s", student_id, class_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None


# --- Allergy sub-resource endpoints ---


@router.post(
    "/{student_id}/allergies", response_model=AllergyResponse, status_code=201
)
def add_allergy(
    student_id: int,
    allergy: AllergyCreate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Add an allergy to a student. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("POST /api/v1/students/%s/allergies — add allergy request", student_id)
    result, error = service.add_allergy(student_id, allergy)
    if error:
        logger.warning("POST /api/v1/students/%s/allergies — 404: %s", student_id, error)
        raise HTTPException(status_code=404, detail=error)
    return result


@router.delete("/{student_id}/allergies/{allergy_id}", status_code=204)
def remove_allergy(
    student_id: int,
    allergy_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Soft delete an allergy. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("DELETE /api/v1/students/%s/allergies/%s — remove allergy request", student_id, allergy_id)
    success, error = service.delete_allergy(student_id, allergy_id)
    if not success:
        logger.warning("DELETE /api/v1/students/%s/allergies/%s — 404: %s", student_id, allergy_id, error)
        raise HTTPException(status_code=404, detail=error)
    return None


# --- HW Info sub-resource endpoints ---


@router.post(
    "/{student_id}/hw-info", response_model=HWInfoResponse, status_code=201
)
def add_hw_info(
    student_id: int,
    hw_info: HWInfoCreate,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Add HW info to a student. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("POST /api/v1/students/%s/hw-info — add HW info request", student_id)
    result, error = service.add_hw_info(student_id, hw_info)
    if error:
        logger.warning("POST /api/v1/students/%s/hw-info — 404: %s", student_id, error)
        raise HTTPException(status_code=404, detail=error)
    return result


@router.delete("/{student_id}/hw-info/{hw_id}", status_code=204)
def remove_hw_info(
    student_id: int,
    hw_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    service: StudentService = Depends(get_service),
):
    """Soft delete an HW info record. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("DELETE /api/v1/students/%s/hw-info/%s — remove HW info request", student_id, hw_id)
    success, error = service.delete_hw_info(student_id, hw_id)
    if not success:
        logger.warning("DELETE /api/v1/students/%s/hw-info/%s — 404: %s", student_id, hw_id, error)
        raise HTTPException(status_code=404, detail=error)
    return None
