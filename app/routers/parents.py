"""Router layer for Parent endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
from app.services.parent_service import ParentService
from app.schemas.parent import (
    ParentCreate,
    ParentResponse,
    ParentUpdate,
    ParentWithStudents,
)

router = APIRouter(prefix="/api/v1/parents", tags=["Parents"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> ParentService:
    return ParentService(db)


@router.post("/", response_model=ParentResponse, status_code=201)
def create_parent(
    parent: ParentCreate,
    service: ParentService = Depends(get_service),
):
    """Create a new parent."""
    result, error = service.create(parent)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[ParentResponse])
def list_parents(service: ParentService = Depends(get_service)):
    """List all parents."""
    return service.get_all()


@router.get("/{parent_id}", response_model=ParentWithStudents)
def get_parent(parent_id: int, service: ParentService = Depends(get_service)):
    """Get a parent by ID with linked student IDs."""
    result = service.get_by_id(parent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Parent not found")
    return result


@router.put("/{parent_id}", response_model=ParentResponse)
def update_parent(
    parent_id: int,
    parent: ParentUpdate,
    service: ParentService = Depends(get_service),
):
    """Update a parent."""
    result, error = service.update(parent_id, parent)
    if error:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{parent_id}", status_code=204)
def delete_parent(parent_id: int, service: ParentService = Depends(get_service)):
    """Soft delete a parent."""
    success, error = service.delete(parent_id)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=409, detail=error)
    return None
