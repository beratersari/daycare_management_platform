"""Base repository with common CRUD operations."""
import sqlite3
from datetime import datetime
from typing import Optional

from app.logger import get_logger

logger = get_logger(__name__)


def get_current_datetime() -> str:
    """Return current datetime as ISO string."""
    now = datetime.utcnow().isoformat()
    logger.trace("Generated current datetime: %s", now)
    return now


class BaseRepository:
    """Base repository class with common database operations."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.cursor = db.cursor()
        logger.trace("%s initialised", self.__class__.__name__)

    def commit(self):
        """Commit the current transaction."""
        logger.trace("Committing transaction (%s)", self.__class__.__name__)
        self.db.commit()
