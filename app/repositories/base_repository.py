"""Base repository with common CRUD operations."""
import sqlite3
from datetime import datetime
from typing import Optional


def get_current_datetime() -> str:
    """Return current datetime as ISO string."""
    return datetime.utcnow().isoformat()


class BaseRepository:
    """Base repository class with common database operations."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.cursor = db.cursor()

    def commit(self):
        """Commit the current transaction."""
        self.db.commit()
