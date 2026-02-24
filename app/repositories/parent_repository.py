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

    def get_all(self, search: Optional[str] = None) -> list[dict]:
        """Get all parents (excluding soft-deleted), sorted by first_name, last_name, parent_id."""
        logger.trace("SELECT all parents")
        query, params = self._build_search_query(search)
        self.cursor.execute(
            f"{query} ORDER BY first_name, last_name, parent_id",
            params,
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_paginated(
        self, page: int = 1, page_size: int = 10, search: Optional[str] = None
    ) -> tuple[list[dict], int]:
        """Get paginated parents (excluding soft-deleted), sorted by first_name, last_name, parent_id."""
        logger.debug("Fetching paginated parents: page=%d, page_size=%d", page, page_size)
        query, params = self._build_search_query(search)
        query = f"{query} ORDER BY first_name, last_name, parent_id"
        results, total = self.paginate(query, params, page, page_size)
        logger.info("Retrieved %d parents out of %d total", len(results), total)
        return results, total

    def _build_search_query(self, search: Optional[str]) -> tuple[str, tuple]:
        """Build search query for parents by first and last name."""
        base_query = "SELECT * FROM parents WHERE is_deleted = 0"
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
