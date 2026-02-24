"""Repository layer for Student entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class StudentRepository(BaseRepository):
    """Repository for Student database operations."""

    def create(
        self,
        first_name: str,
        last_name: str,
        school_id: int,
        student_photo: Optional[str],
        date_of_birth: Optional[str],
    ) -> dict:
        """Create a new student record."""
        logger.debug("Inserting student record: %s %s", first_name, last_name)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO students 
               (first_name, last_name, school_id, student_photo, date_of_birth, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, school_id, student_photo, date_of_birth, created_date),
        )
        self.commit()
        logger.trace("Student record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "student_id": self.cursor.lastrowid,
            "first_name": first_name,
            "last_name": last_name,
            "school_id": school_id,
            "student_photo": student_photo,
            "date_of_birth": date_of_birth,
            "created_date": created_date,
        }

    def get_by_id(self, student_id: int) -> Optional[dict]:
        """Get a student by ID (excluding soft-deleted)."""
        logger.trace("SELECT student by id=%s", student_id)
        self.cursor.execute(
            "SELECT * FROM students WHERE student_id = ? AND is_deleted = 0",
            (student_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self, search: Optional[str] = None) -> list[dict]:
        """Get all students (excluding soft-deleted), sorted by first_name, last_name, student_id."""
        logger.trace("SELECT all students")
        query, params = self._build_search_query(search)
        self.cursor.execute(
            f"{query} ORDER BY first_name, last_name, student_id",
            params,
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_paginated(
        self, page: int = 1, page_size: int = 10, search: Optional[str] = None
    ) -> tuple[list[dict], int]:
        """Get paginated students (excluding soft-deleted), sorted by first_name, last_name, student_id."""
        logger.debug("Fetching paginated students: page=%d, page_size=%d", page, page_size)
        query, params = self._build_search_query(search)
        query = f"{query} ORDER BY first_name, last_name, student_id"
        results, total = self.paginate(query, params, page, page_size)
        logger.info("Retrieved %d students out of %d total", len(results), total)
        return results, total

    def _build_search_query(self, search: Optional[str]) -> tuple[str, tuple]:
        """Build search query for students by first and last name."""
        base_query = "SELECT * FROM students WHERE is_deleted = 0"
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

    def get_by_class_id(self, class_id: int) -> list[dict]:
        """Get all students enrolled in a class (excluding soft-deleted)."""
        logger.trace("SELECT students by class_id=%s via student_classes", class_id)
        self.cursor.execute(
            """SELECT s.* FROM students s
               JOIN student_classes sc ON sc.student_id = s.student_id
               WHERE sc.class_id = ? AND s.is_deleted = 0""",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, student_id: int, **kwargs) -> Optional[dict]:
        """Update a student record (basic fields only; class enrollments managed separately)."""
        logger.debug("Updating student record: id=%s, fields=%s", student_id, list(kwargs.keys()))
        existing = self.get_by_id(student_id)
        if not existing:
            return None

        for key in ("first_name", "last_name", "school_id", "student_photo", "date_of_birth"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE students 
               SET first_name=?, last_name=?, school_id=?, student_photo=?, date_of_birth=? 
               WHERE student_id=? AND is_deleted = 0""",
            (
                existing["first_name"],
                existing["last_name"],
                existing["school_id"],
                existing["student_photo"],
                existing["date_of_birth"],
                student_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, student_id: int) -> bool:
        """Soft delete a student by setting is_deleted = 1."""
        logger.debug("Soft-deleting student: id=%s", student_id)
        existing = self.get_by_id(student_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE students SET is_deleted = 1 WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
        logger.trace("Student soft-deleted in DB: id=%s", student_id)
        return True

    def exists(self, student_id: int) -> bool:
        """Check if a student exists (not soft-deleted)."""
        logger.trace("Checking if student exists: id=%s", student_id)
        result = self.get_by_id(student_id) is not None
        logger.trace("Student exists check result: id=%s → %s", student_id, result)
        return result

    # --- Class enrollments ---

    def enroll_in_class(self, student_id: int, class_id: int):
        """Enroll a student in a class (idempotent)."""
        logger.debug("Enrolling student id=%s in class id=%s", student_id, class_id)
        self.cursor.execute(
            "INSERT OR IGNORE INTO student_classes (student_id, class_id) VALUES (?, ?)",
            (student_id, class_id),
        )
        self.commit()
        logger.trace("Enrollment recorded: student_id=%s, class_id=%s", student_id, class_id)

    def unenroll_from_class(self, student_id: int, class_id: int):
        """Remove a student from a specific class."""
        logger.debug("Unenrolling student id=%s from class id=%s", student_id, class_id)
        self.cursor.execute(
            "DELETE FROM student_classes WHERE student_id = ? AND class_id = ?",
            (student_id, class_id),
        )
        self.commit()
        logger.trace("Enrollment removed: student_id=%s, class_id=%s", student_id, class_id)

    def unenroll_from_all_classes(self, student_id: int):
        """Remove a student from all classes."""
        logger.debug("Unenrolling student id=%s from all classes", student_id)
        self.cursor.execute(
            "DELETE FROM student_classes WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
        logger.trace("All class enrollments removed for student id=%s", student_id)

    def get_class_ids(self, student_id: int) -> list[int]:
        """Get all class IDs a student is enrolled in (active classes only)."""
        logger.trace("Fetching class IDs for student id=%s", student_id)
        self.cursor.execute(
            """SELECT sc.class_id FROM student_classes sc
               JOIN classes c ON sc.class_id = c.class_id
               WHERE sc.student_id = ? AND c.is_deleted = 0""",
            (student_id,),
        )
        class_ids = [row["class_id"] for row in self.cursor.fetchall()]
        logger.trace("Class IDs for student id=%s: %s", student_id, class_ids)
        return class_ids

    def is_enrolled_in_class(self, student_id: int, class_id: int) -> bool:
        """Check whether a student is already enrolled in a given class."""
        logger.trace("Checking enrollment: student_id=%s, class_id=%s", student_id, class_id)
        self.cursor.execute(
            "SELECT 1 FROM student_classes WHERE student_id = ? AND class_id = ?",
            (student_id, class_id),
        )
        result = self.cursor.fetchone() is not None
        logger.trace("Enrollment check result: student_id=%s, class_id=%s → %s", student_id, class_id, result)
        return result

    # --- Parent links ---

    def link_parent(self, student_id: int, parent_id: int):
        """Link a parent to a student."""
        logger.debug("Linking parent id=%s to student id=%s", parent_id, student_id)
        self.cursor.execute(
            "INSERT OR IGNORE INTO student_parents (student_id, parent_id) VALUES (?, ?)",
            (student_id, parent_id),
        )
        self.commit()
        logger.trace("Parent-student link created: parent_id=%s, student_id=%s", parent_id, student_id)

    def unlink_all_parents(self, student_id: int):
        """Remove all parent links for a student."""
        logger.debug("Unlinking all parents from student id=%s", student_id)
        self.cursor.execute(
            "DELETE FROM student_parents WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
        logger.trace("All parent links removed for student id=%s", student_id)

    def get_parent_ids(self, student_id: int) -> list[int]:
        """Get all parent IDs for a student."""
        logger.trace("Fetching parent IDs for student id=%s", student_id)
        self.cursor.execute(
            """SELECT sp.parent_id FROM student_parents sp
               JOIN parents p ON sp.parent_id = p.parent_id
               WHERE sp.student_id = ? AND p.is_deleted = 0""",
            (student_id,),
        )
        parent_ids = [row["parent_id"] for row in self.cursor.fetchall()]
        logger.trace("Parent IDs for student id=%s: %s", student_id, parent_ids)
        return parent_ids

    # --- Allergies ---

    def add_allergy(
        self,
        student_id: int,
        allergy_name: str,
        severity: Optional[str],
        notes: Optional[str],
    ) -> dict:
        """Add an allergy record for a student."""
        logger.debug("Inserting allergy record '%s' for student id=%s", allergy_name, student_id)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO student_allergies 
               (student_id, allergy_name, severity, notes, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, 0)""",
            (student_id, allergy_name, severity, notes, created_date),
        )
        self.commit()
        logger.trace("Allergy record inserted with rowid=%s for student id=%s", self.cursor.lastrowid, student_id)
        return {
            "allergy_id": self.cursor.lastrowid,
            "student_id": student_id,
            "allergy_name": allergy_name,
            "severity": severity,
            "notes": notes,
            "created_date": created_date,
        }

    def get_allergies(self, student_id: int) -> list[dict]:
        """Get all allergies for a student (excluding soft-deleted)."""
        logger.trace("SELECT allergies for student id=%s", student_id)
        self.cursor.execute(
            "SELECT * FROM student_allergies WHERE student_id = ? AND is_deleted = 0",
            (student_id,),
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.trace("Found %d allergy record(s) for student id=%s", len(results), student_id)
        return results

    def get_allergy(self, student_id: int, allergy_id: int) -> Optional[dict]:
        """Get a specific allergy record."""
        logger.trace("SELECT allergy id=%s for student id=%s", allergy_id, student_id)
        self.cursor.execute(
            "SELECT * FROM student_allergies WHERE allergy_id = ? AND student_id = ? AND is_deleted = 0",
            (allergy_id, student_id),
        )
        row = self.cursor.fetchone()
        if not row:
            logger.trace("Allergy not found: allergy_id=%s, student_id=%s", allergy_id, student_id)
        return dict(row) if row else None

    def soft_delete_allergy(self, allergy_id: int) -> bool:
        """Soft delete an allergy record."""
        logger.debug("Soft-deleting allergy: id=%s", allergy_id)
        self.cursor.execute(
            "UPDATE student_allergies SET is_deleted = 1 WHERE allergy_id = ?",
            (allergy_id,),
        )
        self.commit()
        deleted = self.cursor.rowcount > 0
        logger.trace("Allergy soft-delete result: id=%s → %s", allergy_id, deleted)
        return deleted

    def soft_delete_all_allergies(self, student_id: int):
        """Soft delete all allergies for a student."""
        logger.debug("Soft-deleting all allergies for student id=%s", student_id)
        self.cursor.execute(
            "UPDATE student_allergies SET is_deleted = 1 WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
        logger.trace("All allergies soft-deleted for student id=%s (rows affected: %d)", student_id, self.cursor.rowcount)

    # --- HW Info ---

    def add_hw_info(
        self,
        student_id: int,
        height: float,
        weight: float,
        measurement_date: str,
    ) -> dict:
        """Add a height/weight record for a student."""
        logger.debug("Inserting HW info for student id=%s (height=%s, weight=%s)", student_id, height, weight)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO student_hw_info 
               (student_id, height, weight, measurement_date, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, 0)""",
            (student_id, height, weight, measurement_date, created_date),
        )
        self.commit()
        logger.trace("HW info record inserted with rowid=%s for student id=%s", self.cursor.lastrowid, student_id)
        return {
            "hw_id": self.cursor.lastrowid,
            "student_id": student_id,
            "height": height,
            "weight": weight,
            "measurement_date": measurement_date,
            "created_date": created_date,
        }

    def get_hw_info(self, student_id: int) -> list[dict]:
        """Get all HW info for a student (excluding soft-deleted)."""
        logger.trace("SELECT HW info for student id=%s", student_id)
        self.cursor.execute(
            "SELECT * FROM student_hw_info WHERE student_id = ? AND is_deleted = 0",
            (student_id,),
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.trace("Found %d HW info record(s) for student id=%s", len(results), student_id)
        return results

    def get_hw_record(self, student_id: int, hw_id: int) -> Optional[dict]:
        """Get a specific HW info record."""
        logger.trace("SELECT HW info id=%s for student id=%s", hw_id, student_id)
        self.cursor.execute(
            "SELECT * FROM student_hw_info WHERE hw_id = ? AND student_id = ? AND is_deleted = 0",
            (hw_id, student_id),
        )
        row = self.cursor.fetchone()
        if not row:
            logger.trace("HW info not found: hw_id=%s, student_id=%s", hw_id, student_id)
        return dict(row) if row else None

    def soft_delete_hw_info(self, hw_id: int) -> bool:
        """Soft delete an HW info record."""
        logger.debug("Soft-deleting HW info: id=%s", hw_id)
        self.cursor.execute(
            "UPDATE student_hw_info SET is_deleted = 1 WHERE hw_id = ?",
            (hw_id,),
        )
        self.commit()
        deleted = self.cursor.rowcount > 0
        logger.trace("HW info soft-delete result: id=%s → %s", hw_id, deleted)
        return deleted

    def soft_delete_all_hw_info(self, student_id: int):
        """Soft delete all HW info for a student."""
        logger.debug("Soft-deleting all HW info for student id=%s", student_id)
        self.cursor.execute(
            "UPDATE student_hw_info SET is_deleted = 1 WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
        logger.trace("All HW info soft-deleted for student id=%s (rows affected: %d)", student_id, self.cursor.rowcount)
