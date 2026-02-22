"""DTO schemas for Term entity."""
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

from app.logger import get_logger

logger = get_logger(__name__)

# Regex patterns for validation
URL_REGEX = re.compile(
    r"^(https?://)?([a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/[^\s]*)?$|^$"
)


class TermCreate(BaseModel):
    school_id: int = Field(..., examples=[1], description="ID of the school this term belongs to")
    term_name: str = Field(..., examples=["Fall 2024"], description="Name of the term")
    start_date: str = Field(..., examples=["2024-09-01"], description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, examples=["2024-12-31"], description="End date in YYYY-MM-DD format. If empty, term is considered active")
    activity_status: bool = Field(True, examples=[True], description="Whether the term is active")
    term_img_url: Optional[str] = Field(None, examples=["https://example.com/term.jpg"], description="URL to term image")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format (YYYY-MM-DD)."""
        if v is None:
            return v
        logger.trace("Validating date format: %s", v)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            logger.warning("Invalid date format: %s", v)
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")
        return v

    @field_validator("term_img_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format."""
        if v is None or v == "":
            return v
        logger.trace("Validating URL: %s", v)
        if not URL_REGEX.match(v):
            logger.warning("Invalid URL format: %s", v)
            raise ValueError("Invalid URL format")
        return v


class TermUpdate(BaseModel):
    term_name: Optional[str] = Field(None, examples=["Fall 2024"], description="Name of the term")
    start_date: Optional[str] = Field(None, examples=["2024-09-01"], description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, examples=["2024-12-31"], description="End date in YYYY-MM-DD format")
    activity_status: Optional[bool] = Field(None, examples=[True], description="Whether the term is active")
    term_img_url: Optional[str] = Field(None, examples=["https://example.com/term.jpg"], description="URL to term image")

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format (YYYY-MM-DD)."""
        if v is None:
            return v
        logger.trace("Validating date format: %s", v)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            logger.warning("Invalid date format: %s", v)
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")
        return v

    @field_validator("term_img_url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format."""
        if v is None or v == "":
            return v
        logger.trace("Validating URL: %s", v)
        if not URL_REGEX.match(v):
            logger.warning("Invalid URL format: %s", v)
            raise ValueError("Invalid URL format")
        return v


class TermResponse(BaseModel):
    term_id: int
    school_id: int
    term_name: str
    start_date: str
    end_date: Optional[str] = None
    activity_status: bool
    term_img_url: Optional[str] = None
    created_date: str
