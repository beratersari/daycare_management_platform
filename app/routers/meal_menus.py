"""Router layer for Meal Menu endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.database.connection import get_db
from app.logger import get_logger
from app.services.meal_menu_service import MealMenuService
from app.schemas.meal_menu import MealMenuCreate, MealMenuResponse, MealMenuUpdate

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/meals", tags=["Meal Menus"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> MealMenuService:
    logger.trace("Creating MealMenuService dependency")
    return MealMenuService(db)


@router.post("/", response_model=MealMenuResponse, status_code=201)
def create_meal_menu(
    menu: MealMenuCreate,
    service: MealMenuService = Depends(get_service),
):
    """Create a new meal menu. Teachers can use this to design daily menus."""
    logger.info("POST /api/v1/meals — create meal menu request")
    result, error = service.create(menu)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/meals — 404 not found: %s", error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/meals — 409 conflict: %s", error)
        raise HTTPException(status_code=409, detail=error)
    return result


@router.get("/", response_model=list[MealMenuResponse])
def list_meal_menus(service: MealMenuService = Depends(get_service)):
    """List all meal menus."""
    logger.info("GET /api/v1/meals — list meal menus request")
    return service.get_all()


@router.get("/{menu_id}", response_model=MealMenuResponse)
def get_meal_menu(
    menu_id: int,
    service: MealMenuService = Depends(get_service),
):
    """Get a meal menu by ID."""
    logger.info("GET /api/v1/meals/%s — get meal menu request", menu_id)
    result = service.get_by_id(menu_id)
    if not result:
        logger.warning("GET /api/v1/meals/%s — 404 not found", menu_id)
        raise HTTPException(status_code=404, detail="Meal menu not found")
    return result


@router.get("/school/{school_id}", response_model=list[MealMenuResponse])
def get_meal_menus_by_school(
    school_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    service: MealMenuService = Depends(get_service),
):
    """Get meal menus for a school. Optionally filter by date range."""
    logger.info("GET /api/v1/meals/school/%s — get school meal menus request", school_id)
    if start_date and end_date:
        return service.get_by_school_and_date_range(school_id, start_date, end_date)
    return service.get_by_school_id(school_id)


@router.get("/school/{school_id}/date/{menu_date}", response_model=list[MealMenuResponse])
def get_meal_menus_by_school_and_date(
    school_id: int,
    menu_date: str,
    service: MealMenuService = Depends(get_service),
):
    """Get all meal menus for a specific school and date. Parents use this to see daily meals."""
    logger.info("GET /api/v1/meals/school/%s/date/%s — get daily meal menus", school_id, menu_date)
    return service.get_by_date(school_id, menu_date)


@router.get("/class/{class_id}", response_model=list[MealMenuResponse])
def get_meal_menus_by_class(
    class_id: int,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    service: MealMenuService = Depends(get_service),
):
    """Get meal menus for a class. Optionally filter by date range."""
    logger.info("GET /api/v1/meals/class/%s — get class meal menus request", class_id)
    if start_date and end_date:
        return service.get_by_class_and_date_range(class_id, start_date, end_date)
    return service.get_by_class_id(class_id)


@router.get("/class/{class_id}/date/{menu_date}", response_model=list[MealMenuResponse])
def get_meal_menus_by_class_and_date(
    class_id: int,
    menu_date: str,
    service: MealMenuService = Depends(get_service),
):
    """Get all meal menus for a specific class and date. Includes school-wide menus."""
    logger.info("GET /api/v1/meals/class/%s/date/%s — get class daily meal menus", class_id, menu_date)
    return service.get_by_class_and_date(class_id, menu_date)


@router.put("/{menu_id}", response_model=MealMenuResponse)
def update_meal_menu(
    menu_id: int,
    menu: MealMenuUpdate,
    service: MealMenuService = Depends(get_service),
):
    """Update a meal menu."""
    logger.info("PUT /api/v1/meals/%s — update meal menu request", menu_id)
    result, error = service.update(menu_id, menu)
    if error:
        if "not found" in error.lower():
            logger.warning("PUT /api/v1/meals/%s — 404 not found: %s", menu_id, error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("PUT /api/v1/meals/%s — 409 conflict: %s", menu_id, error)
        raise HTTPException(status_code=409, detail=error)
    return result


@router.delete("/{menu_id}", status_code=204)
def delete_meal_menu(
    menu_id: int,
    service: MealMenuService = Depends(get_service),
):
    """Soft delete a meal menu."""
    logger.info("DELETE /api/v1/meals/%s — delete meal menu request", menu_id)
    success, error = service.delete(menu_id)
    if not success:
        logger.warning("DELETE /api/v1/meals/%s — 404 not found: %s", menu_id, error)
        raise HTTPException(status_code=404, detail=error)
    return None