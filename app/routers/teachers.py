"""Router layer for Teacher endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
from app.services.teacher_service import TeacherService
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.schemas.class_dto import ClassResponse

router = APIRouter(prefix="/api/v1/teachers", tags=["Teachers"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> TeacherService:
    return TeacherService(db)


@router.post("/", response_model=TeacherResponse, status_code=201)
def create_teacher(
    teacher: TeacherCreate,
    service: TeacherService = Depends(get_service),
):
    """Create a new teacher."""
    result, error = service.create(teacher)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[TeacherResponse])
def list_teachers(service: TeacherService = Depends(get_service)):
    """List all teachers."""
    return service.get_all()


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, service: TeacherService = Depends(get_service)):
    """Get a teacher by ID."""
    result = service.get_by_id(teacher_id)
    if not result:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return result


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    service: TeacherService = Depends(get_service),
):
    """Update a teacher."""
    result, error = service.update(teacher_id, teacher)
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(teacher_id: int, service: TeacherService = Depends(get_service)):
    """Soft delete a teacher."""
    success, error = service.delete(teacher_id)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.get("/{teacher_id}/classes", response_model=list[ClassResponse])
def get_teacher_classes(
    teacher_id: int,
    service: TeacherService = Depends(get_service),
):
    """
    Get the class assigned to a teacher, including full student and teacher details.
    Returns a list with one class if assigned, or an empty list if not assigned.
    """
    result = service.get_classes(teacher_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return result
