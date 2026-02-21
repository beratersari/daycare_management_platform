"""Repository layer for Class entity."""
import sqlite3
from typing import Optional

from app.repositories.base_repository import BaseRepository, get_current_datetime


class ClassRepository(BaseRepository):
    """Repository for Class database operations."""

    def create(
        self,
        class_name: str,
        capacity: Optional[int],
    ) -> dict:
        """Create a new class record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO classes 
               (class_name, capacity, created_date, is_deleted) 
               VALUES (?, ?, ?, 0)""",
            (class_name, capacity, created_date),
        )
        self.commit()
        return {
            "class_id": self.cursor.lastrowid,
            "class_name": class_name,
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

        for key in ("class_name", "capacity"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE classes 
               SET class_name=?, capacity=? 
               WHERE class_id=? AND is_deleted = 0""",
            (existing["class_name"], existing["capacity"], class_id),
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

    def exists(self, class_id: int) -> bool:
        """Check if a class exists (not soft-deleted)."""
        return self.get_by_id(class_id) is not None

    # --- Teacher links ---

    def link_teacher(self, class_id: int, teacher_id: int):
        """Link a teacher to a class."""
        self.cursor.execute(
            "INSERT OR IGNORE INTO class_teachers (class_id, teacher_id) VALUES (?, ?)",
            (class_id, teacher_id),
        )
        self.commit()

    def unlink_all_teachers(self, class_id: int):
        """Remove all teacher links for a class."""
        self.cursor.execute(
            "DELETE FROM class_teachers WHERE class_id = ?",
            (class_id,),
        )
        self.commit()

    def get_teacher_ids(self, class_id: int) -> list[int]:
        """Get all teacher IDs for a class (excluding soft-deleted teachers)."""
        self.cursor.execute(
            """SELECT ct.teacher_id FROM class_teachers ct
               JOIN teachers t ON ct.teacher_id = t.teacher_id
               WHERE ct.class_id = ? AND t.is_deleted = 0""",
            (class_id,),
        )
        return [row["teacher_id"] for row in self.cursor.fetchall()]

    def get_teachers(self, class_id: int) -> list[dict]:
        """Get all teachers for a class (excluding soft-deleted)."""
        self.cursor.execute(
            """SELECT t.* FROM teachers t
               JOIN class_teachers ct ON t.teacher_id = ct.teacher_id
               WHERE ct.class_id = ? AND t.is_deleted = 0""",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]
