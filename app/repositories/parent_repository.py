"""Repository layer for Parent entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


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
        logger.debug("Inserting parent record: %s %s", first_name, last_name)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO parents 
               (first_name, last_name, school_id, email, phone, address, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, school_id, email, phone, address, created_date),
        )
        self.commit()
        logger.trace("Parent record inserted with rowid=%s", self.cursor.lastrowid)
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
        logger.trace("SELECT parent by id=%s", parent_id)
        self.cursor.execute(
            "SELECT * FROM parents WHERE parent_id = ? AND is_deleted = 0",
            (parent_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all parents (excluding soft-deleted)."""
        logger.trace("SELECT all parents")
        self.cursor.execute("SELECT * FROM parents WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, parent_id: int, **kwargs) -> Optional[dict]:
        """Update a parent record."""
        logger.debug("Updating parent record: id=%s, fields=%s", parent_id, list(kwargs.keys()))
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
        logger.debug("Soft-deleting parent: id=%s", parent_id)
        existing = self.get_by_id(parent_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE parents SET is_deleted = 1 WHERE parent_id = ?",
            (parent_id,),
        )
        self.commit()
        logger.trace("Parent soft-deleted in DB: id=%s", parent_id)
        return True

    def count_linked_students(self, parent_id: int) -> int:
        """Count students linked to this parent."""
        logger.trace("Counting linked students for parent id=%s", parent_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM student_parents WHERE parent_id = ?",
            (parent_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Linked students count for parent id=%s: %d", parent_id, count)
        return count

    def get_student_ids(self, parent_id: int) -> list[int]:
        """Get all student IDs linked to this parent."""
        logger.trace("Fetching student IDs for parent id=%s", parent_id)
        self.cursor.execute(
            """SELECT sp.student_id FROM student_parents sp
               JOIN students s ON sp.student_id = s.student_id
               WHERE sp.parent_id = ? AND s.is_deleted = 0""",
            (parent_id,),
        )
        student_ids = [row["student_id"] for row in self.cursor.fetchall()]
        logger.trace("Student IDs for parent id=%s: %s", parent_id, student_ids)
        return student_ids

    def exists(self, parent_id: int) -> bool:
        """Check if a parent exists (not soft-deleted)."""
        logger.trace("Checking if parent exists: id=%s", parent_id)
        result = self.get_by_id(parent_id) is not None
        logger.trace("Parent exists check result: id=%s → %s", parent_id, result)
        return result
