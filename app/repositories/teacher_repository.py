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
        email: Optional[str],
        phone: Optional[str],
        address: Optional[str],
    ) -> dict:
        """Create a new teacher record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO teachers 
               (first_name, last_name, email, phone, address, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, email, phone, address, created_date),
        )
        self.commit()
        return {
            "teacher_id": self.cursor.lastrowid,
            "first_name": first_name,
            "last_name": last_name,
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

        for key, value in kwargs.items():
            if key in existing and value is not None:
                existing[key] = value

        self.cursor.execute(
            """UPDATE teachers 
               SET first_name=?, last_name=?, email=?, phone=?, address=? 
               WHERE teacher_id=? AND is_deleted = 0""",
            (
                existing["first_name"],
                existing["last_name"],
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

    def get_class_ids(self, teacher_id: int) -> list[int]:
        """Get all class IDs for this teacher."""
        self.cursor.execute(
            """SELECT ct.class_id FROM class_teachers ct
               JOIN classes c ON ct.class_id = c.class_id
               WHERE ct.teacher_id = ? AND c.is_deleted = 0""",
            (teacher_id,),
        )
        return [row["class_id"] for row in self.cursor.fetchall()]

    def exists(self, teacher_id: int) -> bool:
        """Check if a teacher exists (not soft-deleted)."""
        return self.get_by_id(teacher_id) is not None
