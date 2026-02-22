"""Repository layer for School entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class SchoolRepository(BaseRepository):
    """Repository for School database operations."""

    def create(
        self,
        school_name: str,
        address: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        director_name: Optional[str] = None,
        license_number: Optional[str] = None,
        capacity: Optional[int] = None,
        active_term_id: Optional[int] = None,
    ) -> dict:
        """Create a new school record."""
        logger.debug("Inserting school record: %s", school_name)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO schools 
               (school_name, address, phone, email, director_name, license_number, capacity, active_term_id, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (school_name, address, phone, email, director_name, license_number, capacity, active_term_id, created_date),
        )
        self.commit()
        logger.trace("School record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "school_id": self.cursor.lastrowid,
            "school_name": school_name,
            "address": address,
            "phone": phone,
            "email": email,
            "director_name": director_name,
            "license_number": license_number,
            "capacity": capacity,
            "active_term_id": active_term_id,
            "created_date": created_date,
        }

    def get_by_id(self, school_id: int) -> Optional[dict]:
        """Get a school by ID (excluding soft-deleted)."""
        logger.trace("SELECT school by id=%s", school_id)
        self.cursor.execute(
            "SELECT * FROM schools WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all schools (excluding soft-deleted)."""
        logger.trace("SELECT all schools")
        self.cursor.execute("SELECT * FROM schools WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, school_id: int, **kwargs) -> Optional[dict]:
        """Update a school record."""
        logger.debug("Updating school record: id=%s, fields=%s", school_id, list(kwargs.keys()))
        existing = self.get_by_id(school_id)
        if not existing:
            return None

        for key, value in kwargs.items():
            if key in existing and value is not None:
                existing[key] = value

        self.cursor.execute(
            """UPDATE schools 
               SET school_name=?, address=?, phone=?, email=?, director_name=?, license_number=?, capacity=?, active_term_id=? 
               WHERE school_id=? AND is_deleted = 0""",
            (
                existing["school_name"],
                existing["address"],
                existing["phone"],
                existing["email"],
                existing["director_name"],
                existing["license_number"],
                existing["capacity"],
                existing.get("active_term_id"),
                school_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, school_id: int) -> bool:
        """Soft delete a school by setting is_deleted = 1."""
        logger.debug("Soft-deleting school: id=%s", school_id)
        existing = self.get_by_id(school_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE schools SET is_deleted = 1 WHERE school_id = ?",
            (school_id,),
        )
        self.commit()
        logger.trace("School soft-deleted in DB: id=%s", school_id)
        return True

    def count_active_students(self, school_id: int) -> int:
        """Count active students in a school."""
        logger.trace("Counting active students for school id=%s", school_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active students count for school id=%s: %d", school_id, count)
        return count

    def count_active_teachers(self, school_id: int) -> int:
        """Count active teachers in a school."""
        logger.trace("Counting active teachers for school id=%s", school_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM teachers WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active teachers count for school id=%s: %d", school_id, count)
        return count

    def count_active_parents(self, school_id: int) -> int:
        """Count active parents in a school."""
        logger.trace("Counting active parents for school id=%s", school_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM parents WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active parents count for school id=%s: %d", school_id, count)
        return count

    def count_active_classes(self, school_id: int) -> int:
        """Count active classes in a school."""
        logger.trace("Counting active classes for school id=%s", school_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM classes WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active classes count for school id=%s: %d", school_id, count)
        return count

    def exists(self, school_id: int) -> bool:
        """Check if a school exists (not soft-deleted)."""
        logger.trace("Checking if school exists: id=%s", school_id)
        result = self.get_by_id(school_id) is not None
        logger.trace("School exists check result: id=%s → %s", school_id, result)
        return result

    def get_school_stats(self, school_id: int) -> dict:
        """Get statistics for a school (total students, teachers, classes, parents)."""
        logger.debug("Fetching school stats for id=%s", school_id)
        if not self.exists(school_id):
            logger.warning("School not found for stats: id=%s", school_id)
            return {}

        # Count students
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        total_students = self.cursor.fetchone()["count"]

        # Count teachers
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM teachers WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        total_teachers = self.cursor.fetchone()["count"]

        # Count classes
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM classes WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        total_classes = self.cursor.fetchone()["count"]

        # Count parents
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM parents WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        total_parents = self.cursor.fetchone()["count"]

        stats = {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classes": total_classes,
            "total_parents": total_parents,
        }
        logger.debug("School stats for id=%s: %s", school_id, stats)
        return stats

    def get_current_student_count(self, school_id: int) -> int:
        """Get the current number of students in a school."""
        logger.trace("Getting current student count for school id=%s", school_id)
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Current student count for school id=%s: %d", school_id, count)
        return count

    def get_capacity(self, school_id: int) -> Optional[int]:
        """Get the capacity of a school."""
        logger.trace("Getting capacity for school id=%s", school_id)
        school_data = self.get_by_id(school_id)
        if not school_data:
            logger.trace("School not found for capacity lookup: id=%s", school_id)
            return None
        capacity = school_data.get("capacity")
        logger.trace("School id=%s capacity: %s", school_id, capacity)
        return capacity
        
    def check_capacity_available(self, school_id: int, additional_students: int = 1) -> tuple[bool, Optional[str]]:
        """Check if school has capacity for additional students."""
        logger.debug("Checking capacity for school id=%s (adding %d)", school_id, additional_students)
        school_data = self.get_by_id(school_id)
        if not school_data:
            logger.warning("School not found for capacity check: id=%s", school_id)
            return False, "School not found"
        
        capacity = school_data.get("capacity")
        if capacity is None:
            # No capacity limit set, allow unlimited students
            logger.trace("School id=%s has no capacity limit — allowing", school_id)
            return True, None
        
        current_count = self.get_current_student_count(school_id)
        if current_count + additional_students > capacity:
            msg = f"School capacity exceeded. Current: {current_count}, Capacity: {capacity}, Trying to add: {additional_students}"
            logger.warning("School capacity check failed for id=%s: %s", school_id, msg)
            return False, msg
        
        logger.trace("School capacity check passed for id=%s: %d/%d", school_id, current_count, capacity)
        return True, None