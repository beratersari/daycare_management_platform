"""Service layer for School entity."""
import sqlite3
from typing import Optional

from app.repositories.school_repository import SchoolRepository
from app.schemas.school import (
    SchoolCreate,
    SchoolResponse,
    SchoolUpdate,
    SchoolWithStats,
)


class SchoolService:
    """Service for School business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.repo = SchoolRepository(db)

    def create(self, data: SchoolCreate) -> SchoolResponse:
        """Create a new school."""
        result = self.repo.create(
            school_name=data.school_name,
            address=data.address,
            phone=data.phone,
            email=data.email,
            director_name=data.director_name,
            license_number=data.license_number,
            capacity=data.capacity,
        )
        return SchoolResponse(**result)

    def get_all(self) -> list[SchoolResponse]:
        """Get all schools."""
        schools = self.repo.get_all()
        return [SchoolResponse(**s) for s in schools]

    def get_by_id(self, school_id: int) -> Optional[SchoolResponse]:
        """Get a school by ID."""
        school = self.repo.get_by_id(school_id)
        if not school:
            return None
        return SchoolResponse(**school)

    def get_by_id_with_stats(self, school_id: int) -> Optional[SchoolWithStats]:
        """Get a school by ID with statistics."""
        school = self.repo.get_by_id(school_id)
        if not school:
            return None
        stats = self.repo.get_school_stats(school_id)
        return SchoolWithStats(**school, **stats)

    def update(self, school_id: int, data: SchoolUpdate) -> Optional[SchoolResponse]:
        """Update a school."""
        update_data = data.model_dump(exclude_unset=True)
        result = self.repo.update(school_id, **update_data)
        if not result:
            return None
        return SchoolResponse(**result)

    def delete(self, school_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete a school if no active dependencies exist."""
        if not self.repo.exists(school_id):
            return False, "School not found"

        # Business rule: a school cannot be deleted while it has active entities
        dependencies = {
            "students": self.repo.count_active_students(school_id),
            "teachers": self.repo.count_active_teachers(school_id),
            "parents": self.repo.count_active_parents(school_id),
            "classes": self.repo.count_active_classes(school_id),
        }

        active = {k: v for k, v in dependencies.items() if v > 0}
        if active:
            parts = [f"{count} active {label}" for label, count in active.items()]
            summary = ", ".join(parts)
            return False, f"Cannot delete school. It still has {summary}."

        self.repo.soft_delete(school_id)
        return True, None

    def exists(self, school_id: int) -> bool:
        """Check if school exists."""
        return self.repo.exists(school_id)

    def get_capacity_info(self, school_id: int) -> Optional[dict]:
        """Get school capacity information."""
        school = self.repo.get_by_id(school_id)
        if not school:
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
        
        return result