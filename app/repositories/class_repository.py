"""Repository layer for Class entity."""
import sqlite3
from typing import Optional

from app.repositories.base_repository import BaseRepository, get_current_datetime


class ClassRepository(BaseRepository):
    """Repository for Class database operations."""

    def create(
        self,
        class_name: str,
        school_id: int,
        capacity: Optional[int],
    ) -> dict:
        """Create a new class record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO classes 
               (class_name, school_id, capacity, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, 0)""",
            (class_name, school_id, capacity, created_date),
        )
        self.commit()
        return {
            "class_id": self.cursor.lastrowid,
            "class_name": class_name,
            "school_id": school_id,
            "capacity": capacity,
            "created_date": created_date,
        }

    def get_by_id(self, class_id: int) -> Optional[dict]:
        """Get a class by ID (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM classes WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all classes (excluding soft-deleted)."""
        self.cursor.execute("SELECT * FROM classes WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, class_id: int, **kwargs) -> Optional[dict]:
        """Update a class record."""
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
        existing = self.get_by_id(class_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE classes SET is_deleted = 1 WHERE class_id = ?",
            (class_id,),
        )
        self.commit()
        return True

    def count_active_students(self, class_id: int) -> int:
        """Count active students in a class."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        return self.cursor.fetchone()["count"]

    def exists(self, class_id: int) -> bool:
        """Check if a class exists (not soft-deleted)."""
        return self.get_by_id(class_id) is not None

    def count_active_teachers(self, class_id: int) -> int:
        """Count active teachers assigned to a class."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM teachers WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        return self.cursor.fetchone()["count"]

    def get_current_student_count(self, class_id: int) -> int:
        """Get the current number of students in a class."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        return self.cursor.fetchone()["count"]

    def check_capacity_available(self, class_id: int, additional_students: int = 1) -> tuple[bool, Optional[str]]:
        """Check if class has capacity for additional students."""
        class_data = self.get_by_id(class_id)
        if not class_data:
            return False, "Class not found"
        
        capacity = class_data.get("capacity")
        if capacity is None:
            # No capacity limit set, allow unlimited students
            return True, None
        
        current_count = self.get_current_student_count(class_id)
        if current_count + additional_students > capacity:
            return False, f"Class capacity exceeded. Current: {current_count}, Capacity: {capacity}, Trying to add: {additional_students}"
        
        return True, None
