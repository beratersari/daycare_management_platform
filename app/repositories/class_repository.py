"""Repository layer for Class entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class ClassRepository(BaseRepository):
    """Repository for Class database operations."""

    def create(
        self,
        class_name: str,
        school_id: int,
        capacity: Optional[int],
    ) -> dict:
        """Create a new class record."""
        logger.debug("Inserting class record: %s (school_id=%s)", class_name, school_id)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO classes 
               (class_name, school_id, capacity, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, 0)""",
            (class_name, school_id, capacity, created_date),
        )
        self.commit()
        logger.trace("Class record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "class_id": self.cursor.lastrowid,
            "class_name": class_name,
            "school_id": school_id,
            "capacity": capacity,
            "created_date": created_date,
        }

    def get_by_id(self, class_id: int) -> Optional[dict]:
        """Get a class by ID (excluding soft-deleted)."""
        logger.trace("SELECT class by id=%s", class_id)
        self.cursor.execute(
            "SELECT * FROM classes WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all classes (excluding soft-deleted)."""
        logger.trace("SELECT all classes")
        self.cursor.execute("SELECT * FROM classes WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, class_id: int, **kwargs) -> Optional[dict]:
        """Update a class record."""
        logger.debug("Updating class record: id=%s, fields=%s", class_id, list(kwargs.keys()))
        existing = self.get_by_id(class_id)
        if not existing:
            return None

        for key in ("class_name", "school_id", "capacity"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE classes 
               SET class_name=?, school_id=?, capacity=? 
               WHERE class_id=? AND is_deleted = 0""",
            (existing["class_name"], existing["school_id"], existing["capacity"], class_id),
        )
        self.commit()
        return existing

    def soft_delete(self, class_id: int) -> bool:
        """Soft delete a class by setting is_deleted = 1."""
        logger.debug("Soft-deleting class: id=%s", class_id)
        existing = self.get_by_id(class_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE classes SET is_deleted = 1 WHERE class_id = ?",
            (class_id,),
        )
        self.commit()
        logger.trace("Class soft-deleted in DB: id=%s", class_id)
        return True

    def count_active_students(self, class_id: int) -> int:
        """Count active students enrolled in a class."""
        logger.trace("Counting active students for class id=%s", class_id)
        self.cursor.execute(
            """SELECT COUNT(*) as count FROM student_classes sc
               JOIN students s ON sc.student_id = s.student_id
               WHERE sc.class_id = ? AND s.is_deleted = 0""",
            (class_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active students count for class id=%s: %d", class_id, count)
        return count

    def exists(self, class_id: int) -> bool:
        """Check if a class exists (not soft-deleted)."""
        logger.trace("Checking if class exists: id=%s", class_id)
        result = self.get_by_id(class_id) is not None
        logger.trace("Class exists check result: id=%s → %s", class_id, result)
        return result

    def count_active_teachers(self, class_id: int) -> int:
        """Count active teachers assigned to a class."""
        logger.trace("Counting active teachers for class id=%s", class_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM teachers WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active teachers count for class id=%s: %d", class_id, count)
        return count

    def get_current_student_count(self, class_id: int) -> int:
        """Get the current number of active students enrolled in a class."""
        logger.trace("Getting current student count for class id=%s", class_id)
        self.cursor.execute(
            """SELECT COUNT(*) as count FROM student_classes sc
               JOIN students s ON sc.student_id = s.student_id
               WHERE sc.class_id = ? AND s.is_deleted = 0""",
            (class_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Current student count for class id=%s: %d", class_id, count)
        return count

    def check_capacity_available(self, class_id: int, additional_students: int = 1) -> tuple[bool, Optional[str]]:
        """Check if class has capacity for additional students."""
        logger.debug("Checking capacity for class id=%s (adding %d)", class_id, additional_students)
        class_data = self.get_by_id(class_id)
        if not class_data:
            logger.warning("Class not found for capacity check: id=%s", class_id)
            return False, "Class not found"
        
        capacity = class_data.get("capacity")
        if capacity is None:
            # No capacity limit set, allow unlimited students
            logger.trace("Class id=%s has no capacity limit — allowing", class_id)
            return True, None
        
        current_count = self.get_current_student_count(class_id)
        if current_count + additional_students > capacity:
            msg = f"Class capacity exceeded. Current: {current_count}, Capacity: {capacity}, Trying to add: {additional_students}"
            logger.warning("Class capacity check failed for id=%s: %s", class_id, msg)
            return False, msg
        
        logger.trace("Class capacity check passed for id=%s: %d/%d", class_id, current_count, capacity)
        return True, None
