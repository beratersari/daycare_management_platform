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

    def paginate(self, query: str, params: tuple = (), page: int = 1, page_size: int = 10) -> tuple[list[dict], int]:
        """
        Execute a SELECT query with pagination.
        
        Args:
            query: SQL SELECT query (should not include LIMIT/OFFSET)
            params: Query parameters
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (paginated_results, total_count)
        """
        logger.trace("Paginating query: page=%d, page_size=%d", page, page_size)
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM ({query})"
        self.cursor.execute(count_query, params)
        total = self.cursor.fetchone()["count"]
        logger.trace("Total count for query: %d", total)
        
        # Get paginated results
        offset = (page - 1) * page_size
        paginated_query = f"{query} LIMIT ? OFFSET ?"
        self.cursor.execute(paginated_query, params + (page_size, offset))
        results = [dict(row) for row in self.cursor.fetchall()]
        logger.trace("Retrieved %d results for page %d", len(results), page)
        
        return results, total
