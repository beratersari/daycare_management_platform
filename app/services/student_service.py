"""Service layer for Student entity."""
import sqlite3
from typing import Optional

from app.repositories.student_repository import StudentRepository
from app.repositories.parent_repository import ParentRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.school_repository import SchoolRepository
from app.schemas.student import (
    AllergyCreate,
    AllergyResponse,
    HWInfoCreate,
    HWInfoResponse,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
)


class StudentService:
    """Service for Student business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = StudentRepository(db)
        self.parent_repo = ParentRepository(db)
        self.class_repo = ClassRepository(db)
        self.school_repo = SchoolRepository(db)

    def create(self, data: StudentCreate) -> tuple[Optional[StudentResponse], Optional[str]]:
        """Create a new student with parents, allergies, and HW info."""
        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            return None, "School not found"
            
        # Check school capacity
        can_add_to_school, school_error = self.school_repo.check_capacity_available(data.school_id, 1)
        if not can_add_to_school:
            return None, school_error
            
        # Validate class_id
        if data.class_id is not None and not self.class_repo.exists(data.class_id):
            return None, "Class not found"
            
        # Check class capacity if class is specified
        if data.class_id is not None:
            can_add_to_class, class_error = self.class_repo.check_capacity_available(data.class_id, 1)
            if not can_add_to_class:
                return None, class_error

        # Validate parent_ids
        for pid in data.parent_ids:
            if not self.parent_repo.exists(pid):
                return None, f"Parent with id {pid} not found"

        # Create student
        student = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            school_id=data.school_id,
            class_id=data.class_id,
            student_photo=data.student_photo,
            date_of_birth=data.date_of_birth,
        )
        student_id = student["student_id"]

        # Link parents
        for pid in data.parent_ids:
            self.repo.link_parent(student_id, pid)

        # Add allergies
        for allergy in data.allergies:
            self.repo.add_allergy(
                student_id,
                allergy.allergy_name,
                allergy.severity,
                allergy.notes,
            )

        # Add HW info
        for hw in data.hw_info:
            self.repo.add_hw_info(
                student_id,
                hw.height,
                hw.weight,
                hw.measurement_date,
            )

        return self._build_response(student), None

    def get_all(self) -> list[StudentResponse]:
        """Get all students."""
        students = self.repo.get_all()
        return [self._build_response(s) for s in students]

    def get_by_id(self, student_id: int) -> Optional[StudentResponse]:
        """Get a student by ID."""
        student = self.repo.get_by_id(student_id)
        if not student:
            return None
        return self._build_response(student)

    def update(
        self, student_id: int, data: StudentUpdate
    ) -> tuple[Optional[StudentResponse], Optional[str]]:
        """Update a student."""
        existing = self.repo.get_by_id(student_id)
        if not existing:
            return None, "Student not found"

        update_data = data.model_dump(exclude_unset=True)

        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                return None, "School not found"
            
            # Check if changing schools - if so, validate new school capacity
            if update_data["school_id"] != existing["school_id"]:
                can_add_to_school, school_error = self.school_repo.check_capacity_available(update_data["school_id"], 1)
                if not can_add_to_school:
                    return None, school_error

        # Validate class_id if being updated
        if "class_id" in update_data and update_data["class_id"] is not None:
            if not self.class_repo.exists(update_data["class_id"]):
                return None, "Class not found"
            
            # Check if changing classes - if so, validate new class capacity
            if update_data["class_id"] != existing.get("class_id"):
                can_add_to_class, class_error = self.class_repo.check_capacity_available(update_data["class_id"], 1)
                if not can_add_to_class:
                    return None, class_error

        # Update basic fields
        result = self.repo.update(student_id, **update_data)

        # Update parent links if provided
        if "parent_ids" in update_data and update_data["parent_ids"] is not None:
            for pid in update_data["parent_ids"]:
                if not self.parent_repo.exists(pid):
                    return None, f"Parent with id {pid} not found"
            self.repo.unlink_all_parents(student_id)
            for pid in update_data["parent_ids"]:
                self.repo.link_parent(student_id, pid)

        # Update allergies if provided (replace all)
        if "allergies" in update_data and update_data["allergies"] is not None:
            self.repo.soft_delete_all_allergies(student_id)
            for allergy_data in update_data["allergies"]:
                self.repo.add_allergy(
                    student_id,
                    allergy_data["allergy_name"],
                    allergy_data.get("severity"),
                    allergy_data.get("notes"),
                )

        # Update HW info if provided (replace all)
        if "hw_info" in update_data and update_data["hw_info"] is not None:
            self.repo.soft_delete_all_hw_info(student_id)
            for hw_data in update_data["hw_info"]:
                self.repo.add_hw_info(
                    student_id,
                    hw_data["height"],
                    hw_data["weight"],
                    hw_data["measurement_date"],
                )

        return self._build_response(result), None

    def delete(self, student_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a student."""
        if not self.repo.exists(student_id):
            return False, "Student not found"

        self.repo.soft_delete(student_id)
        return True, None

    def exists(self, student_id: int) -> bool:
        """Check if student exists."""
        return self.repo.exists(student_id)

    # --- Allergy operations ---

    def add_allergy(
        self, student_id: int, data: AllergyCreate
    ) -> tuple[Optional[AllergyResponse], Optional[str]]:
        """Add an allergy to a student."""
        if not self.repo.exists(student_id):
            return None, "Student not found"

        result = self.repo.add_allergy(
            student_id,
            data.allergy_name,
            data.severity,
            data.notes,
        )
        return AllergyResponse(**result), None

    def delete_allergy(
        self, student_id: int, allergy_id: int
    ) -> tuple[bool, Optional[str]]:
        """Soft delete an allergy."""
        allergy = self.repo.get_allergy(student_id, allergy_id)
        if not allergy:
            return False, "Allergy record not found"

        self.repo.soft_delete_allergy(allergy_id)
        return True, None

    # --- HW Info operations ---

    def add_hw_info(
        self, student_id: int, data: HWInfoCreate
    ) -> tuple[Optional[HWInfoResponse], Optional[str]]:
        """Add HW info to a student."""
        if not self.repo.exists(student_id):
            return None, "Student not found"

        result = self.repo.add_hw_info(
            student_id,
            data.height,
            data.weight,
            data.measurement_date,
        )
        return HWInfoResponse(**result), None

    def delete_hw_info(
        self, student_id: int, hw_id: int
    ) -> tuple[bool, Optional[str]]:
        """Soft delete an HW info record."""
        hw_record = self.repo.get_hw_record(student_id, hw_id)
        if not hw_record:
            return False, "HW info record not found"

        self.repo.soft_delete_hw_info(hw_id)
        return True, None

    def _build_response(self, student: dict) -> StudentResponse:
        """Build a StudentResponse with parents, allergies, and HW info."""
        student_id = student["student_id"]

        parent_ids = self.repo.get_parent_ids(student_id)
        allergies = [
            AllergyResponse(**a) for a in self.repo.get_allergies(student_id)
        ]
        hw_info = [HWInfoResponse(**h) for h in self.repo.get_hw_info(student_id)]

        return StudentResponse(
            **student,
            parents=parent_ids,
            student_allergies=allergies,
            student_hw_info=hw_info,
        )
