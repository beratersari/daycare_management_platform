"""Service layer for Teacher entity."""
import sqlite3
from typing import Optional

from app.repositories.teacher_repository import TeacherRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.schemas.class_dto import ClassResponse
from app.schemas.student import AllergyResponse, HWInfoResponse, StudentResponse


class TeacherService:
    """Service for Teacher business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = TeacherRepository(db)
        self.class_repo = ClassRepository(db)
        self.student_repo = StudentRepository(db)

    def create(self, data: TeacherCreate) -> TeacherResponse:
        """Create a new teacher."""
        result = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            address=data.address,
        )
        return TeacherResponse(**result)

    def get_all(self) -> list[TeacherResponse]:
        """Get all teachers."""
        teachers = self.repo.get_all()
        return [TeacherResponse(**t) for t in teachers]

    def get_by_id(self, teacher_id: int) -> Optional[TeacherResponse]:
        """Get a teacher by ID."""
        teacher = self.repo.get_by_id(teacher_id)
        if not teacher:
            return None
        return TeacherResponse(**teacher)

    def update(self, teacher_id: int, data: TeacherUpdate) -> Optional[TeacherResponse]:
        """Update a teacher."""
        update_data = data.model_dump(exclude_unset=True)
        result = self.repo.update(teacher_id, **update_data)
        if not result:
            return None
        return TeacherResponse(**result)

    def delete(self, teacher_id: int) -> bool:
        """Soft delete a teacher."""
        return self.repo.soft_delete(teacher_id)

    def exists(self, teacher_id: int) -> bool:
        """Check if teacher exists."""
        return self.repo.exists(teacher_id)

    def get_classes(self, teacher_id: int) -> Optional[list[ClassResponse]]:
        """Get all classes for a teacher with full student details."""
        if not self.repo.exists(teacher_id):
            return None

        class_ids = self.repo.get_class_ids(teacher_id)
        classes = []

        for class_id in class_ids:
            cls = self.class_repo.get_by_id(class_id)
            if cls:
                classes.append(self._build_class_response(cls))

        return classes

    def _build_class_response(self, cls: dict) -> ClassResponse:
        """Build a ClassResponse with students and teachers."""
        class_id = cls["class_id"]

        # Get students
        students = self.student_repo.get_by_class_id(class_id)
        student_responses = [self._build_student_response(s) for s in students]

        # Get teachers
        teachers = self.class_repo.get_teachers(class_id)
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
