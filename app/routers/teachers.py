"""Router layer for Teacher endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.repositories.user_repository import UserRepository
from app.repositories.class_repository import ClassRepository
from app.services.class_service import ClassService
from app.schemas.auth import UserResponse, UserRole
from app.schemas.class_dto import ClassResponse
from app.schemas.pagination import PaginatedResponse
from app.auth.dependencies import (
    require_admin_or_director,
    require_admin_director_or_teacher,
    check_school_ownership,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/teachers", tags=["Teachers"])


def get_user_repo(db: sqlite3.Connection = Depends(get_db)) -> UserRepository:
    logger.trace("Creating UserRepository dependency")
    return UserRepository(db)


def get_class_repo(db: sqlite3.Connection = Depends(get_db)) -> ClassRepository:
    logger.trace("Creating ClassRepository dependency")
    return ClassRepository(db)


def get_class_service(db: sqlite3.Connection = Depends(get_db)) -> ClassService:
    logger.trace("Creating ClassService dependency")
    return ClassService(db)


@router.get("/", response_model=PaginatedResponse[UserResponse])
def list_teachers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (1-100)"),
    search: str | None = Query(None, description="Search by teacher first or last name"),
    current_user: dict = Depends(require_admin_director_or_teacher),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """List all teachers with pagination. ADMIN, DIRECTOR, or TEACHER."""
    logger.info(
        "GET /api/v1/teachers — list teachers request (page=%d, page_size=%d, search=%s)",
        page,
        page_size,
        search,
    )
    teachers = user_repo.get_users_by_role(UserRole.TEACHER.value, current_user.get("school_id"))
    if search:
        term = search.lower()
        teachers = [t for t in teachers if term in t.get("first_name", "").lower() or term in t.get("last_name", "").lower()]
    total = len(teachers)
    start = (page - 1) * page_size
    end = start + page_size
    teachers = teachers[start:end]
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_previous = page > 1
    return PaginatedResponse(
        data=[UserResponse(**t) for t in teachers],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


@router.get("/{teacher_id}", response_model=UserResponse)
def get_teacher(
    teacher_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    user_repo: UserRepository = Depends(get_user_repo),
):
    """Get a teacher by user ID. ADMIN, DIRECTOR, or TEACHER."""
    logger.info("GET /api/v1/teachers/%s — get teacher request", teacher_id)
    teacher = user_repo.get_by_id(teacher_id)
    if not teacher or teacher.get("role") != UserRole.TEACHER.value:
        logger.warning("GET /api/v1/teachers/%s — 404 not found", teacher_id)
        raise HTTPException(status_code=404, detail="Teacher not found")
    if current_user.get("role") == UserRole.TEACHER.value and current_user.get("sub") != teacher_id:
        raise HTTPException(status_code=403, detail="You can only view your own profile")
    check_school_ownership(current_user, teacher.get("school_id"))
    return UserResponse(**teacher)


@router.get("/{teacher_id}/classes", response_model=list[ClassResponse])
def get_teacher_classes(
    teacher_id: int,
    current_user: dict = Depends(require_admin_director_or_teacher),
    user_repo: UserRepository = Depends(get_user_repo),
    class_service: ClassService = Depends(get_class_service),
):
    """Get classes assigned to a teacher (by user ID)."""
    logger.info("GET /api/v1/teachers/%s/classes — get teacher classes request", teacher_id)
    teacher = user_repo.get_by_id(teacher_id)
    if not teacher or teacher.get("role") != UserRole.TEACHER.value:
        logger.warning("GET /api/v1/teachers/%s/classes — 404 not found", teacher_id)
        raise HTTPException(status_code=404, detail="Teacher not found")
    if current_user.get("role") == UserRole.TEACHER.value and current_user.get("sub") != teacher_id:
        raise HTTPException(status_code=403, detail="You can only view your own classes")
    check_school_ownership(current_user, teacher.get("school_id"))
    class_ids = user_repo.get_teacher_class_ids(teacher_id)
    classes = []
    for cid in class_ids:
        class_data = class_service.get_by_id(cid)
        if class_data is not None:
            classes.append(class_data)
    return classes


@router.post("/{teacher_id}/classes/{class_id}", status_code=204)
def assign_teacher_to_class(
    teacher_id: int,
    class_id: int,
    current_user: dict = Depends(require_admin_or_director),
    user_repo: UserRepository = Depends(get_user_repo),
    class_repo: ClassRepository = Depends(get_class_repo),
):
    """Assign a teacher (user) to a class."""
    logger.info("POST /api/v1/teachers/%s/classes/%s — assign teacher", teacher_id, class_id)
    teacher = user_repo.get_by_id(teacher_id)
    if not teacher or teacher.get("role") != UserRole.TEACHER.value:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if not class_repo.exists(class_id):
        raise HTTPException(status_code=404, detail="Class not found")
    check_school_ownership(current_user, teacher.get("school_id"))
    user_repo.assign_teacher_to_class(teacher_id, class_id)
    return None


@router.delete("/{teacher_id}/classes/{class_id}", status_code=204)
def unassign_teacher_from_class(
    teacher_id: int,
    class_id: int,
    current_user: dict = Depends(require_admin_or_director),
    user_repo: UserRepository = Depends(get_user_repo),
    class_repo: ClassRepository = Depends(get_class_repo),
):
    """Unassign a teacher (user) from a class."""
    logger.info("DELETE /api/v1/teachers/%s/classes/%s — unassign teacher", teacher_id, class_id)
    teacher = user_repo.get_by_id(teacher_id)
    if not teacher or teacher.get("role") != UserRole.TEACHER.value:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if not class_repo.exists(class_id):
        raise HTTPException(status_code=404, detail="Class not found")
    check_school_ownership(current_user, teacher.get("school_id"))
    user_repo.unassign_teacher_from_class(teacher_id, class_id)
    return None
