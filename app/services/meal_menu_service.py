"""Service layer for Meal Menu entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.meal_menu_repository import MealMenuRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.teacher_repository import TeacherRepository
from app.schemas.meal_menu import MealMenuCreate, MealMenuResponse, MealMenuUpdate

logger = get_logger(__name__)


class MealMenuService:
    """Service for Meal Menu business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = MealMenuRepository(db)
        self.school_repo = SchoolRepository(db)
        self.class_repo = ClassRepository(db)
        self.teacher_repo = TeacherRepository(db)
        logger.trace("MealMenuService initialised")

    def create(
        self, data: MealMenuCreate, created_by: Optional[int] = None
    ) -> tuple[Optional[MealMenuResponse], Optional[str]]:
        """Create a new meal menu."""
        logger.info(
            "Creating meal menu for date=%s (school_id=%s, class_id=%s)",
            data.menu_date, data.school_id, data.class_id
        )
        logger.debug("Meal menu creation payload: %s", data.model_dump())

        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            logger.warning("School not found during meal menu creation: school_id=%s", data.school_id)
            return None, "School not found"

        # Validate class exists if provided
        if data.class_id is not None and not self.class_repo.exists(data.class_id):
            logger.warning("Class not found during meal menu creation: class_id=%s", data.class_id)
            return None, "Class not found"

        # Validate teacher exists if created_by is provided
        if created_by is not None and not self.teacher_repo.exists(created_by):
            logger.warning("Teacher not found during meal menu creation: teacher_id=%s", created_by)
            return None, "Teacher not found"

        # Check for duplicate entry (only one menu per school/class/date)
        if self.repo.check_duplicate(data.school_id, data.menu_date, data.class_id):
            logger.warning(
                "Duplicate meal menu entry: school_id=%s, date=%s, class_id=%s",
                data.school_id, data.menu_date, data.class_id
            )
            scope = f"class {data.class_id}" if data.class_id else "school-wide"
            return None, f"A menu already exists for {data.menu_date} ({scope})"

        # Create meal menu
        menu = self.repo.create(
            school_id=data.school_id,
            class_id=data.class_id,
            menu_date=data.menu_date,
            breakfast=data.breakfast,
            lunch=data.lunch,
            dinner=data.dinner,
            breakfast_img_url=data.breakfast_img_url,
            lunch_img_url=data.lunch_img_url,
            dinner_img_url=data.dinner_img_url,
            created_by=created_by,
        )

        logger.info("Meal menu created successfully with id=%s", menu["menu_id"])
        return MealMenuResponse(**menu), None

    def get_all(self) -> list[MealMenuResponse]:
        """Get all meal menus."""
        logger.debug("Fetching all meal menus")
        menus = self.repo.get_all()
        logger.info("Retrieved %d meal menu(s)", len(menus))
        return [MealMenuResponse(**m) for m in menus]

    def get_by_id(self, menu_id: int) -> Optional[MealMenuResponse]:
        """Get a meal menu by ID."""
        logger.debug("Fetching meal menu by id=%s", menu_id)
        menu = self.repo.get_by_id(menu_id)
        if not menu:
            logger.warning("Meal menu not found: id=%s", menu_id)
            return None
        logger.trace("Meal menu found: %s", menu)
        return MealMenuResponse(**menu)

    def get_by_school_id(self, school_id: int) -> list[MealMenuResponse]:
        """Get all school-wide meal menus for a specific school."""
        logger.debug("Fetching meal menus for school_id=%s", school_id)
        if not self.school_repo.exists(school_id):
            logger.warning("School not found: id=%s", school_id)
            return []
        menus = self.repo.get_by_school_id(school_id)
        logger.info("Retrieved %d meal menu(s) for school id=%s", len(menus), school_id)
        return [MealMenuResponse(**m) for m in menus]

    def get_by_class_id(self, class_id: int) -> list[MealMenuResponse]:
        """Get all meal menus for a specific class."""
        logger.debug("Fetching meal menus for class_id=%s", class_id)
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return []
        menus = self.repo.get_by_class_id(class_id)
        logger.info("Retrieved %d meal menu(s) for class id=%s", len(menus), class_id)
        return [MealMenuResponse(**m) for m in menus]

    def get_by_school_and_date_range(
        self, school_id: int, start_date: str, end_date: str
    ) -> list[MealMenuResponse]:
        """Get school-wide meal menus for a school within a date range."""
        logger.debug(
            "Fetching meal menus for school_id=%s between %s and %s",
            school_id, start_date, end_date
        )
        if not self.school_repo.exists(school_id):
            logger.warning("School not found: id=%s", school_id)
            return []
        menus = self.repo.get_by_school_and_date_range(school_id, start_date, end_date)
        logger.info(
            "Retrieved %d meal menu(s) for school id=%s in date range",
            len(menus), school_id
        )
        return [MealMenuResponse(**m) for m in menus]

    def get_by_class_and_date_range(
        self, class_id: int, start_date: str, end_date: str
    ) -> list[MealMenuResponse]:
        """Get meal menus for a class within a date range."""
        logger.debug(
            "Fetching meal menus for class_id=%s between %s and %s",
            class_id, start_date, end_date
        )
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return []
        menus = self.repo.get_by_class_and_date_range(class_id, start_date, end_date)
        logger.info(
            "Retrieved %d meal menu(s) for class id=%s in date range",
            len(menus), class_id
        )
        return [MealMenuResponse(**m) for m in menus]

    def get_by_date(self, school_id: int, menu_date: str) -> Optional[MealMenuResponse]:
        """Get school-wide meal menu for a specific date."""
        logger.debug("Fetching meal menu for school_id=%s on date=%s", school_id, menu_date)
        if not self.school_repo.exists(school_id):
            logger.warning("School not found: id=%s", school_id)
            return None
        menu = self.repo.get_by_date(school_id, menu_date)
        if not menu:
            logger.trace("No menu found for school id=%s on date=%s", school_id, menu_date)
            return None
        logger.info("Retrieved meal menu for school id=%s on date=%s", school_id, menu_date)
        return MealMenuResponse(**menu)

    def get_by_class_and_date(self, class_id: int, menu_date: str) -> Optional[MealMenuResponse]:
        """Get meal menu for a specific class and date."""
        logger.debug("Fetching meal menu for class_id=%s on date=%s", class_id, menu_date)
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return None
        menu = self.repo.get_by_class_and_date(class_id, menu_date)
        if not menu:
            logger.trace("No menu found for class id=%s on date=%s", class_id, menu_date)
            return None
        logger.info("Retrieved meal menu for class id=%s on date=%s", class_id, menu_date)
        return MealMenuResponse(**menu)

    def update(
        self, menu_id: int, data: MealMenuUpdate
    ) -> tuple[Optional[MealMenuResponse], Optional[str]]:
        """Update a meal menu."""
        logger.info("Updating meal menu: id=%s", menu_id)
        existing = self.repo.get_by_id(menu_id)
        if not existing:
            logger.warning("Meal menu not found for update: id=%s", menu_id)
            return None, "Meal menu not found"

        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Meal menu update data: %s", update_data)

        # Validate class exists if being updated
        if "class_id" in update_data and update_data["class_id"] is not None:
            if not self.class_repo.exists(update_data["class_id"]):
                logger.warning(
                    "Class not found during meal menu update: class_id=%s",
                    update_data["class_id"]
                )
                return None, "Class not found"

        # Check for duplicates if date or class is being changed
        new_date = update_data.get("menu_date", existing["menu_date"])
        new_class_id = update_data.get("class_id", existing["class_id"])

        if new_date != existing["menu_date"] or new_class_id != existing["class_id"]:
            if self.repo.check_duplicate(existing["school_id"], new_date, new_class_id):
                scope = f"class {new_class_id}" if new_class_id else "school-wide"
                return None, f"A menu already exists for {new_date} ({scope})"

        result = self.repo.update(menu_id, **update_data)
        logger.info("Meal menu updated successfully: id=%s", menu_id)
        return MealMenuResponse(**result), None

    def delete(self, menu_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a meal menu."""
        logger.info("Attempting to delete meal menu: id=%s", menu_id)
        if not self.repo.exists(menu_id):
            logger.warning("Meal menu not found for deletion: id=%s", menu_id)
            return False, "Meal menu not found"

        self.repo.soft_delete(menu_id)
        logger.info("Meal menu soft-deleted successfully: id=%s", menu_id)
        return True, None

    def exists(self, menu_id: int) -> bool:
        """Check if meal menu exists."""
        result = self.repo.exists(menu_id)
        logger.trace("Meal menu exists check: id=%s → %s", menu_id, result)
        return result
