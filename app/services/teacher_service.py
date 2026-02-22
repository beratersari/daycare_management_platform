"""Service layer for Teacher entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.teacher_repository import TeacherRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.school_repository import SchoolRepository
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
from app.schemas.class_dto import ClassResponse
from app.schemas.student import AllergyResponse, HWInfoResponse, StudentResponse

logger = get_logger(__name__)


class TeacherService:
    """Service for Teacher business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = TeacherRepository(db)
        self.class_repo = ClassRepository(db)
        self.student_repo = StudentRepository(db)
        self.school_repo = SchoolRepository(db)
        logger.trace("TeacherService initialised")

    def create(self, data: TeacherCreate) -> tuple[Optional[TeacherResponse], Optional[str]]:
        """Create a new teacher."""
        logger.info("Creating teacher: %s %s", data.first_name, data.last_name)
        logger.debug("Teacher creation payload: %s", data.model_dump())

        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            logger.warning("School not found during teacher creation: school_id=%s", data.school_id)
            return None, "School not found"

        # Validate class_id if provided
        if data.class_id is not None and not self.class_repo.exists(data.class_id):
            logger.warning("Class not found during teacher creation: class_id=%s", data.class_id)
            return None, "Class not found"

        result = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            school_id=data.school_id,
            class_id=data.class_id,
            email=data.email,
            phone=data.phone,
            address=data.address,
        )
        logger.info("Teacher created successfully with id=%s", result["teacher_id"])
        return TeacherResponse(**result), None

    def get_all(self) -> list[TeacherResponse]:
        """Get all teachers."""
        logger.debug("Fetching all teachers")
        teachers = self.repo.get_all()
        logger.info("Retrieved %d teacher(s)", len(teachers))
        return [TeacherResponse(**t) for t in teachers]

    def get_by_id(self, teacher_id: int) -> Optional[TeacherResponse]:
        """Get a teacher by ID."""
        logger.debug("Fetching teacher by id=%s", teacher_id)
        teacher = self.repo.get_by_id(teacher_id)
        if not teacher:
            logger.warning("Teacher not found: id=%s", teacher_id)
            return None
        logger.trace("Teacher found: %s", teacher)
        return TeacherResponse(**teacher)

    def update(self, teacher_id: int, data: TeacherUpdate) -> tuple[Optional[TeacherResponse], Optional[str]]:
        """Update a teacher."""
        logger.info("Updating teacher: id=%s", teacher_id)
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Teacher update data: %s", update_data)

        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                logger.warning("School not found during teacher update: school_id=%s", update_data["school_id"])
                return None, "School not found"

        # Validate class_id if being updated
        if "class_id" in update_data and update_data["class_id"] is not None:
            if not self.class_repo.exists(update_data["class_id"]):
                logger.warning("Class not found during teacher update: class_id=%s", update_data["class_id"])
                return None, "Class not found"

        result = self.repo.update(teacher_id, **update_data)
        if not result:
            logger.warning("Teacher not found for update: id=%s", teacher_id)
            return None, "Teacher not found"
        logger.info("Teacher updated successfully: id=%s", teacher_id)
        return TeacherResponse(**result), None

    def delete(self, teacher_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a teacher if not assigned to a class."""
        logger.info("Attempting to delete teacher: id=%s", teacher_id)
        if not self.repo.exists(teacher_id):
            logger.warning("Teacher not found for deletion: id=%s", teacher_id)
            return False, "Teacher not found"

        # Business rule: a teacher cannot be deleted while assigned to a class
        if self.repo.is_assigned_to_class(teacher_id):
            logger.warning("Cannot delete teacher id=%s — still assigned to a class", teacher_id)
            return False, "Cannot delete teacher. Still assigned to a class."

        self.repo.soft_delete(teacher_id)
        logger.info("Teacher soft-deleted successfully: id=%s", teacher_id)
        return True, None

    def exists(self, teacher_id: int) -> bool:
        """Check if teacher exists."""
        result = self.repo.exists(teacher_id)
        logger.trace("Teacher exists check: id=%s → %s", teacher_id, result)
        return result

    def get_classes(self, teacher_id: int) -> Optional[list[ClassResponse]]:
        """Get the class for a teacher with full student details."""
        logger.debug("Fetching classes for teacher id=%s", teacher_id)
        teacher = self.repo.get_by_id(teacher_id)
        if not teacher:
            logger.warning("Teacher not found for class lookup: id=%s", teacher_id)
            return None

        classes = []
        class_id = teacher.get("class_id")
        if class_id is not None:
            cls = self.class_repo.get_by_id(class_id)
            if cls:
                classes.append(self._build_class_response(cls))
        logger.trace("Teacher id=%s assigned to %d class(es)", teacher_id, len(classes))

        return classes

    def _build_class_response(self, cls: dict) -> ClassResponse:
        """Build a ClassResponse with students and teachers."""
        class_id = cls["class_id"]
        logger.trace("Building ClassResponse for class id=%s", class_id)

        # Get students
        students = self.student_repo.get_by_class_id(class_id)
        student_responses = [self._build_student_response(s) for s in students]

        # Get teachers
        teachers = self.repo.get_by_class_id(class_id)
        teacher_responses = [TeacherResponse(**t) for t in teachers]

        logger.trace("ClassResponse built for id=%s: %d student(s), %d teacher(s)", class_id, len(student_responses), len(teacher_responses))
        return ClassResponse(
            **cls,
            students=student_responses,
            teachers=teacher_responses,
        )

    def _build_student_response(self, student: dict) -> StudentResponse:
        """Build a StudentResponse with parents, allergies, and HW info."""
        student_id = student["student_id"]
        logger.trace("Building StudentResponse for student id=%s", student_id)

        parent_ids = self.student_repo.get_parent_ids(student_id)
        allergies = [
            AllergyResponse(**a) for a in self.student_repo.get_allergies(student_id)
        ]
        hw_info = [
            HWInfoResponse(**h) for h in self.student_repo.get_hw_info(student_id)
        ]

        logger.trace("StudentResponse built for id=%s: %d parent(s), %d allergy(ies), %d hw_info(s)", student_id, len(parent_ids), len(allergies), len(hw_info))
        return StudentResponse(
            **student,
            parents=parent_ids,
            student_allergies=allergies,
            student_hw_info=hw_info,
        )
