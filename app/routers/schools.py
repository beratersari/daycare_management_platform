"""Router layer for School endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.services.school_service import SchoolService
from app.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolUpdate,
    SchoolWithStats,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/schools", tags=["Schools"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> SchoolService:
    logger.trace("Creating SchoolService dependency")
    return SchoolService(db)


@router.post("/", response_model=SchoolResponse, status_code=201)
def create_school(
    school: SchoolCreate,
    service: SchoolService = Depends(get_service),
):
    """Create a new school."""
    logger.info("POST /api/v1/schools — create school request")
    return service.create(school)


@router.get("/", response_model=list[SchoolResponse])
def list_schools(service: SchoolService = Depends(get_service)):
    """List all schools."""
    logger.info("GET /api/v1/schools — list schools request")
    return service.get_all()


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(
    school_id: int, 
    include_stats: bool = Query(False, description="Include school statistics"),
    service: SchoolService = Depends(get_service)
):
    """Get a school by ID, optionally with statistics."""
    logger.info("GET /api/v1/schools/%s — get school request (include_stats=%s)", school_id, include_stats)
    if include_stats:
        result = service.get_by_id_with_stats(school_id)
        if not result:
            logger.warning("GET /api/v1/schools/%s — 404 not found", school_id)
            raise HTTPException(status_code=404, detail="School not found")
        return result
    else:
        result = service.get_by_id(school_id)
        if not result:
            logger.warning("GET /api/v1/schools/%s — 404 not found", school_id)
            raise HTTPException(status_code=404, detail="School not found")
        return result


@router.get("/{school_id}/stats", response_model=SchoolWithStats)
def get_school_with_stats(school_id: int, service: SchoolService = Depends(get_service)):
    """Get a school by ID with detailed statistics."""
    logger.info("GET /api/v1/schools/%s/stats — get school stats request", school_id)
    result = service.get_by_id_with_stats(school_id)
    if not result:
        logger.warning("GET /api/v1/schools/%s/stats — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="School not found")
    return result


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: int,
    school: SchoolUpdate,
    service: SchoolService = Depends(get_service),
):
    """Update a school."""
    logger.info("PUT /api/v1/schools/%s — update school request", school_id)
    result = service.update(school_id, school)
    if not result:
        logger.warning("PUT /api/v1/schools/%s — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="School not found")
    return result


@router.delete("/{school_id}", status_code=204)
def delete_school(school_id: int, service: SchoolService = Depends(get_service)):
    """Soft delete a school."""
    logger.info("DELETE /api/v1/schools/%s — delete school request", school_id)
    success, error = service.delete(school_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/schools/%s — 404 not found", school_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/schools/%s — 409 conflict: %s", school_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.get("/{school_id}/capacity")
def get_school_capacity_info(school_id: int, service: SchoolService = Depends(get_service)):
    """Get school capacity information."""
    logger.info("GET /api/v1/schools/%s/capacity — capacity info request", school_id)
    result = service.get_capacity_info(school_id)
    if not result:
        logger.warning("GET /api/v1/schools/%s/capacity — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="School not found")
    return result