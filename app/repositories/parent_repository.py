"""Repository layer for Parent entity."""
import sqlite3
from typing import Optional

from app.repositories.base_repository import BaseRepository, get_current_datetime


class ParentRepository(BaseRepository):
    """Repository for Parent database operations."""

    def create(
        self,
        first_name: str,
        last_name: str,
        school_id: int,
        email: Optional[str],
        phone: Optional[str],
        address: Optional[str],
    ) -> dict:
        """Create a new parent record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO parents 
               (first_name, last_name, school_id, email, phone, address, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, school_id, email, phone, address, created_date),
        )
        self.commit()
        return {
            "parent_id": self.cursor.lastrowid,
            "first_name": first_name,
            "last_name": last_name,
            "school_id": school_id,
            "email": email,
            "phone": phone,
            "address": address,
            "created_date": created_date,
        }

    def get_by_id(self, parent_id: int) -> Optional[dict]:
        """Get a parent by ID (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM parents WHERE parent_id = ? AND is_deleted = 0",
            (parent_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all parents (excluding soft-deleted)."""
        self.cursor.execute("SELECT * FROM parents WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, parent_id: int, **kwargs) -> Optional[dict]:
        """Update a parent record."""
        existing = self.get_by_id(parent_id)
        if not existing:
            return None

        for key, value in kwargs.items():
            if key in existing and value is not None:
                existing[key] = value

        self.cursor.execute(
            """UPDATE parents 
               SET first_name=?, last_name=?, school_id=?, email=?, phone=?, address=? 
               WHERE parent_id=? AND is_deleted = 0""",
            (
                existing["first_name"],
                existing["last_name"],
                existing["school_id"],
                existing["email"],
                existing["phone"],
                existing["address"],
                parent_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, parent_id: int) -> bool:
        """Soft delete a parent by setting is_deleted = 1."""
        existing = self.get_by_id(parent_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE parents SET is_deleted = 1 WHERE parent_id = ?",
            (parent_id,),
        )
        self.commit()
        return True

    def count_linked_students(self, parent_id: int) -> int:
        """Count students linked to this parent."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM student_parents WHERE parent_id = ?",
            (parent_id,),
        )
        return self.cursor.fetchone()["count"]

    def get_student_ids(self, parent_id: int) -> list[int]:
        """Get all student IDs linked to this parent."""
        self.cursor.execute(
            """SELECT sp.student_id FROM student_parents sp
               JOIN students s ON sp.student_id = s.student_id
               WHERE sp.parent_id = ? AND s.is_deleted = 0""",
            (parent_id,),
        )
        return [row["student_id"] for row in self.cursor.fetchall()]

    def exists(self, parent_id: int) -> bool:
        """Check if a parent exists (not soft-deleted)."""
        return self.get_by_id(parent_id) is not None
