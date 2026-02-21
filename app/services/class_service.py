"""Service layer for Class entity."""
import sqlite3
from typing import Optional

from app.repositories.class_repository import ClassRepository
from app.repositories.teacher_repository import TeacherRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.school_repository import SchoolRepository
from app.schemas.class_dto import ClassCreate, ClassResponse, ClassUpdate
from app.schemas.teacher import TeacherResponse
from app.schemas.student import AllergyResponse, HWInfoResponse, StudentResponse


class ClassService:
    """Service for Class business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = ClassRepository(db)
        self.teacher_repo = TeacherRepository(db)
        self.student_repo = StudentRepository(db)
        self.school_repo = SchoolRepository(db)

    def create(self, data: ClassCreate) -> tuple[Optional[ClassResponse], Optional[str]]:
        """Create a new class."""
        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            return None, "School not found"
            
        # Validate class capacity doesn't exceed school capacity
        if data.capacity is not None:
            school_capacity = self.school_repo.get_capacity(data.school_id)
            if school_capacity is not None and data.capacity > school_capacity:
                return None, f"Class capacity ({data.capacity}) cannot exceed school capacity ({school_capacity})"

        # Create class
        cls = self.repo.create(
            class_name=data.class_name,
            school_id=data.school_id,
            capacity=data.capacity,
        )

        return self._build_response(cls), None

    def get_all(self) -> list[ClassResponse]:
        """Get all classes."""
        classes = self.repo.get_all()
        return [self._build_response(c) for c in classes]

    def get_by_id(self, class_id: int) -> Optional[ClassResponse]:
        """Get a class by ID."""
        cls = self.repo.get_by_id(class_id)
        if not cls:
            return None
        return self._build_response(cls)

    def update(
        self, class_id: int, data: ClassUpdate
    ) -> tuple[Optional[ClassResponse], Optional[str]]:
        """Update a class."""
        existing = self.repo.get_by_id(class_id)
        if not existing:
            return None, "Class not found"

        update_data = data.model_dump(exclude_unset=True)

        # Determine which school_id to use for capacity check
        school_id = update_data.get("school_id") if "school_id" in update_data else existing["school_id"]
        
        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                return None, "School not found"
        
        # Validate class capacity doesn't exceed school capacity
        if "capacity" in update_data and update_data["capacity"] is not None:
            new_capacity = update_data["capacity"]
            school_capacity = self.school_repo.get_capacity(school_id)
            if school_capacity is not None and new_capacity > school_capacity:
                return None, f"Class capacity ({new_capacity}) cannot exceed school capacity ({school_capacity})"

        # Update basic fields
        result = self.repo.update(class_id, **update_data)

        return self._build_response(result), None

    def delete(self, class_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a class if no active students or teachers exist."""
        if not self.repo.exists(class_id):
            return False, "Class not found"

        # Business rule: a class cannot be deleted while it has active students or teachers
        student_count = self.repo.count_active_students(class_id)
        teacher_count = self.repo.count_active_teachers(class_id)

        parts = []
        if student_count > 0:
            parts.append(f"{student_count} active student(s)")
        if teacher_count > 0:
            parts.append(f"{teacher_count} active teacher(s)")

        if parts:
            summary = " and ".join(parts)
            return False, f"Cannot delete class. It still has {summary}."

        self.repo.soft_delete(class_id)
        return True, None

    def exists(self, class_id: int) -> bool:
        """Check if class exists."""
        return self.repo.exists(class_id)

    def get_capacity_info(self, class_id: int) -> Optional[dict]:
        """Get class capacity information."""
        cls = self.repo.get_by_id(class_id)
        if not cls:
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
        
        return result

    def _build_response(self, cls: dict) -> ClassResponse:
        """Build a ClassResponse with students and teachers."""
        class_id = cls["class_id"]

        # Get students
        students = self.student_repo.get_by_class_id(class_id)
        student_responses = [self._build_student_response(s) for s in students]

        # Get teachers
        teachers = self.teacher_repo.get_by_class_id(class_id)
        teacher_responses = [TeacherResponse(**t) for t in teachers]

        return ClassResponse(
            **cls,
            students=student_responses,
            teachers=teacher_responses,
        )

    def _build_student_response(self, student: dict) -> StudentResponse:
        """Build a StudentResponse with parents, allergies, and HW info."""
        student_id = student["student_id"]

        parent_ids = self.student_repo.get_parent_ids(student_id)
        allergies = [
            AllergyResponse(**a) for a in self.student_repo.get_allergies(student_id)
        ]
        hw_info = [
            HWInfoResponse(**h) for h in self.student_repo.get_hw_info(student_id)
        ]

        return StudentResponse(
            **student,
            parents=parent_ids,
            student_allergies=allergies,
            student_hw_info=hw_info,
        )
