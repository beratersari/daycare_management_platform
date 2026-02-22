"""Service layer for School entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.school_repository import SchoolRepository
from app.repositories.term_repository import TermRepository
from app.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolUpdate,
    SchoolWithStats,
)

logger = get_logger(__name__)


class SchoolService:
    """Service for School business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.repo = SchoolRepository(db)
        self.term_repo = TermRepository(db)
        logger.trace("SchoolService initialised")

    def create(self, data: SchoolCreate) -> tuple[SchoolResponse, Optional[str]]:
        """Create a new school. Validates active_term_id and sets to 0 if term not found."""
        logger.info("Creating school: %s", data.school_name)
        logger.debug("School creation payload: %s", data.model_dump())
        
        active_term_id = data.active_term_id
        warning_message = None
        
        # Validate active_term_id if provided
        if active_term_id is not None and active_term_id != 0:
            if not self.term_repo.exists(active_term_id):
                logger.warning(
                    "Term id=%s not found for school creation. Setting active_term_id to 0.",
                    active_term_id
                )
                warning_message = f"Term with id={active_term_id} not found. active_term_id set to 0."
                active_term_id = 0
        
        result = self.repo.create(
            school_name=data.school_name,
            address=data.address,
            phone=data.phone,
            email=data.email,
            director_name=data.director_name,
            license_number=data.license_number,
            capacity=data.capacity,
            active_term_id=active_term_id,
        )
        logger.info("School created successfully with id=%s", result["school_id"])
        return SchoolResponse(**result), warning_message

    def get_all(self) -> list[SchoolResponse]:
        """Get all schools."""
        logger.debug("Fetching all schools")
        schools = self.repo.get_all()
        logger.info("Retrieved %d school(s)", len(schools))
        return [SchoolResponse(**s) for s in schools]

    def get_by_id(self, school_id: int) -> Optional[SchoolResponse]:
        """Get a school by ID."""
        logger.debug("Fetching school by id=%s", school_id)
        school = self.repo.get_by_id(school_id)
        if not school:
            logger.warning("School not found: id=%s", school_id)
            return None
        logger.trace("School found: %s", school)
        return SchoolResponse(**school)

    def get_by_id_with_stats(self, school_id: int) -> Optional[SchoolWithStats]:
        """Get a school by ID with statistics."""
        logger.debug("Fetching school with stats: id=%s", school_id)
        school = self.repo.get_by_id(school_id)
        if not school:
            logger.warning("School not found for stats: id=%s", school_id)
            return None
        stats = self.repo.get_school_stats(school_id)
        logger.trace("School stats for id=%s: %s", school_id, stats)
        return SchoolWithStats(**school, **stats)

    def update(self, school_id: int, data: SchoolUpdate) -> tuple[Optional[SchoolResponse], Optional[str]]:
        """Update a school. Validates active_term_id and sets to 0 if term not found."""
        logger.info("Updating school: id=%s", school_id)
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("School update data: %s", update_data)
        
        warning_message = None
        
        # Validate active_term_id if provided in update
        if "active_term_id" in update_data and update_data["active_term_id"] is not None:
            active_term_id = update_data["active_term_id"]
            if active_term_id != 0 and not self.term_repo.exists(active_term_id):
                logger.warning(
                    "Term id=%s not found for school update. Setting active_term_id to 0.",
                    active_term_id
                )
                warning_message = f"Term with id={active_term_id} not found. active_term_id set to 0."
                update_data["active_term_id"] = 0
        
        result = self.repo.update(school_id, **update_data)
        if not result:
            logger.warning("School not found for update: id=%s", school_id)
            return None, None
        logger.info("School updated successfully: id=%s", school_id)
        return SchoolResponse(**result), warning_message

    def delete(self, school_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a school if no active dependencies exist."""
        logger.info("Attempting to delete school: id=%s", school_id)
        if not self.repo.exists(school_id):
            logger.warning("School not found for deletion: id=%s", school_id)
            return False, "School not found"

        # Business rule: a school cannot be deleted while it has active entities
        dependencies = {
            "students": self.repo.count_active_students(school_id),
            "teachers": self.repo.count_active_teachers(school_id),
            "parents": self.repo.count_active_parents(school_id),
            "classes": self.repo.count_active_classes(school_id),
        }
        logger.trace("School id=%s dependency counts: %s", school_id, dependencies)

        active = {k: v for k, v in dependencies.items() if v > 0}
        if active:
            parts = [f"{count} active {label}" for label, count in active.items()]
            summary = ", ".join(parts)
            logger.warning("Cannot delete school id=%s — active dependencies: %s", school_id, summary)
            return False, f"Cannot delete school. It still has {summary}."

        self.repo.soft_delete(school_id)
        logger.info("School soft-deleted successfully: id=%s", school_id)
        return True, None

    def exists(self, school_id: int) -> bool:
        """Check if school exists."""
        result = self.repo.exists(school_id)
        logger.trace("School exists check: id=%s → %s", school_id, result)
        return result

    def get_capacity_info(self, school_id: int) -> Optional[dict]:
        """Get school capacity information."""
        logger.debug("Fetching capacity info for school id=%s", school_id)
        school = self.repo.get_by_id(school_id)
        if not school:
            logger.warning("School not found for capacity info: id=%s", school_id)
            return None
        
        current_count = self.repo.get_current_student_count(school_id)
        capacity = school.get("capacity")
        
        result = {
            "school_id": school_id,
            "school_name": school["school_name"],
            "current_students": current_count,
            "capacity": capacity,
            "available_spots": capacity - current_count if capacity is not None else None,
            "is_full": capacity is not None and current_count >= capacity,
            "utilization_percentage": round((current_count / capacity) * 100, 2) if capacity and capacity > 0 else None
        }
        
        logger.trace("School capacity info for id=%s: %s", school_id, result)
        return result