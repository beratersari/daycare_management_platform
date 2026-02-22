"""Router layer for Class endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
from app.logger import get_logger
from app.services.class_service import ClassService
from app.schemas.class_dto import ClassCreate, ClassResponse, ClassUpdate

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/classes", tags=["Classes"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> ClassService:
    logger.trace("Creating ClassService dependency")
    return ClassService(db)


@router.post("/", response_model=ClassResponse, status_code=201)
def create_class(
    cls: ClassCreate,
    service: ClassService = Depends(get_service),
):
    """Create a new class."""
    logger.info("POST /api/v1/classes — create class request")
    result, error = service.create(cls)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/classes — 404: %s", error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("POST /api/v1/classes — 400: %s", error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.get("/", response_model=list[ClassResponse])
def list_classes(service: ClassService = Depends(get_service)):
    """List all classes."""
    logger.info("GET /api/v1/classes — list classes request")
    return service.get_all()


@router.get("/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, service: ClassService = Depends(get_service)):
    """Get a class by ID with students and teachers."""
    logger.info("GET /api/v1/classes/%s — get class request", class_id)
    result = service.get_by_id(class_id)
    if not result:
        logger.warning("GET /api/v1/classes/%s — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    return result


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    cls: ClassUpdate,
    service: ClassService = Depends(get_service),
):
    """Update a class."""
    logger.info("PUT /api/v1/classes/%s — update class request", class_id)
    result, error = service.update(class_id, cls)
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/classes/%s — 404: %s", class_id, error)
            raise HTTPException(status_code=404, detail=error)
        else:
            logger.warning("PUT /api/v1/classes/%s — 400: %s", class_id, error)
            raise HTTPException(status_code=400, detail=error)
    return result


@router.delete("/{class_id}", status_code=204)
def delete_class(class_id: int, service: ClassService = Depends(get_service)):
    """Soft delete a class."""
    logger.info("DELETE /api/v1/classes/%s — delete class request", class_id)
    success, error = service.delete(class_id)
    if not success:
        if "not found" in error.lower():
            logger.warning("DELETE /api/v1/classes/%s — 404 not found", class_id)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("DELETE /api/v1/classes/%s — 409 conflict: %s", class_id, error)
        raise HTTPException(status_code=409, detail=error)
    return None


@router.get("/{class_id}/capacity")
def get_class_capacity_info(class_id: int, service: ClassService = Depends(get_service)):
    """Get class capacity information."""
    logger.info("GET /api/v1/classes/%s/capacity — capacity info request", class_id)
    result = service.get_capacity_info(class_id)
    if not result:
        logger.warning("GET /api/v1/classes/%s/capacity — 404 not found", class_id)
        raise HTTPException(status_code=404, detail="Class not found")
    return result
