"""Repository layer for Student entity."""
import sqlite3
from typing import Optional

from app.repositories.base_repository import BaseRepository, get_current_datetime


class StudentRepository(BaseRepository):
    """Repository for Student database operations."""

    def create(
        self,
        first_name: str,
        last_name: str,
        school_id: int,
        class_id: Optional[int],
        student_photo: Optional[str],
        date_of_birth: Optional[str],
    ) -> dict:
        """Create a new student record."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO students 
               (first_name, last_name, school_id, class_id, student_photo, date_of_birth, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (first_name, last_name, school_id, class_id, student_photo, date_of_birth, created_date),
        )
        self.commit()
        return {
            "student_id": self.cursor.lastrowid,
            "first_name": first_name,
            "last_name": last_name,
            "school_id": school_id,
            "class_id": class_id,
            "student_photo": student_photo,
            "date_of_birth": date_of_birth,
            "created_date": created_date,
        }

    def get_by_id(self, student_id: int) -> Optional[dict]:
        """Get a student by ID (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM students WHERE student_id = ? AND is_deleted = 0",
            (student_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self) -> list[dict]:
        """Get all students (excluding soft-deleted)."""
        self.cursor.execute("SELECT * FROM students WHERE is_deleted = 0")
        return [dict(row) for row in self.cursor.fetchall()]

    def get_by_class_id(self, class_id: int) -> list[dict]:
        """Get all students in a class (excluding soft-deleted)."""
        self.cursor.execute(
            "SELECT * FROM students WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def update(self, student_id: int, **kwargs) -> Optional[dict]:
        """Update a student record."""
        existing = self.get_by_id(student_id)
        if not existing:
            return None

        for key in ("first_name", "last_name", "school_id", "class_id", "student_photo", "date_of_birth"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE students 
               SET first_name=?, last_name=?, school_id=?, class_id=?, student_photo=?, date_of_birth=? 
               WHERE student_id=? AND is_deleted = 0""",
            (
                existing["first_name"],
                existing["last_name"],
                existing["school_id"],
                existing["class_id"],
                existing["student_photo"],
                existing["date_of_birth"],
                student_id,
            ),
        )
        self.commit()
        return existing

    def soft_delete(self, student_id: int) -> bool:
        """Soft delete a student by setting is_deleted = 1."""
        existing = self.get_by_id(student_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE students SET is_deleted = 1 WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
        return True

    def exists(self, student_id: int) -> bool:
        """Check if a student exists (not soft-deleted)."""
        return self.get_by_id(student_id) is not None

    # --- Parent links ---

    def link_parent(self, student_id: int, parent_id: int):
        """Link a parent to a student."""
        self.cursor.execute(
            "INSERT OR IGNORE INTO student_parents (student_id, parent_id) VALUES (?, ?)",
            (student_id, parent_id),
        )
        self.commit()

    def unlink_all_parents(self, student_id: int):
        """Remove all parent links for a student."""
        self.cursor.execute(
            "DELETE FROM student_parents WHERE student_id = ?",
            (student_id,),
        )
        self.commit()

    def get_parent_ids(self, student_id: int) -> list[int]:
        """Get all parent IDs for a student."""
        self.cursor.execute(
            """SELECT sp.parent_id FROM student_parents sp
               JOIN parents p ON sp.parent_id = p.parent_id
               WHERE sp.student_id = ? AND p.is_deleted = 0""",
            (student_id,),
        )
        return [row["parent_id"] for row in self.cursor.fetchall()]

    # --- Allergies ---

    def add_allergy(
        self,
        student_id: int,
        allergy_name: str,
        severity: Optional[str],
        notes: Optional[str],
    ) -> dict:
        """Add an allergy record for a student."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO student_allergies 
               (student_id, allergy_name, severity, notes, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, 0)""",
            (student_id, allergy_name, severity, notes, created_date),
        )
        self.commit()
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
        self.cursor.execute(
            "SELECT * FROM student_allergies WHERE student_id = ? AND is_deleted = 0",
            (student_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_allergy(self, student_id: int, allergy_id: int) -> Optional[dict]:
        """Get a specific allergy record."""
        self.cursor.execute(
            "SELECT * FROM student_allergies WHERE allergy_id = ? AND student_id = ? AND is_deleted = 0",
            (allergy_id, student_id),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def soft_delete_allergy(self, allergy_id: int) -> bool:
        """Soft delete an allergy record."""
        self.cursor.execute(
            "UPDATE student_allergies SET is_deleted = 1 WHERE allergy_id = ?",
            (allergy_id,),
        )
        self.commit()
        return self.cursor.rowcount > 0

    def soft_delete_all_allergies(self, student_id: int):
        """Soft delete all allergies for a student."""
        self.cursor.execute(
            "UPDATE student_allergies SET is_deleted = 1 WHERE student_id = ?",
            (student_id,),
        )
        self.commit()

    # --- HW Info ---

    def add_hw_info(
        self,
        student_id: int,
        height: float,
        weight: float,
        measurement_date: str,
    ) -> dict:
        """Add a height/weight record for a student."""
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO student_hw_info 
               (student_id, height, weight, measurement_date, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, 0)""",
            (student_id, height, weight, measurement_date, created_date),
        )
        self.commit()
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
        self.cursor.execute(
            "SELECT * FROM student_hw_info WHERE student_id = ? AND is_deleted = 0",
            (student_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_hw_record(self, student_id: int, hw_id: int) -> Optional[dict]:
        """Get a specific HW info record."""
        self.cursor.execute(
            "SELECT * FROM student_hw_info WHERE hw_id = ? AND student_id = ? AND is_deleted = 0",
            (hw_id, student_id),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def soft_delete_hw_info(self, hw_id: int) -> bool:
        """Soft delete an HW info record."""
        self.cursor.execute(
            "UPDATE student_hw_info SET is_deleted = 1 WHERE hw_id = ?",
            (hw_id,),
        )
        self.commit()
        return self.cursor.rowcount > 0

    def soft_delete_all_hw_info(self, student_id: int):
        """Soft delete all HW info for a student."""
        self.cursor.execute(
            "UPDATE student_hw_info SET is_deleted = 1 WHERE student_id = ?",
            (student_id,),
        )
        self.commit()
