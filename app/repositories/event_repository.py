"""Repository layer for Class Events."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class EventRepository(BaseRepository):
    """Repository for Class Event database operations."""

    def create(
        self,
        class_id: int,
        title: str,
        event_date: str,
        description: Optional[str] = None,
        photo_url: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> dict:
        """Create a new event record."""
        logger.debug("Inserting event record: %s (class_id=%s)", title, class_id)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO class_events 
               (class_id, title, description, photo_url, event_date, created_by, created_date, is_deleted) 
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (class_id, title, description, photo_url, event_date, created_by, created_date),
        )
        self.commit()
        logger.trace("Event record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "event_id": self.cursor.lastrowid,
            "class_id": class_id,
            "title": title,
            "description": description,
            "photo_url": photo_url,
            "event_date": event_date,
            "created_by": created_by,
            "created_date": created_date,
        }

    def get_by_id(self, event_id: int) -> Optional[dict]:
        """Get an event by ID (excluding soft-deleted)."""
        logger.trace("SELECT event by id=%s", event_id)
        self.cursor.execute(
            "SELECT * FROM class_events WHERE event_id = ? AND is_deleted = 0",
            (event_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_by_class_id(self, class_id: int, page: int = 1, page_size: int = 10) -> tuple[list[dict], int]:
        """Get paginated events for a class."""
        logger.debug("Fetching events for class_id=%s", class_id)
        query = "SELECT * FROM class_events WHERE class_id = ? AND is_deleted = 0 ORDER BY event_date DESC"
        results, total = self.paginate(query, (class_id,), page, page_size)
        return results, total

    def update(self, event_id: int, **kwargs) -> Optional[dict]:
        """Update an event record."""
        logger.debug("Updating event record: id=%s, fields=%s", event_id, list(kwargs.keys()))
        existing = self.get_by_id(event_id)
        if not existing:
            return None

        fields = ["title", "description", "photo_url", "event_date"]
        update_fields = []
        params = []
        
        for key in fields:
            if key in kwargs: # Allow setting to None/Null if passed
                update_fields.append(f"{key} = ?")
                params.append(kwargs[key])
        
        if not update_fields:
            return existing

        params.append(event_id)
        query = f"UPDATE class_events SET {', '.join(update_fields)} WHERE event_id = ? AND is_deleted = 0"
        
        self.cursor.execute(query, tuple(params))
        self.commit()
        
        # Return updated record
        return self.get_by_id(event_id)

    def soft_delete(self, event_id: int) -> bool:
        """Soft delete an event."""
        logger.debug("Soft-deleting event: id=%s", event_id)
        if not self.get_by_id(event_id):
            return False

        self.cursor.execute(
            "UPDATE class_events SET is_deleted = 1 WHERE event_id = ?",
            (event_id,),
        )
        self.commit()
        return True
