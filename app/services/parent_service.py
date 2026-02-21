"""Service layer for Parent entity."""
import sqlite3
from typing import Optional

from app.repositories.parent_repository import ParentRepository
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

    def create(self, data: ParentCreate) -> ParentResponse:
        """Create a new parent."""
        result = self.repo.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            address=data.address,
        )
        return ParentResponse(**result)

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

    def update(self, parent_id: int, data: ParentUpdate) -> Optional[ParentResponse]:
        """Update a parent."""
        update_data = data.model_dump(exclude_unset=True)
        result = self.repo.update(parent_id, **update_data)
        if not result:
            return None
        return ParentResponse(**result)

    def delete(self, parent_id: int) -> bool:
        """Soft delete a parent."""
        return self.repo.soft_delete(parent_id)

    def exists(self, parent_id: int) -> bool:
        """Check if parent exists."""
        return self.repo.exists(parent_id)
