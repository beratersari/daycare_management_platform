"""Repository layer for School entity."""
import sqlite3
from typing import Optional

from app.repositories.base_repository import BaseRepository, get_current_datetime


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
    ) -> dict:
        """Create a new school record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO schools 
               (school_name, address, phone, email, director_name, license_number, capacity, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (school_name, address, phone, email, director_name, license_number, capacity, created_date),
        )
        self.commit()
        return {
            "school_id": self.cursor.lastrowid,
            "school_name": school_name,
            "address": address,
            "phone": phone,
            "email": email,
            "director_name": director_name,
            "license_number": license_number,
            "capacity": capacity,
            "created_date": created_date,
        }

    def get_by_id(self, school_id: int) -> Optional[dict]:
        """Get a school by ID (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM schools WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all schools (excluding soft-deleted)."""
        self.cursor.execute("SELECT * FROM schools WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, school_id: int, **kwargs) -> Optional[dict]:
        """Update a school record."""
        existing = self.get_by_id(school_id)
        if not existing:
            return None

        for key, value in kwargs.items():
            if key in existing and value is not None:
                existing[key] = value

        self.cursor.execute(
            """UPDATE schools 
               SET school_name=?, address=?, phone=?, email=?, director_name=?, license_number=?, capacity=? 
               WHERE school_id=? AND is_deleted = 0""",
            (
                existing["school_name"],
                existing["address"],
                existing["phone"],
                existing["email"],
                existing["director_name"],
                existing["license_number"],
                existing["capacity"],
                school_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, school_id: int) -> bool:
        """Soft delete a school by setting is_deleted = 1."""
        existing = self.get_by_id(school_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE schools SET is_deleted = 1 WHERE school_id = ?",
            (school_id,),
        )
        self.commit()
        return True

    def count_active_students(self, school_id: int) -> int:
        """Count active students in a school."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        return self.cursor.fetchone()["count"]

    def count_active_teachers(self, school_id: int) -> int:
        """Count active teachers in a school."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM teachers WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        return self.cursor.fetchone()["count"]

    def count_active_parents(self, school_id: int) -> int:
        """Count active parents in a school."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM parents WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        return self.cursor.fetchone()["count"]

    def count_active_classes(self, school_id: int) -> int:
        """Count active classes in a school."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM classes WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        return self.cursor.fetchone()["count"]

    def exists(self, school_id: int) -> bool:
        """Check if a school exists (not soft-deleted)."""
        return self.get_by_id(school_id) is not None

    def get_school_stats(self, school_id: int) -> dict:
        """Get statistics for a school (total students, teachers, classes, parents)."""
        if not self.exists(school_id):
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

        return {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classes": total_classes,
            "total_parents": total_parents,
        }

    def get_current_student_count(self, school_id: int) -> int:
        """Get the current number of students in a school."""
        self.cursor.execute(
            "SELECT COUNT(*) as count FROM students WHERE school_id = ? AND is_deleted = 0",
            (school_id,),
        )
        return self.cursor.fetchone()["count"]

    def get_capacity(self, school_id: int) -> Optional[int]:
        """Get the capacity of a school."""
        school_data = self.get_by_id(school_id)
        if not school_data:
            return None
        return school_data.get("capacity")
        
    def check_capacity_available(self, school_id: int, additional_students: int = 1) -> tuple[bool, Optional[str]]:
        """Check if school has capacity for additional students."""
        school_data = self.get_by_id(school_id)
        if not school_data:
            return False, "School not found"
        
        capacity = school_data.get("capacity")
        if capacity is None:
            # No capacity limit set, allow unlimited students
            return True, None
        
        current_count = self.get_current_student_count(school_id)
        if current_count + additional_students > capacity:
            return False, f"School capacity exceeded. Current: {current_count}, Capacity: {capacity}, Trying to add: {additional_students}"
        
        return True, None