"""Router layer for School endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.services.school_service import SchoolService
from app.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolUpdate,
    SchoolWithStats,
)

router = APIRouter(prefix="/api/v1/schools", tags=["Schools"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


@router.post("/", response_model=SchoolResponse, status_code=201)
def create_school(
    school: SchoolCreate,
    service: SchoolService = Depends(get_service),
):
    """Create a new school."""
    return service.create(school)


@router.get("/", response_model=list[SchoolResponse])
def list_schools(service: SchoolService = Depends(get_service)):
    """List all schools."""
    return service.get_all()


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(
    school_id: int, 
    include_stats: bool = Query(False, description="Include school statistics"),
    service: SchoolService = Depends(get_service)
):
    """Get a school by ID, optionally with statistics."""
    if include_stats:
        result = service.get_by_id_with_stats(school_id)
        if not result:
            raise HTTPException(status_code=404, detail="School not found")
        return result
    else:
        result = service.get_by_id(school_id)
        if not result:
            raise HTTPException(status_code=404, detail="School not found")
        return result


@router.get("/{school_id}/stats", response_model=SchoolWithStats)
def get_school_with_stats(school_id: int, service: SchoolService = Depends(get_service)):
    """Get a school by ID with detailed statistics."""
    result = service.get_by_id_with_stats(school_id)
    if not result:
        raise HTTPException(status_code=404, detail="School not found")
    return result


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: int,
    school: SchoolUpdate,
    service: SchoolService = Depends(get_service),
):
    """Update a school."""
    result = service.update(school_id, school)
    if not result:
        raise HTTPException(status_code=404, detail="School not found")
    return result


@router.delete("/{school_id}", status_code=204)
def delete_school(school_id: int, service: SchoolService = Depends(get_service)):
    """Soft delete a school."""
    success, error = service.delete(school_id)
    if not success:
        if "not found" in error.lower():
            raise HTTPException(status_code=404, detail=error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.get("/{school_id}/capacity")
def get_school_capacity_info(school_id: int, service: SchoolService = Depends(get_service)):
    """Get school capacity information."""
    result = service.get_capacity_info(school_id)
    if not result:
        raise HTTPException(status_code=404, detail="School not found")
    return result