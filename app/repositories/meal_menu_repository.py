"""Repository layer for Meal Menu entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class MealMenuRepository(BaseRepository):
    """Repository for Meal Menu database operations."""

    def create(
        self,
        school_id: int,
        class_id: Optional[int],
        menu_date: str,
        breakfast: Optional[str],
        lunch: Optional[str],
        dinner: Optional[str],
        breakfast_img_url: Optional[str],
        lunch_img_url: Optional[str],
        dinner_img_url: Optional[str],
        created_by: Optional[int],
    ) -> dict:
        """Create a new meal menu record."""
        logger.debug(
            "Inserting meal menu record for date=%s (school_id=%s, class_id=%s)",
            menu_date, school_id, class_id
        )
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO meal_menus 
               (school_id, class_id, menu_date, breakfast, lunch, dinner, 
                breakfast_img_url, lunch_img_url, dinner_img_url, created_by, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (school_id, class_id, menu_date, breakfast, lunch, dinner,
             breakfast_img_url, lunch_img_url, dinner_img_url, created_by, created_date),
        )
        self.commit()
        logger.trace("Meal menu record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "menu_id": self.cursor.lastrowid,
            "school_id": school_id,
            "class_id": class_id,
            "menu_date": menu_date,
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner,
            "breakfast_img_url": breakfast_img_url,
            "lunch_img_url": lunch_img_url,
            "dinner_img_url": dinner_img_url,
            "created_by": created_by,
            "created_date": created_date,
        }

    def get_by_id(self, menu_id: int) -> Optional[dict]:
        """Get a meal menu by ID (excluding soft-deleted)."""
        logger.trace("SELECT meal menu by id=%s", menu_id)
        self.cursor.execute(
            "SELECT * FROM meal_menus WHERE menu_id = ? AND is_deleted = 0",
            (menu_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all meal menus (excluding soft-deleted)."""
        logger.trace("SELECT all meal menus")
        self.cursor.execute("SELECT * FROM meal_menus WHERE is_deleted = 0 ORDER BY menu_date DESC")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_school_id(self, school_id: int) -> list[dict]:
        """Get all school-wide meal menus for a specific school (excluding soft-deleted)."""
        logger.trace("SELECT all meal menus for school id=%s", school_id)
        self.cursor.execute(
            """SELECT * FROM meal_menus 
               WHERE school_id = ? AND class_id IS NULL AND is_deleted = 0 
               ORDER BY menu_date DESC""",
            (school_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_class_id(self, class_id: int) -> list[dict]:
        """Get all meal menus for a specific class (excluding soft-deleted)."""
        logger.trace("SELECT all meal menus for class id=%s", class_id)
        self.cursor.execute(
            """SELECT * FROM meal_menus 
               WHERE class_id = ? AND is_deleted = 0 
               ORDER BY menu_date DESC""",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_school_and_date_range(
        self, school_id: int, start_date: str, end_date: str
    ) -> list[dict]:
        """Get school-wide meal menus for a school within a date range."""
        logger.trace(
            "SELECT meal menus for school id=%s between %s and %s",
            school_id, start_date, end_date
        )
        self.cursor.execute(
            """SELECT * FROM meal_menus 
               WHERE school_id = ? AND class_id IS NULL AND is_deleted = 0 
               AND menu_date BETWEEN ? AND ?
               ORDER BY menu_date DESC""",
            (school_id, start_date, end_date),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_class_and_date_range(
        self, class_id: int, start_date: str, end_date: str
    ) -> list[dict]:
        """Get meal menus for a class within a date range."""
        logger.trace(
            "SELECT meal menus for class id=%s between %s and %s",
            class_id, start_date, end_date
        )
        self.cursor.execute(
            """SELECT * FROM meal_menus 
               WHERE class_id = ? AND is_deleted = 0 
               AND menu_date BETWEEN ? AND ?
               ORDER BY menu_date DESC""",
            (class_id, start_date, end_date),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_date(self, school_id: int, menu_date: str) -> Optional[dict]:
        """Get school-wide meal menu for a specific date."""
        logger.trace("SELECT meal menu for school id=%s on date=%s", school_id, menu_date)
        self.cursor.execute(
            """SELECT * FROM meal_menus 
               WHERE school_id = ? AND menu_date = ? AND class_id IS NULL AND is_deleted = 0""",
            (school_id, menu_date),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_by_class_and_date(self, class_id: int, menu_date: str) -> Optional[dict]:
        """Get meal menu for a specific class and date."""
        logger.trace("SELECT meal menu for class id=%s on date=%s", class_id, menu_date)
        self.cursor.execute(
            """SELECT * FROM meal_menus 
               WHERE class_id = ? AND menu_date = ? AND is_deleted = 0""",
            (class_id, menu_date),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def update(self, menu_id: int, **kwargs) -> Optional[dict]:
        """Update a meal menu record."""
        logger.debug("Updating meal menu record: id=%s, fields=%s", menu_id, list(kwargs.keys()))
        existing = self.get_by_id(menu_id)
        if not existing:
            return None

        for key in ("class_id", "menu_date", "breakfast", "lunch", "dinner",
                    "breakfast_img_url", "lunch_img_url", "dinner_img_url"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE meal_menus 
               SET class_id=?, menu_date=?, breakfast=?, lunch=?, dinner=?, 
                   breakfast_img_url=?, lunch_img_url=?, dinner_img_url=? 
               WHERE menu_id=? AND is_deleted = 0""",
            (
                existing["class_id"],
                existing["menu_date"],
                existing["breakfast"],
                existing["lunch"],
                existing["dinner"],
                existing["breakfast_img_url"],
                existing["lunch_img_url"],
                existing["dinner_img_url"],
                menu_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, menu_id: int) -> bool:
        """Soft delete a meal menu by setting is_deleted = 1."""
        logger.debug("Soft-deleting meal menu: id=%s", menu_id)
        existing = self.get_by_id(menu_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE meal_menus SET is_deleted = 1 WHERE menu_id = ?",
            (menu_id,),
        )
        self.commit()
        logger.trace("Meal menu soft-deleted in DB: id=%s", menu_id)
        return True

    def exists(self, menu_id: int) -> bool:
        """Check if a meal menu exists (not soft-deleted)."""
        logger.trace("Checking if meal menu exists: id=%s", menu_id)
        result = self.get_by_id(menu_id) is not None
        logger.trace("Meal menu exists check result: id=%s → %s", menu_id, result)
        return result

    def check_duplicate(
        self, school_id: int, menu_date: str, class_id: Optional[int] = None
    ) -> bool:
        """Check if a meal menu already exists for the given date and class."""
        logger.trace(
            "Checking duplicate meal menu: school_id=%s, date=%s, class_id=%s",
            school_id, menu_date, class_id
        )
        if class_id is not None:
            self.cursor.execute(
                """SELECT COUNT(*) as count FROM meal_menus 
                   WHERE school_id = ? AND menu_date = ? 
                   AND class_id = ? AND is_deleted = 0""",
                (school_id, menu_date, class_id),
            )
        else:
            self.cursor.execute(
                """SELECT COUNT(*) as count FROM meal_menus 
                   WHERE school_id = ? AND menu_date = ? 
                   AND class_id IS NULL AND is_deleted = 0""",
                (school_id, menu_date),
            )
        count = self.cursor.fetchone()["count"]
        exists = count > 0
        logger.trace("Duplicate check result: %s", exists)
        return exists
