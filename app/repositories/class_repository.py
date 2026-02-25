"""Repository layer for Class entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class ClassRepository(BaseRepository):
    """Repository for Class database operations."""

    def create(
        self,
        class_name: str,
        school_id: int,
        capacity: Optional[int],
    ) -> dict:
        """Create a new class record."""
        logger.debug("Inserting class record: %s (school_id=%s)", class_name, school_id)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO classes 
               (class_name, school_id, capacity, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, 0)""",
            (class_name, school_id, capacity, created_date),
        )
        self.commit()
        logger.trace("Class record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "class_id": self.cursor.lastrowid,
            "class_name": class_name,
            "school_id": school_id,
            "capacity": capacity,
            "created_date": created_date,
        }

    def get_by_id(self, class_id: int) -> Optional[dict]:
        """Get a class by ID (excluding soft-deleted)."""
        logger.trace("SELECT class by id=%s", class_id)
        self.cursor.execute(
            "SELECT * FROM classes WHERE class_id = ? AND is_deleted = 0",
            (class_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_all(self, search: Optional[str] = None) -> list[dict]:
        """Get all classes (excluding soft-deleted), sorted by class_name, class_id."""
        logger.trace("SELECT all classes")
        query, params = self._build_search_query(search)
        self.cursor.execute(
            f"{query} ORDER BY class_name, class_id",
            params,
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_all_paginated(
        self, page: int = 1, page_size: int = 10, search: Optional[str] = None
    ) -> tuple[list[dict], int]:
        """Get paginated classes (excluding soft-deleted), sorted by class_name, class_id."""
        logger.debug("Fetching paginated classes: page=%d, page_size=%d", page, page_size)
        query, params = self._build_search_query(search)
        query = f"{query} ORDER BY class_name, class_id"
        results, total = self.paginate(query, params, page, page_size)
        logger.info("Retrieved %d classes out of %d total", len(results), total)
        return results, total

    def _build_search_query(self, search: Optional[str]) -> tuple[str, tuple]:
        """Build search query for classes by name."""
        base_query = "SELECT * FROM classes WHERE is_deleted = 0"
        if not search:
            return base_query, ()

        terms = [term.strip() for term in search.split() if term.strip()]
        if not terms:
            return base_query, ()

        like_clauses = []
        params: list[str] = []
        for term in terms:
            like_clauses.append("class_name LIKE ?")
            params.append(f"%{term}%")

        where_clause = " AND ".join(like_clauses)
        return f"{base_query} AND {where_clause}", tuple(params)

    def update(self, class_id: int, **kwargs) -> Optional[dict]:
        """Update a class record."""
        logger.debug("Updating class record: id=%s, fields=%s", class_id, list(kwargs.keys()))
        existing = self.get_by_id(class_id)
        if not existing:
            return None

        for key in ("class_name", "school_id", "capacity"):
            if key in kwargs and kwargs[key] is not None:
                existing[key] = kwargs[key]

        self.cursor.execute(
            """UPDATE classes 
               SET class_name=?, school_id=?, capacity=? 
               WHERE class_id=? AND is_deleted = 0""",
            (existing["class_name"], existing["school_id"], existing["capacity"], class_id),
        )
        self.commit()
        return existing

    def soft_delete(self, class_id: int) -> bool:
        """Soft delete a class by setting is_deleted = 1."""
        logger.debug("Soft-deleting class: id=%s", class_id)
        existing = self.get_by_id(class_id)
        if not existing:
            return False

        self.cursor.execute(
            "UPDATE classes SET is_deleted = 1 WHERE class_id = ?",
            (class_id,),
        )
        self.commit()
        logger.trace("Class soft-deleted in DB: id=%s", class_id)
        return True

    def count_active_students(self, class_id: int) -> int:
        """Count active students enrolled in a class."""
        logger.trace("Counting active students for class id=%s", class_id)
        self.cursor.execute(
            """SELECT COUNT(*) as count FROM student_classes sc
               JOIN students s ON sc.student_id = s.student_id
               WHERE sc.class_id = ? AND s.is_deleted = 0""",
            (class_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active students count for class id=%s: %d", class_id, count)
        return count

    def exists(self, class_id: int) -> bool:
        """Check if a class exists (not soft-deleted)."""
        logger.trace("Checking if class exists: id=%s", class_id)
        result = self.get_by_id(class_id) is not None
        logger.trace("Class exists check result: id=%s → %s", class_id, result)
        return result

    def count_active_teachers(self, class_id: int) -> int:
        """Count active teachers assigned to a class."""
        logger.trace("Counting active teachers for class id=%s", class_id)
        self.cursor.execute(
            """SELECT COUNT(*) as count FROM teacher_classes tc
               JOIN users u ON tc.user_id = u.user_id
               WHERE tc.class_id = ? AND u.is_deleted = 0 AND u.role = 'TEACHER'""",
            (class_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Active teachers count for class id=%s: %d", class_id, count)
        return count

    def get_current_student_count(self, class_id: int) -> int:
        """Get the current number of active students enrolled in a class."""
        logger.trace("Getting current student count for class id=%s", class_id)
        self.cursor.execute(
            """SELECT COUNT(*) as count FROM student_classes sc
               JOIN students s ON sc.student_id = s.student_id
               WHERE sc.class_id = ? AND s.is_deleted = 0""",
            (class_id,),
        )
        count = self.cursor.fetchone()["count"]
        logger.trace("Current student count for class id=%s: %d", class_id, count)
        return count

    def check_capacity_available(self, class_id: int, additional_students: int = 1) -> tuple[bool, Optional[str]]:
        """Check if class has capacity for additional students."""
        logger.debug("Checking capacity for class id=%s (adding %d)", class_id, additional_students)
        class_data = self.get_by_id(class_id)
        if not class_data:
            logger.warning("Class not found for capacity check: id=%s", class_id)
            return False, "Class not found"
        
        capacity = class_data.get("capacity")
        if capacity is None:
            # No capacity limit set, allow unlimited students
            logger.trace("Class id=%s has no capacity limit — allowing", class_id)
            return True, None
        
        current_count = self.get_current_student_count(class_id)
        if current_count + additional_students > capacity:
            msg = f"Class capacity exceeded. Current: {current_count}, Capacity: {capacity}, Trying to add: {additional_students}"
            logger.warning("Class capacity check failed for id=%s: %s", class_id, msg)
            return False, msg
        
        logger.trace("Class capacity check passed for id=%s: %d/%d", class_id, current_count, capacity)
        return True, None

    # --- Attendance methods ---

    def get_students_without_attendance(self, class_id: int, attendance_date: str) -> list[dict]:
        """Get students in class who don't have attendance recorded for the given date."""
        logger.debug("Fetching students without attendance for class_id=%s on date=%s", class_id, attendance_date)
        self.cursor.execute(
            """
            SELECT s.* FROM students s
            JOIN student_classes sc ON s.student_id = sc.student_id
            WHERE sc.class_id = ? 
              AND s.is_deleted = 0
              AND NOT EXISTS (
                  SELECT 1 FROM attendance a 
                  WHERE a.student_id = s.student_id 
                    AND a.class_id = ? 
                    AND a.attendance_date = ?
                    AND a.is_deleted = 0
              )
            ORDER BY s.first_name, s.last_name, s.student_id
            """,
            (class_id, class_id, attendance_date),
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.info("Found %d students without attendance for class_id=%s on date=%s", len(results), class_id, attendance_date)
        return results

    def record_attendance(
        self, 
        class_id: int, 
        student_id: int, 
        attendance_date: str, 
        status: str = "present",
        recorded_by: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """Record attendance for a student on a specific date."""
        logger.debug("Recording attendance: class_id=%s, student_id=%s, date=%s, status=%s", 
                     class_id, student_id, attendance_date, status)
        recorded_at = get_current_datetime()
        
        # Use INSERT OR REPLACE to handle both new records and updates
        self.cursor.execute(
            """
            INSERT INTO attendance (class_id, student_id, attendance_date, status, recorded_by, recorded_at, notes, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(class_id, student_id, attendance_date) 
            DO UPDATE SET 
                status = excluded.status,
                recorded_by = excluded.recorded_by,
                recorded_at = excluded.recorded_at,
                notes = excluded.notes,
                is_deleted = 0
            """,
            (class_id, student_id, attendance_date, status, recorded_by, recorded_at, notes),
        )
        self.commit()
        
        # Get the attendance_id
        self.cursor.execute(
            "SELECT attendance_id FROM attendance WHERE class_id = ? AND student_id = ? AND attendance_date = ?",
            (class_id, student_id, attendance_date),
        )
        attendance_id = self.cursor.fetchone()["attendance_id"]
        
        logger.info("Attendance recorded: attendance_id=%s for student_id=%s on date=%s", 
                    attendance_id, student_id, attendance_date)
        return {
            "attendance_id": attendance_id,
            "class_id": class_id,
            "student_id": student_id,
            "attendance_date": attendance_date,
            "status": status,
            "recorded_by": recorded_by,
            "recorded_at": recorded_at,
            "notes": notes,
        }

    def get_attendance_for_date(self, class_id: int, attendance_date: str) -> list[dict]:
        """Get all attendance records for a class on a specific date."""
        logger.debug("Fetching attendance for class_id=%s on date=%s", class_id, attendance_date)
        self.cursor.execute(
            """
            SELECT a.*, s.first_name, s.last_name 
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.class_id = ? 
              AND a.attendance_date = ?
              AND a.is_deleted = 0
              AND s.is_deleted = 0
            ORDER BY s.first_name, s.last_name, s.student_id
            """,
            (class_id, attendance_date),
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.info("Found %d attendance records for class_id=%s on date=%s", len(results), class_id, attendance_date)
        return results

    def bulk_record_attendance(
        self,
        class_id: int,
        attendance_date: str,
        entries: list[dict],
        recorded_by: Optional[int] = None,
    ) -> list[dict]:
        """
        Record attendance for multiple students at once.
        
        Each entry should have: student_id, status, and optionally notes.
        Uses INSERT OR REPLACE so existing records for the same
        (class_id, student_id, attendance_date) are updated.
        
        Returns a list of attendance record dicts.
        """
        logger.debug(
            "Bulk recording attendance for class_id=%s on date=%s (%d entries)",
            class_id, attendance_date, len(entries),
        )
        recorded_at = get_current_datetime()
        results: list[dict] = []

        for entry in entries:
            student_id = entry["student_id"]
            status = entry.get("status", "present")
            notes = entry.get("notes")

            self.cursor.execute(
                """
                INSERT INTO attendance (class_id, student_id, attendance_date, status, recorded_by, recorded_at, notes, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(class_id, student_id, attendance_date)
                DO UPDATE SET
                    status = excluded.status,
                    recorded_by = excluded.recorded_by,
                    recorded_at = excluded.recorded_at,
                    notes = excluded.notes,
                    is_deleted = 0
                """,
                (class_id, student_id, attendance_date, status, recorded_by, recorded_at, notes),
            )

            # Fetch the attendance_id
            self.cursor.execute(
                "SELECT attendance_id FROM attendance WHERE class_id = ? AND student_id = ? AND attendance_date = ?",
                (class_id, student_id, attendance_date),
            )
            attendance_id = self.cursor.fetchone()["attendance_id"]

            results.append({
                "attendance_id": attendance_id,
                "class_id": class_id,
                "student_id": student_id,
                "attendance_date": attendance_date,
                "status": status,
                "recorded_by": recorded_by,
                "recorded_at": recorded_at,
                "notes": notes,
            })

        self.commit()
        logger.info(
            "Bulk attendance recorded: %d records for class_id=%s on date=%s",
            len(results), class_id, attendance_date,
        )
        return results

    def get_attendance_history(self, class_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list[dict]:
        """Get attendance history for a class with optional date range."""
        logger.debug("Fetching attendance history for class_id=%s from %s to %s", class_id, start_date, end_date)
        
        query = """
            SELECT a.*, s.first_name, s.last_name 
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.class_id = ? 
              AND a.is_deleted = 0
              AND s.is_deleted = 0
        """
        params: list = [class_id]
        
        if start_date:
            query += " AND a.attendance_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND a.attendance_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY a.attendance_date DESC, s.first_name, s.last_name, s.student_id"
        
        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.info("Found %d attendance history records for class_id=%s", len(results), class_id)
        return results

    # --- Event methods ---

    def create_event(
        self,
        class_id: int,
        title: str,
        description: Optional[str],
        photo_url: Optional[str],
        event_date: str,
        created_by: int,
    ) -> dict:
        """Create a new class event."""
        logger.debug("Inserting class event: %s for class_id=%s on date=%s", title, class_id, event_date)
        now = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO class_events
               (class_id, title, description, photo_url, event_date, created_by, created_at, updated_at, is_deleted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (class_id, title, description, photo_url, event_date, created_by, now, now),
        )
        self.commit()
        event_id = self.cursor.lastrowid
        logger.info("Class event created: event_id=%s for class_id=%s", event_id, class_id)
        return {
            "event_id": event_id,
            "class_id": class_id,
            "title": title,
            "description": description,
            "photo_url": photo_url,
            "event_date": event_date,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now,
        }

    def get_event_by_id(self, event_id: int) -> Optional[dict]:
        """Get a class event by ID (excluding soft-deleted)."""
        logger.trace("SELECT class event by id=%s", event_id)
        self.cursor.execute(
            "SELECT * FROM class_events WHERE event_id = ? AND is_deleted = 0",
            (event_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_events_by_class_id(self, class_id: int) -> list[dict]:
        """Get all events for a class (excluding soft-deleted), ordered by newest first."""
        logger.debug("Fetching events for class_id=%s", class_id)
        self.cursor.execute(
            """SELECT * FROM class_events
               WHERE class_id = ? AND is_deleted = 0
               ORDER BY created_at DESC""",
            (class_id,),
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.info("Retrieved %d event(s) for class_id=%s", len(results), class_id)
        return results

    def update_event(
        self,
        event_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        photo_url: Optional[str] = None,
        event_date: Optional[str] = None,
    ) -> Optional[dict]:
        """Update a class event."""
        logger.debug("Updating event: id=%s", event_id)
        existing = self.get_event_by_id(event_id)
        if not existing:
            logger.warning("Event not found for update: id=%s", event_id)
            return None

        # Update only provided fields
        if title is not None:
            existing["title"] = title
        if description is not None:
            existing["description"] = description
        if photo_url is not None:
            existing["photo_url"] = photo_url
        if event_date is not None:
            existing["event_date"] = event_date

        now = get_current_datetime()
        existing["updated_at"] = now

        self.cursor.execute(
            """UPDATE class_events
               SET title=?, description=?, photo_url=?, event_date=?, updated_at=?
               WHERE event_id=? AND is_deleted = 0""",
            (existing["title"], existing["description"], existing["photo_url"], existing["event_date"], now, event_id),
        )
        self.commit()
        logger.info("Event updated: id=%s", event_id)
        return existing

    def soft_delete_event(self, event_id: int) -> bool:
        """Soft delete a class event."""
        logger.debug("Soft-deleting event: id=%s", event_id)
        existing = self.get_event_by_id(event_id)
        if not existing:
            logger.warning("Event not found for deletion: id=%s", event_id)
            return False

        now = get_current_datetime()
        self.cursor.execute(
            "UPDATE class_events SET is_deleted = 1, updated_at = ? WHERE event_id = ?",
            (now, event_id),
        )
        self.commit()
        logger.info("Event soft-deleted: id=%s", event_id)
        return True
