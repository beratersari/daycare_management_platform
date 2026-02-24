"""Service layer for Class entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.user_repository import UserRepository
from app.schemas.class_dto import ClassCreate, ClassResponse, ClassUpdate
from app.schemas.auth import UserResponse, UserRole
from app.schemas.student import AllergyResponse, HWInfoResponse, StudentResponse

logger = get_logger(__name__)


class ClassService:
    """Service for Class business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = ClassRepository(db)
        self.student_repo = StudentRepository(db)
        self.school_repo = SchoolRepository(db)
        self.user_repo = UserRepository(db)
        logger.trace("ClassService initialised")

    def create(self, data: ClassCreate) -> tuple[Optional[ClassResponse], Optional[str]]:
        """Create a new class."""
        logger.info("Creating class: %s for school_id=%s", data.class_name, data.school_id)
        logger.debug("Class creation payload: %s", data.model_dump())

        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            logger.warning("School not found during class creation: school_id=%s", data.school_id)
            return None, "School not found"
            
        # Validate class capacity doesn't exceed school capacity
        if data.capacity is not None:
            school_capacity = self.school_repo.get_capacity(data.school_id)
            if school_capacity is not None and data.capacity > school_capacity:
                logger.warning(
                    "Class capacity (%s) exceeds school capacity (%s) for school_id=%s",
                    data.capacity, school_capacity, data.school_id,
                )
                return None, f"Class capacity ({data.capacity}) cannot exceed school capacity ({school_capacity})"

        # Create class
        cls = self.repo.create(
            class_name=data.class_name,
            school_id=data.school_id,
            capacity=data.capacity,
        )

        logger.info("Class created successfully with id=%s", cls["class_id"])
        return self._build_response(cls), None

    def get_all(self, search: Optional[str] = None) -> list[ClassResponse]:
        """Get all classes."""
        logger.debug("Fetching all classes")
        classes = self.repo.get_all(search)
        logger.info("Retrieved %d class(es)", len(classes))
        return [self._build_response(c) for c in classes]

    def get_all_paginated(
        self, page: int = 1, page_size: int = 10, search: Optional[str] = None
    ) -> tuple[list[ClassResponse], int]:
        """Get paginated classes."""
        logger.debug("Fetching paginated classes: page=%d, page_size=%d", page, page_size)
        classes, total = self.repo.get_all_paginated(page, page_size, search)
        logger.info("Retrieved %d class(es) out of %d total", len(classes), total)
        return [self._build_response(c) for c in classes], total

    def get_by_id(self, class_id: int) -> Optional[ClassResponse]:
        """Get a class by ID."""
        logger.debug("Fetching class by id=%s", class_id)
        cls = self.repo.get_by_id(class_id)
        if not cls:
            logger.warning("Class not found: id=%s", class_id)
            return None
        logger.trace("Class found: %s", cls)
        return self._build_response(cls)

    def update(
        self, class_id: int, data: ClassUpdate
    ) -> tuple[Optional[ClassResponse], Optional[str]]:
        """Update a class."""
        logger.info("Updating class: id=%s", class_id)
        existing = self.repo.get_by_id(class_id)
        if not existing:
            logger.warning("Class not found for update: id=%s", class_id)
            return None, "Class not found"

        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Class update data: %s", update_data)

        # Determine which school_id to use for capacity check
        school_id = update_data.get("school_id") if "school_id" in update_data else existing["school_id"]
        
        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                logger.warning("School not found during class update: school_id=%s", update_data["school_id"])
                return None, "School not found"
        
        # Validate class capacity doesn't exceed school capacity
        if "capacity" in update_data and update_data["capacity"] is not None:
            new_capacity = update_data["capacity"]
            school_capacity = self.school_repo.get_capacity(school_id)
            if school_capacity is not None and new_capacity > school_capacity:
                logger.warning(
                    "Class capacity (%s) exceeds school capacity (%s) during update of class id=%s",
                    new_capacity, school_capacity, class_id,
                )
                return None, f"Class capacity ({new_capacity}) cannot exceed school capacity ({school_capacity})"

        # Update basic fields
        result = self.repo.update(class_id, **update_data)

        logger.info("Class updated successfully: id=%s", class_id)
        return self._build_response(result), None

    def delete(self, class_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a class if no active students or teachers exist."""
        logger.info("Attempting to delete class: id=%s", class_id)
        if not self.repo.exists(class_id):
            logger.warning("Class not found for deletion: id=%s", class_id)
            return False, "Class not found"

        # Business rule: a class cannot be deleted while it has active students or teachers
        student_count = self.repo.count_active_students(class_id)
        teacher_count = self.repo.count_active_teachers(class_id)
        logger.trace("Class id=%s has %d student(s) and %d teacher(s)", class_id, student_count, teacher_count)

        parts = []
        if student_count > 0:
            parts.append(f"{student_count} active student(s)")
        if teacher_count > 0:
            parts.append(f"{teacher_count} active teacher(s)")

        if parts:
            summary = " and ".join(parts)
            logger.warning("Cannot delete class id=%s — active dependencies: %s", class_id, summary)
            return False, f"Cannot delete class. It still has {summary}."

        self.repo.soft_delete(class_id)
        logger.info("Class soft-deleted successfully: id=%s", class_id)
        return True, None

    def exists(self, class_id: int) -> bool:
        """Check if class exists."""
        result = self.repo.exists(class_id)
        logger.trace("Class exists check: id=%s → %s", class_id, result)
        return result

    def get_capacity_info(self, class_id: int) -> Optional[dict]:
        """Get class capacity information."""
        logger.debug("Fetching capacity info for class id=%s", class_id)
        cls = self.repo.get_by_id(class_id)
        if not cls:
            logger.warning("Class not found for capacity info: id=%s", class_id)
            return None
        
        current_count = self.repo.get_current_student_count(class_id)
        capacity = cls.get("capacity")
        
        result = {
            "class_id": class_id,
            "class_name": cls["class_name"],
            "school_id": cls["school_id"],
            "current_students": current_count,
            "capacity": capacity,
            "available_spots": capacity - current_count if capacity is not None else None,
            "is_full": capacity is not None and current_count >= capacity,
            "utilization_percentage": round((current_count / capacity) * 100, 2) if capacity and capacity > 0 else None
        }
        
        logger.trace("Class capacity info for id=%s: %s", class_id, result)
        return result

    # --- Attendance methods ---

    def get_students_without_attendance(
        self, class_id: int, attendance_date: str
    ) -> list[StudentResponse]:
        """Get students in class who don't have attendance recorded for the given date."""
        logger.debug("Fetching students without attendance for class_id=%s on date=%s", class_id, attendance_date)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return []
        
        students = self.repo.get_students_without_attendance(class_id, attendance_date)
        logger.info("Retrieved %d students without attendance for class_id=%s on date=%s", 
                    len(students), class_id, attendance_date)
        return [self._build_student_response(s) for s in students]

    def record_attendance(
        self,
        class_id: int,
        student_id: int,
        attendance_date: str,
        status: str = "present",
        recorded_by: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> tuple[Optional[dict], Optional[str]]:
        """Record attendance for a student on a specific date."""
        logger.info("Recording attendance: class_id=%s, student_id=%s, date=%s, status=%s", 
                    class_id, student_id, attendance_date, status)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found for attendance recording: id=%s", class_id)
            return None, "Class not found"
        
        # Verify student exists and is enrolled in the class
        student = self.student_repo.get_by_id(student_id)
        if not student:
            logger.warning("Student not found for attendance recording: id=%s", student_id)
            return None, "Student not found"
        
        # Check if student is enrolled in the class
        class_ids = self.student_repo.get_class_ids(student_id)
        if class_id not in class_ids:
            logger.warning("Student id=%s is not enrolled in class id=%s", student_id, class_id)
            return None, "Student is not enrolled in this class"
        
        # Validate recorded_by if provided
        if recorded_by is not None:
            teacher = self.user_repo.get_by_id(recorded_by)
            if not teacher or teacher.get("role") != UserRole.TEACHER.value:
                logger.warning("Teacher not found for attendance recording: id=%s", recorded_by)
                return None, "Teacher not found"
        
        # Validate status
        valid_statuses = ["present", "absent", "late", "excused"]
        if status not in valid_statuses:
            logger.warning("Invalid attendance status: %s", status)
            return None, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        
        result = self.repo.record_attendance(
            class_id=class_id,
            student_id=student_id,
            attendance_date=attendance_date,
            status=status,
            recorded_by=recorded_by,
            notes=notes,
        )
        
        logger.info("Attendance recorded successfully: attendance_id=%s", result["attendance_id"])
        return result, None

    def get_attendance_for_date(self, class_id: int, attendance_date: str) -> list[dict]:
        """Get all attendance records for a class on a specific date."""
        logger.debug("Fetching attendance for class_id=%s on date=%s", class_id, attendance_date)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return []
        
        attendance_records = self.repo.get_attendance_for_date(class_id, attendance_date)
        logger.info("Retrieved %d attendance records for class_id=%s on date=%s", 
                    len(attendance_records), class_id, attendance_date)
        return attendance_records

    def get_attendance_history(
        self, 
        class_id: int, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> list[dict]:
        """Get attendance history for a class with optional date range."""
        logger.debug("Fetching attendance history for class_id=%s from %s to %s", class_id, start_date, end_date)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return []
        
        attendance_records = self.repo.get_attendance_history(class_id, start_date, end_date)
        logger.info("Retrieved %d attendance history records for class_id=%s", len(attendance_records), class_id)
        return attendance_records

    def _build_response(self, cls: dict) -> ClassResponse:
        """Build a ClassResponse with students and teachers."""
        class_id = cls["class_id"]
        logger.trace("Building ClassResponse for class id=%s", class_id)

        # Get students
        students = self.student_repo.get_by_class_id(class_id)
        student_responses = [self._build_student_response(s) for s in students]

        # Get teachers
        teachers = self.user_repo.get_teachers_by_class_id(class_id)
        teacher_responses = [UserResponse(**t) for t in teachers]

        logger.trace("ClassResponse built for id=%s: %d student(s), %d teacher(s)", class_id, len(student_responses), len(teacher_responses))
        return ClassResponse(
            **cls,
            students=student_responses,
            teachers=teacher_responses,
        )

    def _build_student_response(self, student: dict) -> StudentResponse:
        """Build a StudentResponse with class_ids, parents, allergies, and HW info."""
        student_id = student["student_id"]
        logger.trace("Building StudentResponse for student id=%s", student_id)

        class_ids = self.student_repo.get_class_ids(student_id)
        parent_ids = self.student_repo.get_parent_ids(student_id)
        allergies = [
            AllergyResponse(**a) for a in self.student_repo.get_allergies(student_id)
        ]
        hw_info = [
            HWInfoResponse(**h) for h in self.student_repo.get_hw_info(student_id)
        ]

        # Strip legacy class_id field from the student dict if present
        student_fields = {k: v for k, v in student.items() if k != "class_id"}

        logger.trace(
            "StudentResponse built for id=%s: %d class(es), %d parent(s), %d allergy(ies), %d hw_info(s)",
            student_id, len(class_ids), len(parent_ids), len(allergies), len(hw_info),
        )
        return StudentResponse(
            **student_fields,
            class_ids=class_ids,
            parents=parent_ids,
            student_allergies=allergies,
            student_hw_info=hw_info,
        )
