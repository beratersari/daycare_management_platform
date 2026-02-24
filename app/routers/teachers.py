"""Router layer for Teacher endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.services.teacher_service import TeacherService
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.schemas.class_dto import ClassResponse
from app.schemas.pagination import PaginatedResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/teachers", tags=["Teachers"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> TeacherService:
    logger.trace("Creating TeacherService dependency")
    return TeacherService(db)


@router.post("/", response_model=TeacherResponse, status_code=201)
def create_teacher(
    teacher: TeacherCreate,
    service: TeacherService = Depends(get_service),
):
    """Create a new teacher."""
    logger.info("POST /api/v1/teachers — create teacher request")
    result, error = service.create(teacher)
    if error:
        logger.warning("POST /api/v1/teachers — 400: %s", error)
        raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=PaginatedResponse[TeacherResponse])
def list_teachers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    search: str | None = Query(None, description="Search by teacher first or last name"),
    service: TeacherService = Depends(get_service),
):
    """List all teachers with pagination."""
    logger.info(
        "GET /api/v1/teachers — list teachers request (page=%d, page_size=%d, search=%s)",
        page,
        page_size,
        search,
    )
    teachers, total = service.get_all_paginated(page, page_size, search)
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    return PaginatedResponse(
        data=teachers,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, service: TeacherService = Depends(get_service)):
    """Get a teacher by ID."""
    logger.info("GET /api/v1/teachers/%s — get teacher request", teacher_id)
    result = service.get_by_id(teacher_id)
    if not result:
        logger.warning("GET /api/v1/teachers/%s — 404 not found", teacher_id)
        raise HTTPException(status_code=404, detail="Teacher not found")
    return result


@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    service: TeacherService = Depends(get_service),
):
    """Update a teacher."""
    logger.info("PUT /api/v1/teachers/%s — update teacher request", teacher_id)
    result, error = service.update(teacher_id, teacher)
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/teachers/%s — 404: %s", teacher_id, error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("PUT /api/v1/teachers/%s — 400: %s", teacher_id, error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{teacher_id}", status_code=204)
def delete_teacher(teacher_id: int, service: TeacherService = Depends(get_service)):
    """Soft delete a teacher."""
    logger.info("DELETE /api/v1/teachers/%s — delete teacher request", teacher_id)
    success, error = service.delete(teacher_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/teachers/%s — 404 not found", teacher_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/teachers/%s — 409 conflict: %s", teacher_id, error)
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
    logger.info("GET /api/v1/teachers/%s/classes — get teacher classes request", teacher_id)
    result = service.get_classes(teacher_id)
    if result is None:
        logger.warning("GET /api/v1/teachers/%s/classes — 404 not found", teacher_id)
        raise HTTPException(status_code=404, detail="Teacher not found")
    return result
