"""Service layer for Class Events."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.event_repository import EventRepository
from app.repositories.class_repository import ClassRepository
from app.repositories.user_repository import UserRepository
from app.schemas.class_dto import EventCreate, EventResponse, EventUpdate
from app.schemas.auth import UserRole

logger = get_logger(__name__)


class EventService:
    """Service for Class Event business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.repo = EventRepository(db)
        self.class_repo = ClassRepository(db)
        self.user_repo = UserRepository(db)
        logger.trace("EventService initialised")

    def create(self, class_id: int, data: EventCreate, created_by: int) -> tuple[Optional[EventResponse], Optional[str]]:
        """Create a new event."""
        logger.info("Creating event '%s' for class_id=%s", data.title, class_id)
        
        # Verify class exists
        if not self.class_repo.exists(class_id):
            logger.warning("Class not found for event creation: id=%s", class_id)
            return None, "Class not found"

        event = self.repo.create(
            class_id=class_id,
            title=data.title,
            description=data.description,
            photo_url=data.photo_url,
            event_date=data.event_date,
            created_by=created_by,
        )
        
        logger.info("Event created successfully with id=%s", event["event_id"])
        return EventResponse(**event), None

    def get_by_class_id(self, class_id: int, page: int = 1, page_size: int = 10) -> tuple[list[EventResponse], int]:
        """Get events for a class."""
        logger.debug("Fetching events for class_id=%s", class_id)
        
        if not self.class_repo.exists(class_id):
             pass

        events, total = self.repo.get_by_class_id(class_id, page, page_size)
        return [EventResponse(**e) for e in events], total

    def update(self, event_id: int, data: EventUpdate, user_id: int = None, user_role: str = None) -> tuple[Optional[EventResponse], Optional[str]]:
        """Update an event."""
        logger.info("Updating event: id=%s", event_id)
        
        existing = self.repo.get_by_id(event_id)
        if not existing:
            logger.warning("Event not found for update: id=%s", event_id)
            return None, "Event not found"

        result = self.repo.update(event_id, **data.model_dump(exclude_unset=True))
        return EventResponse(**result), None

    def delete(self, event_id: int) -> tuple[bool, Optional[str]]:
        """Soft delete an event."""
        logger.info("Deleting event: id=%s", event_id)
        
        if not self.repo.get_by_id(event_id):
             return False, "Event not found"

        self.repo.soft_delete(event_id)
        return True, None
        
    def get_by_id(self, event_id: int) -> Optional[EventResponse]:
        """Get event by ID."""
        event = self.repo.get_by_id(event_id)
        if event:
            return EventResponse(**event)
        return None
