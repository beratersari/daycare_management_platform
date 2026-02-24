"""FastAPI dependencies for authentication and role-based authorization."""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.logger import get_logger
from app.services.auth_service import decode_access_token
from app.schemas.auth import UserRole

logger = get_logger(__name__)

# Bearer token security scheme
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Decode the Bearer JWT token and return the payload as the current user context.
    Raises 401 if the token is missing, invalid, or expired.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Authentication failed — invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.trace("Authenticated user_id=%s role=%s", payload.get("sub"), payload.get("role"))
    return payload


class RoleChecker:
    """
    Dependency class that checks whether the current user has one of the allowed roles.
    Usage:
        require_admin = RoleChecker([UserRole.ADMIN])
        @router.get("/admin-only", dependencies=[Depends(require_admin)])
    """

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = [r.value for r in allowed_roles]

    def __call__(self, current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in self.allowed_roles:
            logger.warning(
                "Authorization failed — user_id=%s role=%s not in %s",
                current_user.get("sub"),
                user_role,
                self.allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user


def require_school_access(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependency that ensures the user has access based on their role.
    ADMIN can access everything.
    Other roles must have a school_id in their token.
    Returns the current_user payload.
    """
    if current_user.get("role") == UserRole.ADMIN.value:
        return current_user
    if current_user.get("school_id") is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No school associated with your account",
        )
    return current_user


def check_school_ownership(current_user: dict, school_id: int) -> None:
    """
    Utility: verify that the current user has access to the given school_id.
    ADMIN can access any school. Others must match their own school_id.
    Raises 403 if access is denied.
    """
    if current_user.get("role") == UserRole.ADMIN.value:
        return
    if current_user.get("school_id") != school_id:
        logger.warning(
            "School access denied — user_id=%s (school_id=%s) tried to access school_id=%s",
            current_user.get("sub"),
            current_user.get("school_id"),
            school_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this school's resources",
        )


# Pre-built role checker instances for convenience
require_admin = RoleChecker([UserRole.ADMIN])
require_admin_or_director = RoleChecker([UserRole.ADMIN, UserRole.DIRECTOR])
require_admin_director_or_teacher = RoleChecker([UserRole.ADMIN, UserRole.DIRECTOR, UserRole.TEACHER])
require_any_authenticated = RoleChecker([UserRole.ADMIN, UserRole.DIRECTOR, UserRole.TEACHER, UserRole.PARENT])
