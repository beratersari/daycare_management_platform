"""Service layer for Class entity."""
import sqlite3
from typing import Optional

from app.repositories.class_repository import ClassRepository
from app.repositories.teacher_repository import TeacherRepository
from app.repositories.student_repository import StudentRepository
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

    def create(self, data: ClassCreate) -> tuple[Optional[ClassResponse], Optional[str]]:
        """Create a new class with teachers."""
        # Validate teacher_ids
        for tid in data.teacher_ids:
            if not self.teacher_repo.exists(tid):
                return None, f"Teacher with id {tid} not found"

        # Create class
        cls = self.repo.create(
            class_name=data.class_name,
            capacity=data.capacity,
        )
        class_id = cls["class_id"]

        # Link teachers
        for tid in data.teacher_ids:
            self.repo.link_teacher(class_id, tid)

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

        # Update basic fields
        result = self.repo.update(class_id, **update_data)

        # Update teacher links if provided
        if "teacher_ids" in update_data and update_data["teacher_ids"] is not None:
            for tid in update_data["teacher_ids"]:
                if not self.teacher_repo.exists(tid):
                    return None, f"Teacher with id {tid} not found"
            self.repo.unlink_all_teachers(class_id)
            for tid in update_data["teacher_ids"]:
                self.repo.link_teacher(class_id, tid)

        return self._build_response(result), None

    def delete(self, class_id: int) -> bool:
        """Soft delete a class."""
        return self.repo.soft_delete(class_id)

    def exists(self, class_id: int) -> bool:
        """Check if class exists."""
        return self.repo.exists(class_id)

    def _build_response(self, cls: dict) -> ClassResponse:
        """Build a ClassResponse with students and teachers."""
        class_id = cls["class_id"]

        # Get students
        students = self.student_repo.get_by_class_id(class_id)
        student_responses = [self._build_student_response(s) for s in students]

        # Get teachers
        teachers = self.repo.get_teachers(class_id)
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
