"""Service layer for Parent entity."""
import sqlite3
from typing import Optional

from app.repositories.parent_repository import ParentRepository
from app.repositories.school_repository import SchoolRepository
from app.schemas.parent import (
    ParentCreate,
    ParentResponse,
    ParentUpdate,
    ParentWithStudents,
)


class ParentService:
    """Service for Parent business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.repo = ParentRepository(db)
        self.school_repo = SchoolRepository(db)

    def create(self, data: ParentCreate) -> tuple[Optional[ParentResponse], Optional[str]]:
        """Create a new parent."""
        # Validate school exists
        if not self.school_repo.exists(data.school_id):
            return None, "School not found"
            
        result = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            school_id=data.school_id,
            email=data.email,
            phone=data.phone,
            address=data.address,
        )
        return ParentResponse(**result), None

    def get_all(self) -> list[ParentResponse]:
        """Get all parents."""
        parents = self.repo.get_all()
        return [ParentResponse(**p) for p in parents]

    def get_by_id(self, parent_id: int) -> Optional[ParentWithStudents]:
        """Get a parent by ID with student IDs."""
        parent = self.repo.get_by_id(parent_id)
        if not parent:
            return None
        student_ids = self.repo.get_student_ids(parent_id)
        return ParentWithStudents(**parent, student_ids=student_ids)

    def update(self, parent_id: int, data: ParentUpdate) -> tuple[Optional[ParentResponse], Optional[str]]:
        """Update a parent."""
        update_data = data.model_dump(exclude_unset=True)
        
        # Validate school if being updated
        if "school_id" in update_data and update_data["school_id"] is not None:
            if not self.school_repo.exists(update_data["school_id"]):
                return None, "School not found"
        
        result = self.repo.update(parent_id, **update_data)
        if not result:
            return None, "Parent not found"
        return ParentResponse(**result), None

    def delete(self, parent_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a parent if no linked students exist."""
        if not self.repo.exists(parent_id):
            return False, "Parent not found"

        # Business rule: a parent cannot be deleted while linked to students
        linked_count = self.repo.count_linked_students(parent_id)
        if linked_count > 0:
            return False, f"Cannot delete parent. Still linked to {linked_count} student(s)."

        self.repo.soft_delete(parent_id)
        return True, None

    def exists(self, parent_id: int) -> bool:
        """Check if parent exists."""
        return self.repo.exists(parent_id)
