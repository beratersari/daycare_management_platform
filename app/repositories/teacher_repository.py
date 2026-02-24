"""Repository layer for Teacher entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


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
        logger.debug("Inserting teacher record: %s %s", first_name, last_name)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO teachers 
               (first_name, last_name, school_id, class_id, email, phone, address, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, school_id, class_id, email, phone, address, created_date),
        )
        self.commit()
        logger.trace("Teacher record inserted with rowid=%s", self.cursor.lastrowid)
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
        logger.trace("SELECT teacher by id=%s", teacher_id)
        self.cursor.execute(
            "SELECT * FROM teachers WHERE teacher_id = ? AND is_deleted = 0",
            (teacher_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self, search: Optional[str] = None) -> list[dict]:
        """Get all teachers (excluding soft-deleted), sorted by first_name, last_name, teacher_id."""
        logger.trace("SELECT all teachers")
        query, params = self._build_search_query(search)
        self.cursor.execute(
            f"{query} ORDER BY first_name, last_name, teacher_id",
            params,
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_paginated(
        self, page: int = 1, page_size: int = 10, search: Optional[str] = None
    ) -> tuple[list[dict], int]:
        """Get paginated teachers (excluding soft-deleted), sorted by first_name, last_name, teacher_id."""
        logger.debug("Fetching paginated teachers: page=%d, page_size=%d", page, page_size)
        query, params = self._build_search_query(search)
        query = f"{query} ORDER BY first_name, last_name, teacher_id"
        results, total = self.paginate(query, params, page, page_size)
        logger.info("Retrieved %d teachers out of %d total", len(results), total)
        return results, total

    def _build_search_query(self, search: Optional[str]) -> tuple[str, tuple]:
        """Build search query for teachers by first and last name."""
        base_query = "SELECT * FROM teachers WHERE is_deleted = 0"
        if not search:
            return base_query, ()

        terms = [term.strip() for term in search.split() if term.strip()]
        if not terms:
            return base_query, ()

        like_clauses = []
        params: list[str] = []
        for term in terms:
            like_clauses.append("(first_name LIKE ? OR last_name LIKE ?)")
            wildcard = f"%{term}%"
            params.extend([wildcard, wildcard])

        where_clause = " AND ".join(like_clauses)
        return f"{base_query} AND {where_clause}", tuple(params)

    def update(self, teacher_id: int, **kwargs) -> Optional[dict]:
        """Update a teacher record."""
        logger.debug("Updating teacher record: id=%s, fields=%s", teacher_id, list(kwargs.keys()))
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
        logger.debug("Soft-deleting teacher: id=%s", teacher_id)
        existing = self.get_by_id(teacher_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE teachers SET is_deleted = 1 WHERE teacher_id = ?",
            (teacher_id,),
        )
        self.commit()
        logger.trace("Teacher soft-deleted in DB: id=%s", teacher_id)
        return True

    def get_by_class_id(self, class_id: int) -> list[dict]:
        """Get all teachers in a class (excluding soft-deleted)."""
        logger.trace("SELECT teachers by class_id=%s", class_id)
        self.cursor.execute(
            "SELECT * FROM teachers WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.trace("Found %d teacher(s) for class id=%s", len(results), class_id)
        return results

    def is_assigned_to_class(self, teacher_id: int) -> bool:
        """Check if a teacher is currently assigned to a class."""
        logger.trace("Checking if teacher id=%s is assigned to a class", teacher_id)
        teacher = self.get_by_id(teacher_id)
        if not teacher:
            logger.trace("Teacher not found for class assignment check: id=%s", teacher_id)
            return False
        assigned = teacher.get("class_id") is not None
        logger.trace("Teacher id=%s assigned to class: %s", teacher_id, assigned)
        return assigned

    def exists(self, teacher_id: int) -> bool:
        """Check if a teacher exists (not soft-deleted)."""
        logger.trace("Checking if teacher exists: id=%s", teacher_id)
        result = self.get_by_id(teacher_id) is not None
        logger.trace("Teacher exists check result: id=%s → %s", teacher_id, result)
        return result
