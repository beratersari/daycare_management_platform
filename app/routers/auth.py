"""Router layer for Authentication endpoints."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database.connection import get_db
from app.logger import get_logger
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.auth.dependencies import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_service(db: sqlite3.Connection = Depends(get_db)) -> AuthService:
    logger.trace("Creating AuthService dependency")
    return AuthService(db)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    data: UserRegister,
    service: AuthService = Depends(get_service),
):
    """Register a new user account."""
    logger.info("POST /api/v1/auth/register — registration request for %s", data.email)
    result, error = service.register(data)
    if error:
        if "not found" in error.lower():
            logger.warning("POST /api/v1/auth/register — 404: %s", error)
            raise HTTPException(status_code=404, detail=error)
        logger.warning("POST /api/v1/auth/register — 400: %s", error)
        raise HTTPException(status_code=400, detail=error)
    return result


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    service: AuthService = Depends(get_service),
):
    """Authenticate and receive access + refresh tokens."""
    logger.info("POST /api/v1/auth/login — login request for %s", data.email)
    result, error = service.login(data.email, data.password)
    if error:
        logger.warning("POST /api/v1/auth/login — 401: %s", error)
        raise HTTPException(status_code=401, detail=error)
    return result


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_service),
):
    """Exchange a refresh token for a new access + refresh token pair (rotation)."""
    logger.info("POST /api/v1/auth/refresh — token refresh request")
    result, error = service.refresh(data.refresh_token)
    if error:
        logger.warning("POST /api/v1/auth/refresh — 401: %s", error)
        raise HTTPException(status_code=401, detail=error)
    return result


@router.post("/logout", status_code=204)
def logout(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_service),
):
    """Logout — revoke all refresh tokens for the current user."""
    user_id = current_user["sub"]
    logger.info("POST /api/v1/auth/logout — logout request for user_id=%s", user_id)
    success, error = service.logout(user_id)
    if not success:
        logger.warning("POST /api/v1/auth/logout — 400: %s", error)
        raise HTTPException(status_code=400, detail=error)
    return None


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_service),
):
    """Get the current authenticated user's profile."""
    user_id = current_user["sub"]
    logger.info("GET /api/v1/auth/me — profile request for user_id=%s", user_id)
    result = service.get_user_by_id(user_id)
    if not result:
        logger.warning("GET /api/v1/auth/me — 404 user not found")
        raise HTTPException(status_code=404, detail="User not found")
    return result
