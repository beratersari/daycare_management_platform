"""Router layer for Student endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

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

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/students", tags=["Students"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> StudentService:
    logger.trace("Creating StudentService dependency")
    return StudentService(db)


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate,
    service: StudentService = Depends(get_service),
):
    """Create a new student with parents, allergies, and HW info."""
    logger.info("POST /api/v1/students — create student request")
    result, error = service.create(student)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/students — 404: %s", error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("POST /api/v1/students — 400: %s", error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[StudentResponse])
def list_students(service: StudentService = Depends(get_service)):
    """List all students."""
    logger.info("GET /api/v1/students — list students request")
    return service.get_all()


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, service: StudentService = Depends(get_service)):
    """Get a student by ID with full details."""
    logger.info("GET /api/v1/students/%s — get student request", student_id)
    result = service.get_by_id(student_id)
    if not result:
        logger.warning("GET /api/v1/students/%s — 404 not found", student_id)
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    service: StudentService = Depends(get_service),
):
    """Update a student."""
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
def delete_student(student_id: int, service: StudentService = Depends(get_service)):
    """Soft delete a student."""
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
    service: StudentService = Depends(get_service),
):
    """Enroll a student in a class."""
    logger.info("POST /api/v1/students/%s/classes/%s — enroll student in class", student_id, class_id)
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
    service: StudentService = Depends(get_service),
):
    """Unenroll a student from a class."""
    logger.info("DELETE /api/v1/students/%s/classes/%s — unenroll student from class", student_id, class_id)
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
    service: StudentService = Depends(get_service),
):
    """Add an allergy to a student."""
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
    service: StudentService = Depends(get_service),
):
    """Soft delete an allergy."""
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
    service: StudentService = Depends(get_service),
):
    """Add HW info to a student."""
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
    service: StudentService = Depends(get_service),
):
    """Soft delete an HW info record."""
    logger.info("DELETE /api/v1/students/%s/hw-info/%s — remove HW info request", student_id, hw_id)
    success, error = service.delete_hw_info(student_id, hw_id)
    if not success:
        logger.warning("DELETE /api/v1/students/%s/hw-info/%s — 404: %s", student_id, hw_id, error)
        raise HTTPException(status_code=404, detail=error)
    return None
