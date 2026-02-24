"""Router layer for Parent endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.services.parent_service import ParentService
from app.schemas.parent import (
    ParentCreate,
    ParentResponse,
    ParentUpdate,
    ParentWithStudents,
)
from app.schemas.pagination import PaginatedResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/parents", tags=["Parents"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> ParentService:
    logger.trace("Creating ParentService dependency")
    return ParentService(db)


@router.post("/", response_model=ParentResponse, status_code=201)
def create_parent(
    parent: ParentCreate,
    service: ParentService = Depends(get_service),
):
    """Create a new parent."""
    logger.info("POST /api/v1/parents — create parent request")
    result, error = service.create(parent)
    if error:
        logger.warning("POST /api/v1/parents — 400: %s", error)
        raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=PaginatedResponse[ParentResponse])
def list_parents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    search: str | None = Query(None, description="Search by parent first or last name"),
    service: ParentService = Depends(get_service),
):
    """List all parents with pagination."""
    logger.info(
        "GET /api/v1/parents — list parents request (page=%d, page_size=%d, search=%s)",
        page,
        page_size,
        search,
    )
    parents, total = service.get_all_paginated(page, page_size, search)
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    return PaginatedResponse(
        data=parents,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.get("/{parent_id}", response_model=ParentWithStudents)
def get_parent(parent_id: int, service: ParentService = Depends(get_service)):
    """Get a parent by ID with linked student IDs."""
    logger.info("GET /api/v1/parents/%s — get parent request", parent_id)
    result = service.get_by_id(parent_id)
    if not result:
        logger.warning("GET /api/v1/parents/%s — 404 not found", parent_id)
        raise HTTPException(status_code=404, detail="Parent not found")
    return result


@router.put("/{parent_id}", response_model=ParentResponse)
def update_parent(
    parent_id: int,
    parent: ParentUpdate,
    service: ParentService = Depends(get_service),
):
    """Update a parent."""
    logger.info("PUT /api/v1/parents/%s — update parent request", parent_id)
    result, error = service.update(parent_id, parent)
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/parents/%s — 404: %s", parent_id, error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("PUT /api/v1/parents/%s — 400: %s", parent_id, error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{parent_id}", status_code=204)
def delete_parent(parent_id: int, service: ParentService = Depends(get_service)):
    """Soft delete a parent."""
    logger.info("DELETE /api/v1/parents/%s — delete parent request", parent_id)
    success, error = service.delete(parent_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/parents/%s — 404 not found", parent_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/parents/%s — 409 conflict: %s", parent_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None
