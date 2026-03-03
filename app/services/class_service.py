"""Service layer for Class entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.class_repository import ClassRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.user_repository import UserRepository
from app.repositories.term_repository import TermRepository
from app.schemas.class_dto import (
    ClassCreate, ClassResponse, ClassUpdate, ClassEventCreate, ClassEventUpdate, ClassEventResponse,
    StudentAssignmentRequest, StudentAssignmentResponse,
    TeacherAssignmentRequest, TeacherAssignmentResponse,
    ClassAssignmentsResponse, BulkStudentAssignmentRequest, BulkTeacherAssignmentRequest, BulkAssignmentResponse,
)
from app.schemas.auth import UserResponse
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
        self.term_repo = TermRepository(db)
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

    def bulk_record_attendance(
        self,
        class_id: int,
        attendance_date: str,
        entries: list[dict],
        recorded_by: Optional[int] = None,
    ) -> tuple[Optional[list[dict]], Optional[str]]:
        """
        Record attendance for multiple students at once (bulk edit).
        
        Validates the class, each student's enrollment, the status values,
        and the optional recorded_by teacher, then delegates to the repo.
        
        Returns (list_of_records, None) on success or (None, error_message) on failure.
        """
        logger.info(
            "Bulk recording attendance: class_id=%s, date=%s, %d entries",
            class_id, attendance_date, len(entries),
        )

        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found for bulk attendance: id=%s", class_id)
            return None, "Class not found"

        valid_statuses = ["present", "absent", "late", "excused"]

        # Validate each entry
        seen_student_ids: set[int] = set()
        for entry in entries:
            student_id = entry["student_id"]

            # Check for duplicates within the request
            if student_id in seen_student_ids:
                logger.warning("Duplicate student_id=%s in bulk attendance request", student_id)
                return None, f"Duplicate student_id {student_id} in request"
            seen_student_ids.add(student_id)

            # Verify student exists
            student = self.student_repo.get_by_id(student_id)
            if not student:
                logger.warning("Student not found for bulk attendance: id=%s", student_id)
                return None, f"Student with id {student_id} not found"

            # Verify student is enrolled in the class
            class_ids = self.student_repo.get_class_ids(student_id)
            if class_id not in class_ids:
                logger.warning("Student id=%s is not enrolled in class id=%s", student_id, class_id)
                return None, f"Student with id {student_id} is not enrolled in this class"

            # Validate status
            status = entry.get("status", "present")
            if status not in valid_statuses:
                logger.warning("Invalid attendance status '%s' for student_id=%s", status, student_id)
                return None, f"Invalid status '{status}' for student {student_id}. Must be one of: {', '.join(valid_statuses)}"

        # All validations passed — delegate to repository
        results = self.repo.bulk_record_attendance(
            class_id=class_id,
            attendance_date=attendance_date,
            entries=entries,
            recorded_by=recorded_by,
        )

        logger.info("Bulk attendance recorded: %d records for class_id=%s", len(results), class_id)
        return results, None

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

    # --- Event methods ---

    def create_event(
        self,
        class_id: int,
        data: ClassEventCreate,
        created_by: int,
    ) -> tuple[Optional[ClassEventResponse], Optional[str]]:
        """Create a new class event."""
        logger.info("Creating event for class_id=%s by user_id=%s", class_id, created_by)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found for event creation: id=%s", class_id)
            return None, "Class not found"
        
        event = self.repo.create_event(
            class_id=class_id,
            title=data.title,
            description=data.description,
            photo_url=data.photo_url,
            event_date=data.event_date,
            created_by=created_by,
        )
        
        logger.info("Event created successfully: event_id=%s", event["event_id"])
        return ClassEventResponse(**event), None

    def get_event_by_id(
        self,
        class_id: int,
        event_id: int,
    ) -> tuple[Optional[ClassEventResponse], Optional[str]]:
        """Get a class event by ID."""
        logger.debug("Fetching event: event_id=%s for class_id=%s", event_id, class_id)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return None, "Class not found"
        
        event = self.repo.get_event_by_id(event_id)
        if not event:
            logger.warning("Event not found: event_id=%s", event_id)
            return None, "Event not found"
        
        # Verify event belongs to this class
        if event["class_id"] != class_id:
            logger.warning("Event %s does not belong to class %s", event_id, class_id)
            return None, "Event not found in this class"
        
        logger.trace("Event found: event_id=%s", event_id)
        return ClassEventResponse(**event), None

    def get_events_by_class_id(
        self,
        class_id: int,
    ) -> tuple[list[ClassEventResponse], Optional[str]]:
        """Get all events for a class."""
        logger.debug("Fetching events for class_id=%s", class_id)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return [], "Class not found"
        
        events = self.repo.get_events_by_class_id(class_id)
        logger.info("Retrieved %d event(s) for class_id=%s", len(events), class_id)
        return [ClassEventResponse(**e) for e in events], None

    def update_event(
        self,
        class_id: int,
        event_id: int,
        data: ClassEventUpdate,
        updated_by: int,
    ) -> tuple[Optional[ClassEventResponse], Optional[str]]:
        """Update a class event."""
        logger.info("Updating event: event_id=%s for class_id=%s by user_id=%s", event_id, class_id, updated_by)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return None, "Class not found"
        
        # Get existing event
        existing = self.repo.get_event_by_id(event_id)
        if not existing:
            logger.warning("Event not found for update: event_id=%s", event_id)
            return None, "Event not found"
        
        # Verify event belongs to this class
        if existing["class_id"] != class_id:
            logger.warning("Event %s does not belong to class %s", event_id, class_id)
            return None, "Event not found in this class"
        
        # Only the creator or admin can update (we'll check admin in router)
        # For now, just perform the update
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Event update data: %s", update_data)
        
        result = self.repo.update_event(
            event_id=event_id,
            title=update_data.get("title"),
            description=update_data.get("description"),
            photo_url=update_data.get("photo_url"),
            event_date=update_data.get("event_date"),
        )
        
        if not result:
            logger.warning("Failed to update event: event_id=%s", event_id)
            return None, "Failed to update event"
        
        logger.info("Event updated successfully: event_id=%s", event_id)
        return ClassEventResponse(**result), None

    def delete_event(
        self,
        class_id: int,
        event_id: int,
        deleted_by: int,
    ) -> tuple[bool, Optional[str]]:
        """Soft delete a class event."""
        logger.info("Deleting event: event_id=%s for class_id=%s by user_id=%s", event_id, class_id, deleted_by)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return False, "Class not found"
        
        # Get existing event
        existing = self.repo.get_event_by_id(event_id)
        if not existing:
            logger.warning("Event not found for deletion: event_id=%s", event_id)
            return False, "Event not found"
        
        # Verify event belongs to this class
        if existing["class_id"] != class_id:
            logger.warning("Event %s does not belong to class %s", event_id, class_id)
            return False, "Event not found in this class"
        
        success = self.repo.soft_delete_event(event_id)
        
        if success:
            logger.info("Event deleted successfully: event_id=%s", event_id)
            return True, None
        else:
            logger.warning("Failed to delete event: event_id=%s", event_id)
            return False, "Failed to delete event"

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

    def get_events_for_user(
        self,
        user_id: int,
        role: str,
    ) -> list[dict]:
        """Get events visible to a user based on their role."""
        logger.debug("Fetching events for user_id=%s with role=%s", user_id, role)
        
        events = self.repo.get_events_for_user(user_id, role)
        logger.info("Retrieved %d events for user_id=%s with role=%s", len(events), user_id, role)
        return events

    # --- Student Assignment Methods ---

    def assign_student_to_class(
        self,
        class_id: int,
        data: StudentAssignmentRequest,
    ) -> tuple[Optional[StudentAssignmentResponse], Optional[str]]:
        """
        Assign a student to a class for a specific term.
        
        Business rules:
        - Student must exist and belong to the same school as the class
        - Term must be active and belong to the same school
        - Student cannot be assigned to multiple active classes in the same term
        - Class capacity must not be exceeded
        """
        logger.info("Assigning student_id=%s to class_id=%s (term_id=%s)", data.student_id, class_id, data.term_id)
        
        # Verify class exists
        class_data = self.repo.get_by_id(class_id)
        if not class_data:
            logger.warning("Class not found: id=%s", class_id)
            return None, "Class not found"
        
        # Verify student exists
        student = self.student_repo.get_by_id(data.student_id)
        if not student:
            logger.warning("Student not found: id=%s", data.student_id)
            return None, "Student not found"
        
        # Verify student belongs to same school as class
        if student["school_id"] != class_data["school_id"]:
            logger.warning(
                "Student school_id=%s does not match class school_id=%s",
                student["school_id"], class_data["school_id"]
            )
            return None, "Student must belong to the same school as the class"
        
        # Resolve term_id
        term_id = data.term_id
        if term_id is None:
            # Use the school's active term
            active_term = self.term_repo.get_active_term_by_school(class_data["school_id"])
            if not active_term:
                logger.warning("No active term found for school_id=%s", class_data["school_id"])
                return None, "No active term found for the school. Please specify a term_id."
            term_id = active_term["term_id"]
            logger.debug("Using active term_id=%s for school_id=%s", term_id, class_data["school_id"])
        
        # Verify term exists and belongs to same school
        term = self.term_repo.get_by_id(term_id)
        if not term:
            logger.warning("Term not found: id=%s", term_id)
            return None, "Term not found"
        if term["school_id"] != class_data["school_id"]:
            logger.warning("Term school_id=%s does not match class school_id=%s", term["school_id"], class_data["school_id"])
            return None, "Term must belong to the same school as the class"
        
        # Check if student is already assigned to this class for this term
        if self.student_repo.is_enrolled_in_class(data.student_id, class_id, term_id):
            logger.info("Student id=%s already assigned to class_id=%s for term_id=%s", data.student_id, class_id, term_id)
            # Return success - idempotent operation
            return StudentAssignmentResponse(
                student_id=data.student_id,
                class_id=class_id,
                term_id=term_id,
                student_name=f"{student['first_name']} {student['last_name']}",
                class_name=class_data["class_name"],
                term_name=term["term_name"],
            ), None
        
        # Check if student is already assigned to another active class in the same term
        existing_enrollments = self.student_repo.get_active_term_enrollments(data.student_id, term_id)
        if existing_enrollments:
            existing_class_names = [e["class_name"] for e in existing_enrollments]
            logger.warning(
                "Student id=%s already assigned to active class(es) %s in term_id=%s",
                data.student_id, existing_class_names, term_id
            )
            return None, f"Student is already assigned to active class(es) in this term: {', '.join(existing_class_names)}"
        
        # Check class capacity
        capacity_ok, capacity_error = self.repo.check_capacity_available(class_id)
        if not capacity_ok:
            logger.warning("Class capacity exceeded: %s", capacity_error)
            return None, capacity_error
        
        # Perform assignment
        self.student_repo.enroll_in_class(data.student_id, class_id, term_id)
        logger.info("Student id=%s assigned to class_id=%s for term_id=%s", data.student_id, class_id, term_id)
        
        return StudentAssignmentResponse(
            student_id=data.student_id,
            class_id=class_id,
            term_id=term_id,
            student_name=f"{student['first_name']} {student['last_name']}",
            class_name=class_data["class_name"],
            term_name=term["term_name"],
        ), None

    def unassign_student_from_class(
        self,
        class_id: int,
        student_id: int,
        term_id: Optional[int] = None,
    ) -> tuple[bool, Optional[str]]:
        """Remove a student from a class."""
        logger.info("Unassigning student_id=%s from class_id=%s (term_id=%s)", student_id, class_id, term_id)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return False, "Class not found"
        
        # Verify student exists
        if not self.student_repo.exists(student_id):
            logger.warning("Student not found: id=%s", student_id)
            return False, "Student not found"
        
        # Check if student is enrolled
        if not self.student_repo.is_enrolled_in_class(student_id, class_id, term_id):
            logger.warning("Student id=%s is not enrolled in class_id=%s (term_id=%s)", student_id, class_id, term_id)
            return False, "Student is not enrolled in this class"
        
        # Remove enrollment
        self.student_repo.unenroll_from_class(student_id, class_id, term_id)
        logger.info("Student id=%s removed from class_id=%s (term_id=%s)", student_id, class_id, term_id)
        
        return True, None

    def bulk_assign_students(
        self,
        class_id: int,
        data: BulkStudentAssignmentRequest,
    ) -> BulkAssignmentResponse:
        """Assign multiple students to a class for a specific term."""
        logger.info("Bulk assigning %d students to class_id=%s", len(data.student_ids), class_id)
        
        assigned = []
        already_assigned = []
        failed = []
        
        for student_id in data.student_ids:
            result, error = self.assign_student_to_class(
                class_id,
                StudentAssignmentRequest(student_id=student_id, term_id=data.term_id)
            )
            if result:
                if error is None:
                    assigned.append(student_id)
                else:
                    # Already assigned case
                    already_assigned.append(student_id)
            else:
                failed.append({"id": student_id, "reason": error})
        
        return BulkAssignmentResponse(
            class_id=class_id,
            term_id=data.term_id,
            assigned=assigned,
            already_assigned=already_assigned,
            failed=failed,
        )

    # --- Teacher Assignment Methods ---

    def assign_teacher_to_class(
        self,
        class_id: int,
        data: TeacherAssignmentRequest,
    ) -> tuple[Optional[TeacherAssignmentResponse], Optional[str]]:
        """
        Assign a teacher to a class for a specific term.
        
        Business rules:
        - Teacher (user) must exist and have role TEACHER
        - Teacher must belong to the same school as the class
        - Term must be active and belong to the same school
        """
        logger.info("Assigning teacher_id=%s to class_id=%s (term_id=%s)", data.teacher_id, class_id, data.term_id)
        
        # Verify class exists
        class_data = self.repo.get_by_id(class_id)
        if not class_data:
            logger.warning("Class not found: id=%s", class_id)
            return None, "Class not found"
        
        # Verify teacher exists and has TEACHER role
        teacher = self.user_repo.get_by_id(data.teacher_id)
        if not teacher:
            logger.warning("Teacher not found: id=%s", data.teacher_id)
            return None, "Teacher not found"
        if teacher["role"] != "TEACHER":
            logger.warning("User id=%s is not a teacher (role=%s)", data.teacher_id, teacher["role"])
            return None, "User is not a teacher"
        
        # Verify teacher belongs to same school as class
        if teacher["school_id"] != class_data["school_id"]:
            logger.warning(
                "Teacher school_id=%s does not match class school_id=%s",
                teacher["school_id"], class_data["school_id"]
            )
            return None, "Teacher must belong to the same school as the class"
        
        # Resolve term_id
        term_id = data.term_id
        if term_id is None:
            active_term = self.term_repo.get_active_term_by_school(class_data["school_id"])
            if not active_term:
                logger.warning("No active term found for school_id=%s", class_data["school_id"])
                return None, "No active term found for the school. Please specify a term_id."
            term_id = active_term["term_id"]
            logger.debug("Using active term_id=%s for school_id=%s", term_id, class_data["school_id"])
        
        # Verify term exists and belongs to same school
        term = self.term_repo.get_by_id(term_id)
        if not term:
            logger.warning("Term not found: id=%s", term_id)
            return None, "Term not found"
        if term["school_id"] != class_data["school_id"]:
            logger.warning("Term school_id=%s does not match class school_id=%s", term["school_id"], class_data["school_id"])
            return None, "Term must belong to the same school as the class"
        
        # Check if teacher is already assigned to this class for this term
        if self.user_repo.is_teacher_assigned_to_class(data.teacher_id, class_id, term_id):
            logger.info("Teacher id=%s already assigned to class_id=%s for term_id=%s", data.teacher_id, class_id, term_id)
            # Return success - idempotent operation
            return TeacherAssignmentResponse(
                teacher_id=data.teacher_id,
                class_id=class_id,
                term_id=term_id,
                teacher_name=f"{teacher['first_name']} {teacher['last_name']}",
                class_name=class_data["class_name"],
                term_name=term["term_name"],
            ), None
        
        # Perform assignment
        self.user_repo.assign_teacher_to_class(data.teacher_id, class_id, term_id)
        logger.info("Teacher id=%s assigned to class_id=%s for term_id=%s", data.teacher_id, class_id, term_id)
        
        return TeacherAssignmentResponse(
            teacher_id=data.teacher_id,
            class_id=class_id,
            term_id=term_id,
            teacher_name=f"{teacher['first_name']} {teacher['last_name']}",
            class_name=class_data["class_name"],
            term_name=term["term_name"],
        ), None

    def unassign_teacher_from_class(
        self,
        class_id: int,
        teacher_id: int,
        term_id: Optional[int] = None,
    ) -> tuple[bool, Optional[str]]:
        """Remove a teacher from a class."""
        logger.info("Unassigning teacher_id=%s from class_id=%s (term_id=%s)", teacher_id, class_id, term_id)
        
        # Verify class exists
        if not self.repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return False, "Class not found"
        
        # Verify teacher exists
        teacher = self.user_repo.get_by_id(teacher_id)
        if not teacher:
            logger.warning("Teacher not found: id=%s", teacher_id)
            return False, "Teacher not found"
        
        # Check if teacher is assigned
        if not self.user_repo.is_teacher_assigned_to_class(teacher_id, class_id, term_id):
            logger.warning("Teacher id=%s is not assigned to class_id=%s (term_id=%s)", teacher_id, class_id, term_id)
            return False, "Teacher is not assigned to this class"
        
        # Remove assignment
        self.user_repo.unassign_teacher_from_class(teacher_id, class_id, term_id)
        logger.info("Teacher id=%s removed from class_id=%s (term_id=%s)", teacher_id, class_id, term_id)
        
        return True, None

    def bulk_assign_teachers(
        self,
        class_id: int,
        data: BulkTeacherAssignmentRequest,
    ) -> BulkAssignmentResponse:
        """Assign multiple teachers to a class for a specific term."""
        logger.info("Bulk assigning %d teachers to class_id=%s", len(data.teacher_ids), class_id)
        
        assigned = []
        already_assigned = []
        failed = []
        
        for teacher_id in data.teacher_ids:
            result, error = self.assign_teacher_to_class(
                class_id,
                TeacherAssignmentRequest(teacher_id=teacher_id, term_id=data.term_id)
            )
            if result:
                if error is None:
                    assigned.append(teacher_id)
                else:
                    already_assigned.append(teacher_id)
            else:
                failed.append({"id": teacher_id, "reason": error})
        
        return BulkAssignmentResponse(
            class_id=class_id,
            term_id=data.term_id,
            assigned=assigned,
            already_assigned=already_assigned,
            failed=failed,
        )

    # --- Class Assignments View ---

    def get_class_assignments(
        self,
        class_id: int,
        term_id: Optional[int] = None,
    ) -> tuple[Optional[ClassAssignmentsResponse], Optional[str]]:
        """Get all assignments (students and teachers) for a class."""
        logger.debug("Fetching assignments for class_id=%s (term_id=%s)", class_id, term_id)
        
        # Verify class exists
        class_data = self.repo.get_by_id(class_id)
        if not class_data:
            logger.warning("Class not found: id=%s", class_id)
            return None, "Class not found"
        
        # Resolve term_id if not provided
        resolved_term_id = term_id
        term_name = None
        if resolved_term_id is None:
            active_term = self.term_repo.get_active_term_by_school(class_data["school_id"])
            if active_term:
                resolved_term_id = active_term["term_id"]
                term_name = active_term["term_name"]
        else:
            term = self.term_repo.get_by_id(resolved_term_id)
            if term:
                term_name = term["term_name"]
        
        # Get students
        students_data = self.student_repo.get_students_by_class_and_term(class_id, resolved_term_id)
        students = [
            StudentAssignmentResponse(
                student_id=s["student_id"],
                class_id=class_id,
                term_id=s.get("term_id"),
                student_name=f"{s['first_name']} {s['last_name']}",
                class_name=class_data["class_name"],
                term_name=s.get("term_name"),
            )
            for s in students_data
        ]
        
        # Get teachers
        teachers_data = self.user_repo.get_teachers_by_class_id(class_id, resolved_term_id)
        teachers = [
            TeacherAssignmentResponse(
                teacher_id=t["user_id"],
                class_id=class_id,
                term_id=t.get("term_id"),
                teacher_name=f"{t['first_name']} {t['last_name']}",
                class_name=class_data["class_name"],
                term_name=t.get("term_name"),
            )
            for t in teachers_data
        ]
        
        # Get capacity info
        current_count = self.student_repo.count_students_in_class_for_term(class_id, resolved_term_id)
        capacity = class_data.get("capacity")
        available_spots = capacity - current_count if capacity is not None else None
        
        return ClassAssignmentsResponse(
            class_id=class_id,
            class_name=class_data["class_name"],
            term_id=resolved_term_id,
            term_name=term_name,
            students=students,
            teachers=teachers,
            capacity=capacity,
            current_student_count=current_count,
            available_spots=available_spots,
        ), None
