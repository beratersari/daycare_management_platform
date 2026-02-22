"""Service layer for Term entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.term_repository import TermRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.class_repository import ClassRepository
from app.schemas.term import TermCreate, TermResponse, TermUpdate

logger = get_logger(__name__)


class TermService:
    """Service for Term business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = TermRepository(db)
        self.school_repo = SchoolRepository(db)
        self.class_repo = ClassRepository(db)
        logger.trace("TermService initialised")

    def create(self, data: TermCreate) -> tuple[Optional[TermResponse], Optional[str]]:
        """Create a new term."""
        logger.info("Creating term: %s for school_id=%s", data.term_name, data.school_id)
        logger.debug("Term creation payload: %s", data.model_dump())

        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            logger.warning("School not found during term creation: school_id=%s", data.school_id)
            return None, "School not found"

        # Create term
        term = self.repo.create(
            school_id=data.school_id,
            term_name=data.term_name,
            start_date=data.start_date,
            end_date=data.end_date,
            activity_status=data.activity_status,
            term_img_url=data.term_img_url,
        )

        logger.info("Term created successfully with id=%s", term["term_id"])
        return TermResponse(**term), None

    def get_all(self) -> list[TermResponse]:
        """Get all terms."""
        logger.debug("Fetching all terms")
        terms = self.repo.get_all()
        logger.info("Retrieved %d term(s)", len(terms))
        return [TermResponse(**t) for t in terms]

    def get_by_id(self, term_id: int) -> Optional[TermResponse]:
        """Get a term by ID."""
        logger.debug("Fetching term by id=%s", term_id)
        term = self.repo.get_by_id(term_id)
        if not term:
            logger.warning("Term not found: id=%s", term_id)
            return None
        logger.trace("Term found: %s", term)
        return TermResponse(**term)

    def get_by_school_id(self, school_id: int) -> list[TermResponse]:
        """Get all terms for a specific school."""
        logger.debug("Fetching terms for school_id=%s", school_id)
        if not self.school_repo.exists(school_id):
            logger.warning("School not found: id=%s", school_id)
            return []
        terms = self.repo.get_by_school_id(school_id)
        logger.info("Retrieved %d term(s) for school id=%s", len(terms), school_id)
        return [TermResponse(**t) for t in terms]

    def get_active_term_by_school(self, school_id: int) -> Optional[TermResponse]:
        """Get the active term for a school."""
        logger.debug("Fetching active term for school_id=%s", school_id)
        if not self.school_repo.exists(school_id):
            logger.warning("School not found: id=%s", school_id)
            return None
        term = self.repo.get_active_term_by_school(school_id)
        if not term:
            logger.trace("No active term found for school id=%s", school_id)
            return None
        logger.trace("Active term found for school id=%s: %s", school_id, term)
        return TermResponse(**term)

    def update(self, term_id: int, data: TermUpdate) -> tuple[Optional[TermResponse], Optional[str]]:
        """Update a term."""
        logger.info("Updating term: id=%s", term_id)
        existing = self.repo.get_by_id(term_id)
        if not existing:
            logger.warning("Term not found for update: id=%s", term_id)
            return None, "Term not found"

        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Term update data: %s", update_data)

        result = self.repo.update(term_id, **update_data)
        logger.info("Term updated successfully: id=%s", term_id)
        return TermResponse(**result), None

    def delete(self, term_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a term if no active classes are assigned to it."""
        logger.info("Attempting to delete term: id=%s", term_id)
        if not self.repo.exists(term_id):
            logger.warning("Term not found for deletion: id=%s", term_id)
            return False, "Term not found"

        # Business rule: a term cannot be deleted while it has active classes assigned
        class_count = self.repo.count_active_classes_in_term(term_id)
        logger.trace("Term id=%s has %d active class(es)", term_id, class_count)

        if class_count > 0:
            msg = f"{class_count} active class(es)"
            logger.warning("Cannot delete term id=%s — active dependencies: %s", term_id, msg)
            return False, f"Cannot delete term. It still has {msg} assigned to it."

        self.repo.soft_delete(term_id)
        logger.info("Term soft-deleted successfully: id=%s", term_id)
        return True, None

    def exists(self, term_id: int) -> bool:
        """Check if term exists."""
        result = self.repo.exists(term_id)
        logger.trace("Term exists check: id=%s → %s", term_id, result)
        return result

    def assign_class_to_term(self, class_id: int, term_id: int) -> tuple[bool, Optional[str]]:
        """Assign a class to a term."""
        logger.info("Assigning class id=%s to term id=%s", class_id, term_id)

        # Validate term exists
        if not self.repo.exists(term_id):
            logger.warning("Term not found: id=%s", term_id)
            return False, "Term not found"

        # Validate class exists
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return False, "Class not found"

        success = self.repo.assign_class_to_term(class_id, term_id)
        if success:
            logger.info("Class assigned to term successfully: class_id=%s, term_id=%s", class_id, term_id)
            return True, None
        else:
            logger.error("Failed to assign class to term: class_id=%s, term_id=%s", class_id, term_id)
            return False, "Failed to assign class to term"

    def unassign_class_from_term(self, class_id: int, term_id: int) -> tuple[bool, Optional[str]]:
        """Unassign a class from a term."""
        logger.info("Unassigning class id=%s from term id=%s", class_id, term_id)

        # Validate term exists
        if not self.repo.exists(term_id):
            logger.warning("Term not found: id=%s", term_id)
            return False, "Term not found"

        # Validate class exists
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return False, "Class not found"

        success = self.repo.unassign_class_from_term(class_id, term_id)
        if success:
            logger.info("Class unassigned from term successfully: class_id=%s, term_id=%s", class_id, term_id)
            return True, None
        else:
            logger.error("Failed to unassign class from term: class_id=%s, term_id=%s", class_id, term_id)
            return False, "Failed to unassign class from term"

    def get_classes_by_term(self, term_id: int) -> list[dict]:
        """Get all classes assigned to a term."""
        logger.debug("Fetching classes for term id=%s", term_id)
        if not self.repo.exists(term_id):
            logger.warning("Term not found: id=%s", term_id)
            return []
        classes = self.repo.get_classes_by_term(term_id)
        logger.info("Retrieved %d class(es) for term id=%s", len(classes), term_id)
        return classes

    def get_terms_by_class(self, class_id: int) -> list[TermResponse]:
        """Get all terms assigned to a class."""
        logger.debug("Fetching terms for class id=%s", class_id)
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found: id=%s", class_id)
            return []
        terms = self.repo.get_terms_by_class(class_id)
        logger.info("Retrieved %d term(s) for class id=%s", len(terms), class_id)
        return [TermResponse(**t) for t in terms]
