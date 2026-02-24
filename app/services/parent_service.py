"""Service layer for Parent entity."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.parent_repository import ParentRepository
from app.repositories.school_repository import SchoolRepository
from app.schemas.parent import (
    ParentCreate,
    ParentResponse,
    ParentUpdate,
    ParentWithStudents,
)

logger = get_logger(__name__)


class ParentService:
    """Service for Parent business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.repo = ParentRepository(db)
        self.school_repo = SchoolRepository(db)
        logger.trace("ParentService initialised")

    def create(self, data: ParentCreate) -> tuple[Optional[ParentResponse], Optional[str]]:
        """Create a new parent."""
        logger.info("Creating parent: %s %s", data.first_name, data.last_name)
        logger.debug("Parent creation payload: %s", data.model_dump())

        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            logger.warning("School not found during parent creation: school_id=%s", data.school_id)
            return None, "School not found"
            
        result = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            school_id=data.school_id,
            email=data.email,
            phone=data.phone,
            address=data.address,
        )
        logger.info("Parent created successfully with id=%s", result["parent_id"])
        return ParentResponse(**result), None

    def get_all(self, search: Optional[str] = None) -> list[ParentResponse]:
        """Get all parents."""
        logger.debug("Fetching all parents")
        parents = self.repo.get_all(search)
        logger.info("Retrieved %d parent(s)", len(parents))
        return [ParentResponse(**p) for p in parents]

    def get_all_paginated(
        self, page: int = 1, page_size: int = 10, search: Optional[str] = None
    ) -> tuple[list[ParentResponse], int]:
        """Get paginated parents."""
        logger.debug("Fetching paginated parents: page=%d, page_size=%d", page, page_size)
        parents, total = self.repo.get_all_paginated(page, page_size, search)
        logger.info("Retrieved %d parent(s) out of %d total", len(parents), total)
        return [ParentResponse(**p) for p in parents], total

    def get_by_id(self, parent_id: int) -> Optional[ParentWithStudents]:
        """Get a parent by ID with student IDs."""
        logger.debug("Fetching parent by id=%s", parent_id)
        parent = self.repo.get_by_id(parent_id)
        if not parent:
            logger.warning("Parent not found: id=%s", parent_id)
            return None
        student_ids = self.repo.get_student_ids(parent_id)
        logger.trace("Parent id=%s linked to students: %s", parent_id, student_ids)
        return ParentWithStudents(**parent, student_ids=student_ids)

    def update(self, parent_id: int, data: ParentUpdate) -> tuple[Optional[ParentResponse], Optional[str]]:
        """Update a parent."""
        logger.info("Updating parent: id=%s", parent_id)
        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Parent update data: %s", update_data)
        
        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                logger.warning("School not found during parent update: school_id=%s", update_data["school_id"])
                return None, "School not found"
        
        result = self.repo.update(parent_id, **update_data)
        if not result:
            logger.warning("Parent not found for update: id=%s", parent_id)
            return None, "Parent not found"
        logger.info("Parent updated successfully: id=%s", parent_id)
        return ParentResponse(**result), None

    def delete(self, parent_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a parent if no linked students exist."""
        logger.info("Attempting to delete parent: id=%s", parent_id)
        if not self.repo.exists(parent_id):
            logger.warning("Parent not found for deletion: id=%s", parent_id)
            return False, "Parent not found"

        # Business rule: a parent cannot be deleted while linked to students
        linked_count = self.repo.count_linked_students(parent_id)
        logger.trace("Parent id=%s linked to %d student(s)", parent_id, linked_count)
        if linked_count > 0:
            logger.warning("Cannot delete parent id=%s — linked to %d student(s)", parent_id, linked_count)
            return False, f"Cannot delete parent. Still linked to {linked_count} student(s)."

        self.repo.soft_delete(parent_id)
        logger.info("Parent soft-deleted successfully: id=%s", parent_id)
        return True, None

    def exists(self, parent_id: int) -> bool:
        """Check if parent exists."""
        result = self.repo.exists(parent_id)
        logger.trace("Parent exists check: id=%s → %s", parent_id, result)
        return result
