"""Router layer for Student endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
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

router = APIRouter(prefix="/api/v1/students", tags=["Students"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> StudentService:
    return StudentService(db)


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
    student: StudentCreate,
    service: StudentService = Depends(get_service),
):
    """Create a new student with parents, allergies, and HW info."""
    result, error = service.create(student)
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[StudentResponse])
def list_students(service: StudentService = Depends(get_service)):
    """List all students."""
    return service.get_all()


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, service: StudentService = Depends(get_service)):
    """Get a student by ID with full details."""
    result = service.get_by_id(student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    service: StudentService = Depends(get_service),
):
    """Update a student."""
    result, error = service.update(student_id, student)
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, service: StudentService = Depends(get_service)):
    """Soft delete a student."""
    success, error = service.delete(student_id)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
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
    result, error = service.add_allergy(student_id, allergy)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return result


@router.delete("/{student_id}/allergies/{allergy_id}", status_code=204)
def remove_allergy(
    student_id: int,
    allergy_id: int,
    service: StudentService = Depends(get_service),
):
    """Soft delete an allergy."""
    success, error = service.delete_allergy(student_id, allergy_id)
    if not success:
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
    result, error = service.add_hw_info(student_id, hw_info)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return result


@router.delete("/{student_id}/hw-info/{hw_id}", status_code=204)
def remove_hw_info(
    student_id: int,
    hw_id: int,
    service: StudentService = Depends(get_service),
):
    """Soft delete an HW info record."""
    success, error = service.delete_hw_info(student_id, hw_id)
    if not success:
        raise HTTPException(status_code=404, detail=error)
    return None
