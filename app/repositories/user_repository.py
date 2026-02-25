"""Repository layer for User and RefreshToken entities."""
import sqlite3
from typing import Optional

from app.logger import get_logger
from app.repositories.base_repository import BaseRepository, get_current_datetime

logger = get_logger(__name__)


class UserRepository(BaseRepository):
    """Repository for User database operations."""

    def create(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        role: str,
        school_id: Optional[int] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> dict:
        """Create a new user record."""
        logger.debug("Inserting user record: %s (%s)", email, role)
        created_date = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO users
               (email, password_hash, first_name, last_name, role,
                school_id, phone, address, created_date, is_deleted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (email, password_hash, first_name, last_name, role,
             school_id, phone, address, created_date),
        )
        self.commit()
        logger.trace("User record inserted with rowid=%s", self.cursor.lastrowid)
        return {
            "user_id": self.cursor.lastrowid,
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "school_id": school_id,
            "phone": phone,
            "address": address,
            "created_date": created_date,
        }

    def get_by_id(self, user_id: int) -> Optional[dict]:
        """Get a user by ID (excluding soft-deleted)."""
        logger.trace("SELECT user by id=%s", user_id)
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id = ? AND is_deleted = 0",
            (user_id,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_by_email(self, email: str) -> Optional[dict]:
        """Get a user by email (excluding soft-deleted)."""
        logger.trace("SELECT user by email=%s", email)
        self.cursor.execute(
            "SELECT * FROM users WHERE email = ? AND is_deleted = 0",
            (email,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def email_exists(self, email: str) -> bool:
        """Check if an email is already registered (not soft-deleted)."""
        logger.trace("Checking if email exists: %s", email)
        return self.get_by_email(email) is not None

    def exists(self, user_id: int) -> bool:
        """Check if a user exists (not soft-deleted)."""
        return self.get_by_id(user_id) is not None

    def soft_delete(self, user_id: int) -> bool:
        """Soft delete a user by setting is_deleted = 1."""
        logger.debug("Soft-deleting user: id=%s", user_id)
        existing = self.get_by_id(user_id)
        if not existing:
            return False
        self.cursor.execute(
            "UPDATE users SET is_deleted = 1 WHERE user_id = ?",
            (user_id,),
        )
        self.commit()
        logger.trace("User soft-deleted in DB: id=%s", user_id)
        return True

    # --- Refresh Token operations ---

    def store_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: str,
    ) -> dict:
        """Store a hashed refresh token."""
        logger.debug("Storing refresh token for user_id=%s", user_id)
        created_at = get_current_datetime()
        self.cursor.execute(
            """INSERT INTO refresh_tokens
               (user_id, token_hash, expires_at, created_at, revoked)
               VALUES (?, ?, ?, ?, 0)""",
            (user_id, token_hash, expires_at, created_at),
        )
        self.commit()
        return {
            "token_id": self.cursor.lastrowid,
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "created_at": created_at,
            "revoked": 0,
        }

    def get_active_refresh_tokens(self, user_id: int) -> list[dict]:
        """Get all active (non-revoked) refresh tokens for a user."""
        logger.trace("SELECT active refresh tokens for user_id=%s", user_id)
        self.cursor.execute(
            "SELECT * FROM refresh_tokens WHERE user_id = ? AND revoked = 0",
            (user_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def revoke_refresh_token(self, token_id: int) -> bool:
        """Revoke a specific refresh token."""
        logger.debug("Revoking refresh token: token_id=%s", token_id)
        self.cursor.execute(
            "UPDATE refresh_tokens SET revoked = 1 WHERE token_id = ?",
            (token_id,),
        )
        self.commit()
        return self.cursor.rowcount > 0

    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all refresh tokens for a user. Returns count of revoked tokens."""
        logger.debug("Revoking all refresh tokens for user_id=%s", user_id)
        self.cursor.execute(
            "UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ? AND revoked = 0",
            (user_id,),
        )
        self.commit()
        count = self.cursor.rowcount
        logger.trace("Revoked %d refresh token(s) for user_id=%s", count, user_id)
        return count

    # --- Teacher class assignments ---

    def assign_teacher_to_class(self, user_id: int, class_id: int) -> None:
        """Assign a teacher (user_id) to a class (idempotent)."""
        logger.debug("Assigning teacher user_id=%s to class_id=%s", user_id, class_id)
        self.cursor.execute(
            "INSERT OR IGNORE INTO teacher_classes (user_id, class_id) VALUES (?, ?)",
            (user_id, class_id),
        )
        self.commit()
        logger.trace("Teacher assignment recorded: user_id=%s, class_id=%s", user_id, class_id)

    def unassign_teacher_from_class(self, user_id: int, class_id: int) -> None:
        """Unassign a teacher (user_id) from a class."""
        logger.debug("Unassigning teacher user_id=%s from class_id=%s", user_id, class_id)
        self.cursor.execute(
            "DELETE FROM teacher_classes WHERE user_id = ? AND class_id = ?",
            (user_id, class_id),
        )
        self.commit()
        logger.trace("Teacher assignment removed: user_id=%s, class_id=%s", user_id, class_id)

    def get_teacher_class_ids(self, user_id: int) -> list[int]:
        """Get class IDs assigned to a teacher (user_id)."""
        logger.trace("Fetching class IDs for teacher user_id=%s", user_id)
        self.cursor.execute(
            """SELECT tc.class_id FROM teacher_classes tc
               JOIN classes c ON tc.class_id = c.class_id
               WHERE tc.user_id = ? AND c.is_deleted = 0""",
            (user_id,),
        )
        class_ids = [row["class_id"] for row in self.cursor.fetchall()]
        logger.trace("Class IDs for teacher user_id=%s: %s", user_id, class_ids)
        return class_ids

    def replace_teacher_classes(self, user_id: int, class_ids: list[int]) -> list[int]:
        """
        Replace all class assignments for a teacher with the given list.
        
        Removes existing assignments and inserts the new ones.
        Returns the final list of class_ids assigned.
        """
        logger.debug("Replacing class assignments for teacher user_id=%s with class_ids=%s", user_id, class_ids)
        # Remove all existing assignments
        self.cursor.execute(
            "DELETE FROM teacher_classes WHERE user_id = ?",
            (user_id,),
        )
        # Insert new assignments
        for class_id in class_ids:
            self.cursor.execute(
                "INSERT OR IGNORE INTO teacher_classes (user_id, class_id) VALUES (?, ?)",
                (user_id, class_id),
            )
        self.commit()
        logger.info("Teacher user_id=%s now assigned to %d class(es): %s", user_id, len(class_ids), class_ids)
        return class_ids

    def get_teachers_by_class_id(self, class_id: int) -> list[dict]:
        """Get teacher users assigned to a class."""
        logger.trace("Fetching teacher users for class_id=%s", class_id)
        self.cursor.execute(
            """SELECT u.* FROM users u
               JOIN teacher_classes tc ON u.user_id = tc.user_id
               WHERE tc.class_id = ? AND u.is_deleted = 0""",
            (class_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    # --- Parent/student links ---

    def link_parent_to_student(self, user_id: int, student_id: int) -> None:
        """Link a parent user to a student (idempotent)."""
        logger.debug("Linking parent user_id=%s to student_id=%s", user_id, student_id)
        self.cursor.execute(
            "INSERT OR IGNORE INTO student_parents (student_id, user_id) VALUES (?, ?)",
            (student_id, user_id),
        )
        self.commit()
        logger.trace("Parent link recorded: user_id=%s, student_id=%s", user_id, student_id)

    def unlink_parent_from_student(self, user_id: int, student_id: int) -> None:
        """Unlink a parent user from a student."""
        logger.debug("Unlinking parent user_id=%s from student_id=%s", user_id, student_id)
        self.cursor.execute(
            "DELETE FROM student_parents WHERE student_id = ? AND user_id = ?",
            (student_id, user_id),
        )
        self.commit()
        logger.trace("Parent link removed: user_id=%s, student_id=%s", user_id, student_id)

    def get_student_ids_for_parent(self, user_id: int) -> list[int]:
        """Get student IDs linked to a parent user."""
        logger.trace("Fetching student IDs for parent user_id=%s", user_id)
        self.cursor.execute(
            """SELECT sp.student_id FROM student_parents sp
               JOIN students s ON sp.student_id = s.student_id
               WHERE sp.user_id = ? AND s.is_deleted = 0""",
            (user_id,),
        )
        student_ids = [row["student_id"] for row in self.cursor.fetchall()]
        logger.trace("Student IDs for parent user_id=%s: %s", user_id, student_ids)
        return student_ids

    def get_parents_by_student_id(self, student_id: int) -> list[dict]:
        """Get parent users linked to a student."""
        logger.trace("Fetching parent users for student_id=%s", student_id)
        self.cursor.execute(
            """SELECT u.* FROM users u
               JOIN student_parents sp ON u.user_id = sp.user_id
               WHERE sp.student_id = ? AND u.is_deleted = 0""",
            (student_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def get_users_by_role(self, role: str, school_id: Optional[int] = None) -> list[dict]:
        """Get users by role (optionally scoped to a school)."""
        logger.trace("Fetching users by role=%s (school_id=%s)", role, school_id)
        if school_id is None:
            self.cursor.execute(
                "SELECT * FROM users WHERE role = ? AND is_deleted = 0",
                (role,),
            )
        else:
            self.cursor.execute(
                "SELECT * FROM users WHERE role = ? AND school_id = ? AND is_deleted = 0",
                (role, school_id),
            )
        return [dict(row) for row in self.cursor.fetchall()]

    def update_contact_info(self, user_id: int, phone: Optional[str], address: Optional[str]) -> Optional[dict]:
        """Update phone/address for a user."""
        logger.debug("Updating contact info for user_id=%s", user_id)
        existing = self.get_by_id(user_id)
        if not existing:
            return None
        if phone is not None:
            existing["phone"] = phone
        if address is not None:
            existing["address"] = address
        self.cursor.execute(
            "UPDATE users SET phone = ?, address = ? WHERE user_id = ?",
            (existing.get("phone"), existing.get("address"), user_id),
        )
        self.commit()
        return existing
