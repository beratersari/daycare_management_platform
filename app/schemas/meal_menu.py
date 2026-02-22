"""DTO schemas for Meal Menu entity."""
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


class MealMenuCreate(BaseModel):
    school_id: int = Field(..., examples=[1], description="ID of the school this menu belongs to")
    class_id: Optional[int] = Field(None, examples=[1], description="ID of the class (None means school-wide menu)")
    menu_date: str = Field(..., examples=["2024-09-01"], description="Date in YYYY-MM-DD format")
    breakfast: Optional[str] = Field(None, examples=["Oatmeal with fruit"], description="Breakfast description")
    lunch: Optional[str] = Field(None, examples=["Chicken nuggets with rice"], description="Lunch description")
    dinner: Optional[str] = Field(None, examples=["Pasta with vegetables"], description="Dinner description")
    breakfast_img_url: Optional[str] = Field(None, examples=["https://example.com/breakfast.jpg"], description="URL to breakfast image")
    lunch_img_url: Optional[str] = Field(None, examples=["https://example.com/lunch.jpg"], description="URL to lunch image")
    dinner_img_url: Optional[str] = Field(None, examples=["https://example.com/dinner.jpg"], description="URL to dinner image")

    @field_validator("menu_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format (YYYY-MM-DD)."""
        logger.trace("Validating menu date format: %s", v)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            logger.warning("Invalid menu date format: %s", v)
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")
        return v

    @field_validator("breakfast_img_url", "lunch_img_url", "dinner_img_url")
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


class MealMenuUpdate(BaseModel):
    class_id: Optional[int] = Field(None, examples=[1], description="ID of the class (None means school-wide menu)")
    menu_date: Optional[str] = Field(None, examples=["2024-09-01"], description="Date in YYYY-MM-DD format")
    breakfast: Optional[str] = Field(None, examples=["Oatmeal with fruit"], description="Breakfast description")
    lunch: Optional[str] = Field(None, examples=["Chicken nuggets with rice"], description="Lunch description")
    dinner: Optional[str] = Field(None, examples=["Pasta with vegetables"], description="Dinner description")
    breakfast_img_url: Optional[str] = Field(None, examples=["https://example.com/breakfast.jpg"], description="URL to breakfast image")
    lunch_img_url: Optional[str] = Field(None, examples=["https://example.com/lunch.jpg"], description="URL to lunch image")
    dinner_img_url: Optional[str] = Field(None, examples=["https://example.com/dinner.jpg"], description="URL to dinner image")

    @field_validator("menu_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format (YYYY-MM-DD)."""
        if v is None:
            return v
        logger.trace("Validating menu date format: %s", v)
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            logger.warning("Invalid menu date format: %s", v)
            raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")
        return v

    @field_validator("breakfast_img_url", "lunch_img_url", "dinner_img_url")
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


class MealMenuResponse(BaseModel):
    menu_id: int
    school_id: int
    class_id: Optional[int] = None
    menu_date: str
    breakfast: Optional[str] = None
    lunch: Optional[str] = None
    dinner: Optional[str] = None
    breakfast_img_url: Optional[str] = None
    lunch_img_url: Optional[str] = None
    dinner_img_url: Optional[str] = None
    created_by: Optional[int] = None
    created_date: str
    message: Optional[str] = None