"""Router layer for Term endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from app.database.connection import get_db
from app.logger import get_logger
from app.services.term_service import TermService
from app.schemas.term import TermCreate, TermResponse, TermUpdate
from app.auth.dependencies import (
    get_current_user,
    require_admin_or_director,
    check_school_ownership,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/terms", tags=["Terms"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> TermService:
    logger.trace("Creating TermService dependency")
    return TermService(db)


@router.post("/", response_model=TermResponse, status_code=201)
def create_term(
    term: TermCreate,
    current_user: dict = Depends(require_admin_or_director),
    service: TermService = Depends(get_service),
):
    """Create a new term. ADMIN or DIRECTOR only."""
    logger.info("POST /api/v1/terms — create term request")
    check_school_ownership(current_user, term.school_id)
    result, error = service.create(term)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/terms — 404 not found: %s", error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/terms — 400 bad request: %s", error)
        raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[TermResponse])
def list_terms(
    current_user: dict = Depends(get_current_user),
    service: TermService = Depends(get_service),
):
    """List all terms. Any authenticated user."""
    logger.info("GET /api/v1/terms — list terms request")
    return service.get_all()


@router.get("/{term_id}", response_model=TermResponse)
def get_term(
    term_id: int,
    current_user: dict = Depends(get_current_user),
    service: TermService = Depends(get_service),
):
    """Get a term by ID. Any authenticated user."""
    logger.info("GET /api/v1/terms/%s — get term request", term_id)
    result = service.get_by_id(term_id)
    if not result:
        logger.warning("GET /api/v1/terms/%s — 404 not found", term_id)
        raise HTTPException(status_code=404, detail="Term not found")
    return result


@router.get("/school/{school_id}", response_model=list[TermResponse])
def get_terms_by_school(
    school_id: int,
    current_user: dict = Depends(get_current_user),
    service: TermService = Depends(get_service),
):
    """Get all terms for a specific school. Any authenticated user."""
    logger.info("GET /api/v1/terms/school/%s — get school terms request", school_id)
    check_school_ownership(current_user, school_id)
    return service.get_by_school_id(school_id)


@router.get("/school/{school_id}/active", response_model=TermResponse)
def get_active_term_by_school(
    school_id: int,
    current_user: dict = Depends(get_current_user),
    service: TermService = Depends(get_service),
):
    """Get the active term for a school. Any authenticated user."""
    logger.info("GET /api/v1/terms/school/%s/active — get active term request", school_id)
    check_school_ownership(current_user, school_id)
    result = service.get_active_term_by_school(school_id)
    if not result:
        logger.warning("GET /api/v1/terms/school/%s/active — 404 not found", school_id)
        raise HTTPException(status_code=404, detail="No active term found for this school")
    return result


@router.put("/{term_id}", response_model=TermResponse)
def update_term(
    term_id: int,
    term: TermUpdate,
    current_user: dict = Depends(require_admin_or_director),
    service: TermService = Depends(get_service),
):
    """Update a term. ADMIN or DIRECTOR only."""
    logger.info("PUT /api/v1/terms/%s — update term request", term_id)
    result, error = service.update(term_id, term)
    if error:
        logger.warning("PUT /api/v1/terms/%s — 404 not found", term_id)
        raise HTTPException(status_code=404, detail=error)
    return result


@router.delete("/{term_id}", status_code=204)
def delete_term(
    term_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: TermService = Depends(get_service),
):
    """Soft delete a term. ADMIN or DIRECTOR only."""
    logger.info("DELETE /api/v1/terms/%s — delete term request", term_id)
    success, error = service.delete(term_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/terms/%s — 404 not found", term_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/terms/%s — 409 conflict: %s", term_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.post("/{term_id}/classes/{class_id}", status_code=200)
def assign_class_to_term(
    term_id: int,
    class_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: TermService = Depends(get_service),
):
    """Assign a class to a term. ADMIN or DIRECTOR only."""
    logger.info("POST /api/v1/terms/%s/classes/%s — assign class to term request", term_id, class_id)
    success, error = service.assign_class_to_term(class_id, term_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/terms/%s/classes/%s — 404 not found: %s", term_id, class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/terms/%s/classes/%s — 400 bad request: %s", term_id, class_id, error)
        raise HTTPException(status_code=400, detail=error)
    return {"message": f"Class {class_id} assigned to term {term_id} successfully"}


@router.delete("/{term_id}/classes/{class_id}", status_code=204)
def unassign_class_from_term(
    term_id: int,
    class_id: int,
    current_user: dict = Depends(require_admin_or_director),
    service: TermService = Depends(get_service),
):
    """Unassign a class from a term. ADMIN or DIRECTOR only."""
    logger.info("DELETE /api/v1/terms/%s/classes/%s — unassign class from term request", term_id, class_id)
    success, error = service.unassign_class_from_term(class_id, term_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/terms/%s/classes/%s — 404 not found: %s", term_id, class_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/terms/%s/classes/%s — 400 bad request: %s", term_id, class_id, error)
        raise HTTPException(status_code=400, detail=error)
    return None


@router.get("/{term_id}/classes", response_model=list[dict])
def get_classes_by_term(
    term_id: int,
    current_user: dict = Depends(get_current_user),
    service: TermService = Depends(get_service),
):
    """Get all classes assigned to a term. Any authenticated user."""
    logger.info("GET /api/v1/terms/%s/classes — get classes by term request", term_id)
    return service.get_classes_by_term(term_id)


@router.get("/class/{class_id}/terms", response_model=list[TermResponse])
def get_terms_by_class(
    class_id: int,
    current_user: dict = Depends(get_current_user),
    service: TermService = Depends(get_service),
):
    """Get all terms assigned to a class. Any authenticated user."""
    logger.info("GET /api/v1/terms/class/%s/terms — get terms by class request", class_id)
    return service.get_terms_by_class(class_id)
