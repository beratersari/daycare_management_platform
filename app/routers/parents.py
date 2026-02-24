"""Router layer for Parent endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserResponse, UserRole
from app.schemas.pagination import PaginatedResponse
from app.auth.dependencies import (
    get_current_user,
    require_admin_or_director,
    check_school_ownership,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/parents", tags=["Parents"])


def get_user_repo(db: sqlite3.Connection = Depends(get_db)) -> UserRepository:
    logger.trace("Creating UserRepository dependency")
    return UserRepository(db)


@router.get("/", response_model=PaginatedResponse[UserResponse])
def list_parents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    search: str | None = Query(None, description="Search by parent first or last name"),
    current_user: dict = Depends(require_admin_or_director),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """List all parents with pagination. ADMIN or DIRECTOR only."""
    logger.info(
        "GET /api/v1/parents — list parents request (page=%d, page_size=%d, search=%s)",
        page,
        page_size,
        search,
    )
    parents = user_repo.get_users_by_role(UserRole.PARENT.value, current_user.get("school_id"))
    if search:
        term = search.lower()
        parents = [p for p in parents if term in p.get("first_name", "").lower() or term in p.get("last_name", "").lower()]
    total = len(parents)
    start = (page - 1) * page_size
    end = start + page_size
    parents = parents[start:end]
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    return PaginatedResponse(
        data=[UserResponse(**p) for p in parents],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.get("/{parent_id}", response_model=UserResponse)
def get_parent(
    parent_id: int,
    current_user: dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """Get a parent by user ID. PARENT can only view themselves."""
    logger.info("GET /api/v1/parents/%s — get parent request", parent_id)
    parent = user_repo.get_by_id(parent_id)
    if not parent or parent.get("role") != UserRole.PARENT.value:
        logger.warning("GET /api/v1/parents/%s — 404 not found", parent_id)
        raise HTTPException(status_code=404, detail="Parent not found")
    if current_user.get("role") == UserRole.PARENT.value and current_user.get("sub") != parent_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")
    check_school_ownership(current_user, parent.get("school_id"))
    return UserResponse(**parent)
