"""Repository layer for Teacher entity."""
import sqlite3
from typing import Optional

from app.repositories.base_repository import BaseRepository, get_current_datetime


class TeacherRepository(BaseRepository):
    """Repository for Teacher database operations."""

    def create(
        self,
        first_name: str,
        last_name: str,
        school_id: int,
        class_id: Optional[int],
        email: Optional[str],
        phone: Optional[str],
        address: Optional[str],
    ) -> dict:
        """Create a new teacher record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO teachers 
               (first_name, last_name, school_id, class_id, email, phone, address, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, school_id, class_id, email, phone, address, created_date),
        )
        self.commit()
        return {
            "teacher_id": self.cursor.lastrowid,
            "first_name": first_name,
            "last_name": last_name,
            "school_id": school_id,
            "class_id": class_id,
            "email": email,
            "phone": phone,
            "address": address,
            "created_date": created_date,
        }

    def get_by_id(self, teacher_id: int) -> Optional[dict]:
        """Get a teacher by ID (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM teachers WHERE teacher_id = ? AND is_deleted = 0",
            (teacher_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all teachers (excluding soft-deleted)."""
        self.cursor.execute("SELECT * FROM teachers WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, teacher_id: int, **kwargs) -> Optional[dict]:
        """Update a teacher record."""
        existing = self.get_by_id(teacher_id)
        if not existing:
            return None

        for key in ("first_name", "last_name", "school_id", "class_id", "email", "phone", "address"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE teachers 
               SET first_name=?, last_name=?, school_id=?, class_id=?, email=?, phone=?, address=? 
               WHERE teacher_id=? AND is_deleted = 0""",
            (
                existing["first_name"],
                existing["last_name"],
                existing["school_id"],
                existing["class_id"],
                existing["email"],
                existing["phone"],
                existing["address"],
                teacher_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, teacher_id: int) -> bool:
        """Soft delete a teacher by setting is_deleted = 1."""
        existing = self.get_by_id(teacher_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE teachers SET is_deleted = 1 WHERE teacher_id = ?",
            (teacher_id,),
        )
        self.commit()
        return True

    def get_by_class_id(self, class_id: int) -> list[dict]:
        """Get all teachers in a class (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM teachers WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def is_assigned_to_class(self, teacher_id: int) -> bool:
        """Check if a teacher is currently assigned to a class."""
        teacher = self.get_by_id(teacher_id)
        if not teacher:
            return False
        return teacher.get("class_id") is not None

    def exists(self, teacher_id: int) -> bool:
        """Check if a teacher exists (not soft-deleted)."""
        return self.get_by_id(teacher_id) is not None
