"""Router layer for School endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.database.connection import get_db
from app.logger import get_logger
from app.services.school_service import SchoolService
from app.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolUpdate,
    SchoolWithStats,
)
from app.auth.dependencies import (
    get_current_user,
    require_admin,
    require_admin_or_director,
    check_school_ownership,
)
from app.schemas.auth import UserRole

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/schools", tags=["Schools"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> SchoolService:
    logger.trace("Creating SchoolService dependency")
    return SchoolService(db)


@router.post("/", response_model=SchoolResponse, status_code=201)
def create_school(
    school: SchoolCreate,
    current_user: dict = Depends(require_admin),
    service: SchoolService = Depends(get_service),
):
    """Create a new school. Only ADMIN can create schools."""
    logger.info("POST /api/v1/schools — create school request by user_id=%s", current_user.get("sub"))
    result, warning = service.create(school)
    if warning:
        result.message = warning
    return result


@router.get("/", response_model=list[SchoolResponse])
def list_schools(
    search: str | None = Query(None, description="Search by school or director name"),
    current_user: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_service),
):
    """List schools. ADMIN sees all. Others see only their own school."""
    logger.info("GET /api/v1/schools — list schools request (search=%s)", search)
    if current_user.get("role") == UserRole.ADMIN.value:
        return service.get_all(search)
    # Non-admin users can only see their own school
    school_id = current_user.get("school_id")
    if school_id:
        result = service.get_by_id(school_id)
        return [result] if result else []
    return []


@router.get("/{school_id}", response_model=SchoolResponse)
def get_school(
    school_id: int, 
    include_stats: bool = Query(False, description="Include school statistics"),
    current_user: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_service),
):
    """Get a school by ID. Users can only view their own school."""
    logger.info("GET /api/v1/schools/%s — get school request (include_stats=%s)", school_id, include_stats)
    check_school_ownership(current_user, school_id)
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
def get_school_with_stats(
    school_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: SchoolService = Depends(get_service),
):
    """Get a school by ID with detailed statistics. ADMIN or DIRECTOR only."""
    logger.info("GET /api/v1/schools/%s/stats — get school stats request", school_id)
    check_school_ownership(current_user, school_id)
    result = service.get_by_id_with_stats(school_id)
    if not result:
        logger.warning("GET /api/v1/schools/%s/stats — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="School not found")
    return result


@router.put("/{school_id}", response_model=SchoolResponse)
def update_school(
    school_id: int,
    school: SchoolUpdate,
    current_user: dict = Depends(require_admin_or_director),
    service: SchoolService = Depends(get_service),
):
    """Update a school. ADMIN or DIRECTOR of that school."""
    logger.info("PUT /api/v1/schools/%s — update school request", school_id)
    check_school_ownership(current_user, school_id)
    result, warning = service.update(school_id, school)
    if not result:
        logger.warning("PUT /api/v1/schools/%s — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="School not found")
    if warning:
        result.message = warning
    return result


@router.delete("/{school_id}", status_code=204)
def delete_school(
    school_id: int,
    current_user: dict = Depends(require_admin),
    service: SchoolService = Depends(get_service),
):
    """Soft delete a school. Only ADMIN."""
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
def get_school_capacity_info(
    school_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: SchoolService = Depends(get_service),
):
    """Get school capacity information. ADMIN or DIRECTOR only."""
    logger.info("GET /api/v1/schools/%s/capacity — capacity info request", school_id)
    check_school_ownership(current_user, school_id)
    result = service.get_capacity_info(school_id)
    if not result:
        logger.warning("GET /api/v1/schools/%s/capacity — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="School not found")
    return result