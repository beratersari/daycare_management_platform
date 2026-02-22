"""Service layer for Student entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
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

logger = get_logger(__name__)


class StudentService:
    """Service for Student business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = StudentRepository(db)
        self.parent_repo = ParentRepository(db)
        self.class_repo = ClassRepository(db)
        self.school_repo = SchoolRepository(db)
        logger.trace("StudentService initialised")

    def create(self, data: StudentCreate) -> tuple[Optional[StudentResponse], Optional[str]]:
        """Create a new student with class enrollments, parents, allergies, and HW info."""
        logger.info("Creating student: %s %s", data.first_name, data.last_name)
        logger.debug("Student creation payload: %s", data.model_dump())

        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            logger.warning("School not found during student creation: school_id=%s", data.school_id)
            return None, "School not found"
            
        # Check school capacity
        can_add_to_school, school_error = self.school_repo.check_capacity_available(data.school_id, 1)
        if not can_add_to_school:
            logger.warning("School capacity exceeded for school_id=%s: %s", data.school_id, school_error)
            return None, school_error

        # Validate each class_id and check capacity
        for cid in data.class_ids:
            if not self.class_repo.exists(cid):
                logger.warning("Class not found during student creation: class_id=%s", cid)
                return None, f"Class with id {cid} not found"
            can_add_to_class, class_error = self.class_repo.check_capacity_available(cid, 1)
            if not can_add_to_class:
                logger.warning("Class capacity exceeded for class_id=%s: %s", cid, class_error)
                return None, class_error

        # Validate parent_ids
        for pid in data.parent_ids:
            if not self.parent_repo.exists(pid):
                logger.warning("Parent not found during student creation: parent_id=%s", pid)
                return None, f"Parent with id {pid} not found"

        # Create student
        student = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            school_id=data.school_id,
            student_photo=data.student_photo,
            date_of_birth=data.date_of_birth,
        )
        student_id = student["student_id"]
        logger.info("Student created with id=%s", student_id)

        # Enroll in classes
        for cid in data.class_ids:
            self.repo.enroll_in_class(student_id, cid)
            logger.debug("Enrolled student id=%s in class id=%s", student_id, cid)
        if data.class_ids:
            logger.debug("Enrolled student id=%s in %d class(es)", student_id, len(data.class_ids))

        # Link parents
        for pid in data.parent_ids:
            self.repo.link_parent(student_id, pid)
            logger.debug("Linked parent id=%s to student id=%s", pid, student_id)

        # Add allergies
        for allergy in data.allergies:
            self.repo.add_allergy(
                student_id,
                allergy.allergy_name,
                allergy.severity,
                allergy.notes,
            )
        if data.allergies:
            logger.debug("Added %d allergy record(s) for student id=%s", len(data.allergies), student_id)

        # Add HW info
        for hw in data.hw_info:
            self.repo.add_hw_info(
                student_id,
                hw.height,
                hw.weight,
                hw.measurement_date,
            )
        if data.hw_info:
            logger.debug("Added %d HW info record(s) for student id=%s", len(data.hw_info), student_id)

        logger.info("Student creation completed: id=%s", student_id)
        return self._build_response(student), None

    def get_all(self) -> list[StudentResponse]:
        """Get all students."""
        logger.debug("Fetching all students")
        students = self.repo.get_all()
        logger.info("Retrieved %d student(s)", len(students))
        return [self._build_response(s) for s in students]

    def get_by_id(self, student_id: int) -> Optional[StudentResponse]:
        """Get a student by ID."""
        logger.debug("Fetching student by id=%s", student_id)
        student = self.repo.get_by_id(student_id)
        if not student:
            logger.warning("Student not found: id=%s", student_id)
            return None
        logger.trace("Student found: %s", student)
        return self._build_response(student)

    def update(
        self, student_id: int, data: StudentUpdate
    ) -> tuple[Optional[StudentResponse], Optional[str]]:
        """Update a student."""
        logger.info("Updating student: id=%s", student_id)
        existing = self.repo.get_by_id(student_id)
        if not existing:
            logger.warning("Student not found for update: id=%s", student_id)
            return None, "Student not found"

        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Student update data: %s", update_data)

        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                logger.warning("School not found during student update: school_id=%s", update_data["school_id"])
                return None, "School not found"
            
            # Check if changing schools - if so, validate new school capacity
            if update_data["school_id"] != existing["school_id"]:
                can_add_to_school, school_error = self.school_repo.check_capacity_available(update_data["school_id"], 1)
                if not can_add_to_school:
                    logger.warning("School capacity exceeded during student update: %s", school_error)
                    return None, school_error

        # Validate class_ids if being updated (replace all enrollments)
        if "class_ids" in update_data and update_data["class_ids"] is not None:
            current_class_ids = set(self.repo.get_class_ids(student_id))
            for cid in update_data["class_ids"]:
                if not self.class_repo.exists(cid):
                    logger.warning("Class not found during student update: class_id=%s", cid)
                    return None, f"Class with id {cid} not found"
                # Only check capacity for newly added classes
                if cid not in current_class_ids:
                    can_add_to_class, class_error = self.class_repo.check_capacity_available(cid, 1)
                    if not can_add_to_class:
                        logger.warning("Class capacity exceeded during student update: %s", class_error)
                        return None, class_error

        # Update basic fields (class_ids excluded — handled separately)
        basic_fields = {k: v for k, v in update_data.items() if k not in ("class_ids", "parent_ids", "allergies", "hw_info")}
        result = self.repo.update(student_id, **basic_fields)

        # Replace class enrollments if provided
        if "class_ids" in update_data and update_data["class_ids"] is not None:
            self.repo.unenroll_from_all_classes(student_id)
            for cid in update_data["class_ids"]:
                self.repo.enroll_in_class(student_id, cid)
            logger.debug("Replaced class enrollments for student id=%s: %s", student_id, update_data["class_ids"])

        # Update parent links if provided
        if "parent_ids" in update_data and update_data["parent_ids"] is not None:
            for pid in update_data["parent_ids"]:
                if not self.parent_repo.exists(pid):
                    logger.warning("Parent not found during student update: parent_id=%s", pid)
                    return None, f"Parent with id {pid} not found"
            self.repo.unlink_all_parents(student_id)
            for pid in update_data["parent_ids"]:
                self.repo.link_parent(student_id, pid)
            logger.debug("Updated parent links for student id=%s: %s", student_id, update_data["parent_ids"])

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
            logger.debug("Replaced allergies for student id=%s (%d records)", student_id, len(update_data["allergies"]))

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
            logger.debug("Replaced HW info for student id=%s (%d records)", student_id, len(update_data["hw_info"]))

        logger.info("Student updated successfully: id=%s", student_id)
        return self._build_response(result), None

    def delete(self, student_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a student."""
        logger.info("Attempting to delete student: id=%s", student_id)
        if not self.repo.exists(student_id):
            logger.warning("Student not found for deletion: id=%s", student_id)
            return False, "Student not found"

        self.repo.soft_delete(student_id)
        logger.info("Student soft-deleted successfully: id=%s", student_id)
        return True, None

    def exists(self, student_id: int) -> bool:
        """Check if student exists."""
        result = self.repo.exists(student_id)
        logger.trace("Student exists check: id=%s → %s", student_id, result)
        return result

    # --- Class enrollment operations ---

    def enroll_in_class(
        self, student_id: int, class_id: int
    ) -> tuple[Optional[StudentResponse], Optional[str]]:
        """Enroll a student in a class."""
        logger.info("Enrolling student id=%s in class id=%s", student_id, class_id)
        if not self.repo.exists(student_id):
            logger.warning("Student not found for enrollment: id=%s", student_id)
            return None, "Student not found"
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found for enrollment: id=%s", class_id)
            return None, "Class not found"
        if self.repo.is_enrolled_in_class(student_id, class_id):
            logger.warning("Student id=%s is already enrolled in class id=%s", student_id, class_id)
            return None, "Student is already enrolled in this class"
        can_add, error = self.class_repo.check_capacity_available(class_id, 1)
        if not can_add:
            logger.warning("Class capacity exceeded for class_id=%s: %s", class_id, error)
            return None, error
        self.repo.enroll_in_class(student_id, class_id)
        logger.info("Student id=%s enrolled in class id=%s", student_id, class_id)
        student = self.repo.get_by_id(student_id)
        return self._build_response(student), None

    def unenroll_from_class(
        self, student_id: int, class_id: int
    ) -> tuple[bool, Optional[str]]:
        """Unenroll a student from a class."""
        logger.info("Unenrolling student id=%s from class id=%s", student_id, class_id)
        if not self.repo.exists(student_id):
            logger.warning("Student not found for unenrollment: id=%s", student_id)
            return False, "Student not found"
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found for unenrollment: id=%s", class_id)
            return False, "Class not found"
        if not self.repo.is_enrolled_in_class(student_id, class_id):
            logger.warning("Student id=%s is not enrolled in class id=%s", student_id, class_id)
            return False, "Student is not enrolled in this class"
        self.repo.unenroll_from_class(student_id, class_id)
        logger.info("Student id=%s unenrolled from class id=%s", student_id, class_id)
        return True, None

    # --- Allergy operations ---

    def add_allergy(
        self, student_id: int, data: AllergyCreate
    ) -> tuple[Optional[AllergyResponse], Optional[str]]:
        """Add an allergy to a student."""
        logger.info("Adding allergy '%s' to student id=%s", data.allergy_name, student_id)
        if not self.repo.exists(student_id):
            logger.warning("Student not found for allergy addition: id=%s", student_id)
            return None, "Student not found"

        result = self.repo.add_allergy(
            student_id,
            data.allergy_name,
            data.severity,
            data.notes,
        )
        logger.info("Allergy added with id=%s for student id=%s", result["allergy_id"], student_id)
        return AllergyResponse(**result), None

    def delete_allergy(
        self, student_id: int, allergy_id: int
    ) -> tuple[bool, Optional[str]]:
        """Soft delete an allergy."""
        logger.info("Deleting allergy id=%s for student id=%s", allergy_id, student_id)
        allergy = self.repo.get_allergy(student_id, allergy_id)
        if not allergy:
            logger.warning("Allergy record not found: allergy_id=%s, student_id=%s", allergy_id, student_id)
            return False, "Allergy record not found"

        self.repo.soft_delete_allergy(allergy_id)
        logger.info("Allergy soft-deleted: id=%s", allergy_id)
        return True, None

    # --- HW Info operations ---

    def add_hw_info(
        self, student_id: int, data: HWInfoCreate
    ) -> tuple[Optional[HWInfoResponse], Optional[str]]:
        """Add HW info to a student."""
        logger.info("Adding HW info to student id=%s", student_id)
        logger.debug("HW info: height=%s, weight=%s, date=%s", data.height, data.weight, data.measurement_date)
        if not self.repo.exists(student_id):
            logger.warning("Student not found for HW info addition: id=%s", student_id)
            return None, "Student not found"

        result = self.repo.add_hw_info(
            student_id,
            data.height,
            data.weight,
            data.measurement_date,
        )
        logger.info("HW info added with id=%s for student id=%s", result["hw_id"], student_id)
        return HWInfoResponse(**result), None

    def delete_hw_info(
        self, student_id: int, hw_id: int
    ) -> tuple[bool, Optional[str]]:
        """Soft delete an HW info record."""
        logger.info("Deleting HW info id=%s for student id=%s", hw_id, student_id)
        hw_record = self.repo.get_hw_record(student_id, hw_id)
        if not hw_record:
            logger.warning("HW info record not found: hw_id=%s, student_id=%s", hw_id, student_id)
            return False, "HW info record not found"

        self.repo.soft_delete_hw_info(hw_id)
        logger.info("HW info soft-deleted: id=%s", hw_id)
        return True, None

    def _build_response(self, student: dict) -> StudentResponse:
        """Build a StudentResponse with class_ids, parents, allergies, and HW info."""
        student_id = student["student_id"]
        logger.trace("Building StudentResponse for student id=%s", student_id)

        class_ids = self.repo.get_class_ids(student_id)
        parent_ids = self.repo.get_parent_ids(student_id)
        allergies = [
            AllergyResponse(**a) for a in self.repo.get_allergies(student_id)
        ]
        hw_info = [HWInfoResponse(**h) for h in self.repo.get_hw_info(student_id)]

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
