"""Repository layer for Term entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class TermRepository(BaseRepository):
    """Repository for Term database operations."""

    def create(
        self,
        school_id: int,
        term_name: str,
        start_date: str,
        end_date: Optional[str] = None,
        activity_status: bool = True,
        term_img_url: Optional[str] = None,
    ) -> dict:
        """Create a new term record."""
        logger.debug("Inserting term record: %s (school_id=%s)", term_name, school_id)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO terms 
               (school_id, term_name, start_date, end_date, activity_status, term_img_url, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (school_id, term_name, start_date, end_date, activity_status, term_img_url, created_date),
        )
        self.commit()
        logger.trace("Term record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "term_id": self.cursor.lastrowid,
            "school_id": school_id,
            "term_name": term_name,
            "start_date": start_date,
            "end_date": end_date,
            "activity_status": activity_status,
            "term_img_url": term_img_url,
            "created_date": created_date,
        }

    def get_by_id(self, term_id: int) -> Optional[dict]:
        """Get a term by ID (excluding soft-deleted)."""
        logger.trace("SELECT term by id=%s", term_id)
        self.cursor.execute(
            "SELECT * FROM terms WHERE term_id = ? AND is_deleted = 0",
            (term_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all terms (excluding soft-deleted)."""
        logger.trace("SELECT all terms")
        self.cursor.execute("SELECT * FROM terms WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_school_id(self, school_id: int) -> list[dict]:
        """Get all terms for a specific school (excluding soft-deleted)."""
        logger.trace("SELECT all terms for school id=%s", school_id)
        self.cursor.execute(
            "SELECT * FROM terms WHERE school_id = ? AND is_deleted = 0 ORDER BY created_date DESC",
            (school_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_active_term_by_school(self, school_id: int) -> Optional[dict]:
        """Get the active term for a school (where end_date is NULL or in the future)."""
        logger.trace("SELECT active term for school id=%s", school_id)
        self.cursor.execute(
            """SELECT * FROM terms 
               WHERE school_id = ? AND is_deleted = 0 AND activity_status = 1 
               AND (end_date IS NULL OR end_date > date('now'))
               ORDER BY start_date DESC LIMIT 1""",
            (school_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def update(self, term_id: int, **kwargs) -> Optional[dict]:
        """Update a term record."""
        logger.debug("Updating term record: id=%s, fields=%s", term_id, list(kwargs.keys()))
        existing = self.get_by_id(term_id)
        if not existing:
            return None

        for key in ("term_name", "start_date", "end_date", "activity_status", "term_img_url"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE terms 
               SET term_name=?, start_date=?, end_date=?, activity_status=?, term_img_url=? 
               WHERE term_id=? AND is_deleted = 0""",
            (
                existing["term_name"],
                existing["start_date"],
                existing["end_date"],
                existing["activity_status"],
                existing["term_img_url"],
                term_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, term_id: int) -> bool:
        """Soft delete a term by setting is_deleted = 1."""
        logger.debug("Soft-deleting term: id=%s", term_id)
        existing = self.get_by_id(term_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE terms SET is_deleted = 1 WHERE term_id = ?",
            (term_id,),
        )
        self.commit()
        logger.trace("Term soft-deleted in DB: id=%s", term_id)
        return True

    def exists(self, term_id: int) -> bool:
        """Check if a term exists (not soft-deleted)."""
        logger.trace("Checking if term exists: id=%s", term_id)
        result = self.get_by_id(term_id) is not None
        logger.trace("Term exists check result: id=%s → %s", term_id, result)
        return result

    def count_active_classes_in_term(self, term_id: int) -> int:
        """Count active classes assigned to a term."""
        logger.trace("Counting active classes for term id=%s", term_id)
        self.cursor.execute(
            """SELECT COUNT(*) as count FROM class_terms ct
               JOIN classes c ON ct.class_id = c.class_id
               WHERE ct.term_id = ? AND c.is_deleted = 0""",
            (term_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active classes count for term id=%s: %d", term_id, count)
        return count

    def assign_class_to_term(self, class_id: int, term_id: int) -> bool:
        """Assign a class to a term."""
        logger.debug("Assigning class id=%s to term id=%s", class_id, term_id)
        try:
            self.cursor.execute(
                """INSERT OR IGNORE INTO class_terms (class_id, term_id) 
                   VALUES (?, ?)""",
                (class_id, term_id),
            )
            self.commit()
            logger.trace("Class assigned to term: class_id=%s, term_id=%s", class_id, term_id)
            return True
        except Exception as e:
            logger.error("Error assigning class to term: %s", str(e))
            return False

    def unassign_class_from_term(self, class_id: int, term_id: int) -> bool:
        """Unassign a class from a term."""
        logger.debug("Unassigning class id=%s from term id=%s", class_id, term_id)
        try:
            self.cursor.execute(
                "DELETE FROM class_terms WHERE class_id = ? AND term_id = ?",
                (class_id, term_id),
            )
            self.commit()
            logger.trace("Class unassigned from term: class_id=%s, term_id=%s", class_id, term_id)
            return True
        except Exception as e:
            logger.error("Error unassigning class from term: %s", str(e))
            return False

    def get_classes_by_term(self, term_id: int) -> list[dict]:
        """Get all classes assigned to a term."""
        logger.trace("Getting classes for term id=%s", term_id)
        self.cursor.execute(
            """SELECT c.* FROM classes c
               JOIN class_terms ct ON c.class_id = ct.class_id
               WHERE ct.term_id = ? AND c.is_deleted = 0""",
            (term_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_terms_by_class(self, class_id: int) -> list[dict]:
        """Get all terms assigned to a class."""
        logger.trace("Getting terms for class id=%s", class_id)
        self.cursor.execute(
            """SELECT t.* FROM terms t
               JOIN class_terms ct ON t.term_id = ct.term_id
               WHERE ct.class_id = ? AND t.is_deleted = 0""",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]
