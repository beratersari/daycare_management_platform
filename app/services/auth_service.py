"""Service layer for authentication and authorization."""
import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext

from app.logger import get_logger
from app.repositories.user_repository import UserRepository
from app.repositories.school_repository import SchoolRepository
from app.schemas.auth import (
    TokenResponse,
    UserRegister,
    UserResponse,
    UserRole,
)

logger = get_logger(__name__)

# JWT configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "kinder-tracker-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _hash_token(token: str) -> str:
    """Hash a refresh token using SHA-256 for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def _create_access_token(user: dict) -> str:
    """Create a short-lived JWT access token (15 minutes)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user["user_id"],
        "role": user["role"],
        "school_id": user.get("school_id"),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.trace("Access token created for user_id=%s, expires=%s", user["user_id"], expire.isoformat())
    return token


def _create_refresh_token() -> str:
    """Generate a cryptographically secure random refresh token."""
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token. Returns payload or None."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        logger.trace("Access token decoded successfully for user_id=%s", payload.get("sub"))
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Access token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning("Invalid access token: %s", str(e))
        return None


class AuthService:
    """Service for authentication and authorization business logic."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.user_repo = UserRepository(db)
        self.school_repo = SchoolRepository(db)
        logger.trace("AuthService initialised")

    def register(self, data: UserRegister) -> tuple[Optional[UserResponse], Optional[str]]:
        """Register a new user."""
        logger.info("Registering user: %s (role=%s)", data.email, data.role.value)

        # Check if email already exists
        if self.user_repo.email_exists(data.email):
            logger.warning("Registration failed — email already exists: %s", data.email)
            return None, "Email already registered"

        # Validate school_id for non-ADMIN roles
        if data.role != UserRole.ADMIN:
            if data.school_id is None:
                logger.warning("Registration failed — school_id required for role %s", data.role.value)
                return None, f"school_id is required for {data.role.value} role"
            if not self.school_repo.exists(data.school_id):
                logger.warning("Registration failed — school not found: school_id=%s", data.school_id)
                return None, "School not found"

        # Hash password and create user
        password_hash = _hash_password(data.password)
        user = self.user_repo.create(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role.value,
            school_id=data.school_id,
            phone=data.phone,
            address=data.address,
        )

        logger.info("User registered successfully: user_id=%s, role=%s", user["user_id"], data.role.value)
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            school_id=user["school_id"],
            phone=user.get("phone"),
            address=user.get("address"),
            created_date=user["created_date"],
        ), None

    def login(self, email: str, password: str) -> tuple[Optional[TokenResponse], Optional[str]]:
        """Authenticate a user and return access + refresh tokens."""
        logger.info("Login attempt for email: %s", email)

        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning("Login failed — user not found: %s", email)
            return None, "Invalid email or password"

        if not _verify_password(password, user["password_hash"]):
            logger.warning("Login failed — wrong password for: %s", email)
            return None, "Invalid email or password"

        # Create tokens
        access_token = _create_access_token(user)
        refresh_token = _create_refresh_token()

        # Store hashed refresh token
        refresh_hash = _hash_token(refresh_token)
        expires_at = (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
        self.user_repo.store_refresh_token(
            user_id=user["user_id"],
            token_hash=refresh_hash,
            expires_at=expires_at,
        )

        logger.info("Login successful for user_id=%s", user["user_id"])
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ), None

    def refresh(self, refresh_token: str) -> tuple[Optional[TokenResponse], Optional[str]]:
        """
        Exchange a valid refresh token for a new access + refresh token pair.
        Implements refresh token rotation: the old token is revoked and a new one issued.
        """
        logger.info("Refresh token exchange attempt")

        token_hash = _hash_token(refresh_token)

        # Search all users' active tokens for a match
        # (We hash the incoming token and compare with stored hashes)
        self.user_repo.cursor.execute(
            """SELECT rt.*, u.user_id, u.email, u.first_name, u.last_name,
                      u.role, u.school_id
               FROM refresh_tokens rt
               JOIN users u ON rt.user_id = u.user_id
               WHERE rt.token_hash = ? AND rt.revoked = 0 AND u.is_deleted = 0""",
            (token_hash,),
        )
        row = self.user_repo.cursor.fetchone()
        if not row:
            logger.warning("Refresh failed — token not found or revoked")
            return None, "Invalid or expired refresh token"

        record = dict(row)

        # Check expiry
        expires_at = datetime.fromisoformat(record["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            logger.warning("Refresh failed — token expired for user_id=%s", record["user_id"])
            # Revoke the expired token
            self.user_repo.revoke_refresh_token(record["token_id"])
            return None, "Refresh token has expired"

        # Revoke the old refresh token (rotation)
        self.user_repo.revoke_refresh_token(record["token_id"])

        # Build user dict for token creation
        user = {
            "user_id": record["user_id"],
            "email": record["email"],
            "first_name": record["first_name"],
            "last_name": record["last_name"],
            "role": record["role"],
            "school_id": record["school_id"],
        }

        # Issue new token pair
        new_access_token = _create_access_token(user)
        new_refresh_token = _create_refresh_token()
        new_refresh_hash = _hash_token(new_refresh_token)
        new_expires_at = (datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()

        self.user_repo.store_refresh_token(
            user_id=user["user_id"],
            token_hash=new_refresh_hash,
            expires_at=new_expires_at,
        )

        logger.info("Refresh successful for user_id=%s — new tokens issued", user["user_id"])
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ), None

    def logout(self, user_id: int) -> tuple[bool, Optional[str]]:
        """Revoke all refresh tokens for a user (logout from all devices)."""
        logger.info("Logout for user_id=%s — revoking all refresh tokens", user_id)
        if not self.user_repo.exists(user_id):
            logger.warning("Logout failed — user not found: user_id=%s", user_id)
            return False, "User not found"

        count = self.user_repo.revoke_all_user_tokens(user_id)
        logger.info("Logout successful for user_id=%s — %d token(s) revoked", user_id, count)
        return True, None

    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Get user info by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        return UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            role=user["role"],
            school_id=user["school_id"],
            phone=user.get("phone"),
            address=user.get("address"),
            created_date=user["created_date"],
        )
