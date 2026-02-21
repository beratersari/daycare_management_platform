"""Router layer for Class endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
from app.services.class_service import ClassService
from app.schemas.class_dto import ClassCreate, ClassResponse, ClassUpdate

router = APIRouter(prefix="/api/v1/classes", tags=["Classes"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> ClassService:
    return ClassService(db)


@router.post("/", response_model=ClassResponse, status_code=201)
def create_class(
    cls: ClassCreate,
    service: ClassService = Depends(get_service),
):
    """Create a new class."""
    result, error = service.create(cls)
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[ClassResponse])
def list_classes(service: ClassService = Depends(get_service)):
    """List all classes."""
    return service.get_all()


@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, service: ClassService = Depends(get_service)):
    """Get a class by ID with students and teachers."""
    result = service.get_by_id(class_id)
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")
    return result


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    cls: ClassUpdate,
    service: ClassService = Depends(get_service),
):
    """Update a class."""
    result, error = service.update(class_id, cls)
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{class_id}", status_code=204)
def delete_class(class_id: int, service: ClassService = Depends(get_service)):
    """Soft delete a class."""
    success, error = service.delete(class_id)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.get("/{class_id}/capacity")
def get_class_capacity_info(class_id: int, service: ClassService = Depends(get_service)):
    """Get class capacity information."""
    result = service.get_capacity_info(class_id)
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")
    return result
