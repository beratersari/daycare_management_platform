import sqlite3
import os

from app.logger import get_logger

logger = get_logger(__name__)

DB_PATH = "/testbed/db/kinder_tracker.db"


def get_connection() -> sqlite3.Connection:
    """Get a new SQLite connection with row_factory set."""
    logger.trace("Opening SQLite connection to %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """FastAPI dependency that yields a database connection."""
    logger.trace("get_db: yielding new connection")
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
        logger.trace("get_db: connection closed")


def init_db():
    """Initialize the database schema."""
    logger.info("Initialising database at %s", DB_PATH)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS schools (
            school_id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            director_name TEXT,
            license_number TEXT,
            capacity INTEGER,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS parents (
            parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            school_id INTEGER NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS classes (
            class_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            school_id INTEGER NOT NULL,
            capacity INTEGER,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            school_id INTEGER NOT NULL,
            class_id INTEGER,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            school_id INTEGER NOT NULL,
            student_photo TEXT,
            date_of_birth TEXT,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS student_classes (
            student_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            PRIMARY KEY (student_id, class_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_parents (
            student_id INTEGER NOT NULL,
            parent_id INTEGER NOT NULL,
            PRIMARY KEY (student_id, parent_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES parents(parent_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_allergies (
            allergy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            allergy_name TEXT NOT NULL,
            severity TEXT,
            notes TEXT,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS student_hw_info (
            hw_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            measurement_date TEXT NOT NULL,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
    """)

    # Migration: if the students table still has the legacy class_id column,
    # migrate data into student_classes and rebuild the table without it.
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    if "class_id" in columns:
        logger.info("Migrating legacy class_id column from students table to student_classes join table")
        cursor.executescript("""
            INSERT OR IGNORE INTO student_classes (student_id, class_id)
                SELECT student_id, class_id FROM students
                WHERE class_id IS NOT NULL AND is_deleted = 0;

            CREATE TABLE students_new (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                school_id INTEGER NOT NULL,
                student_photo TEXT,
                date_of_birth TEXT,
                created_date TEXT NOT NULL,
                is_deleted INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT
            );

            INSERT INTO students_new
                SELECT student_id, first_name, last_name, school_id,
                       student_photo, date_of_birth, created_date, is_deleted
                FROM students;

            DROP TABLE students;
            ALTER TABLE students_new RENAME TO students;
        """)
        logger.info("Migration of class_id column completed successfully")

    conn.commit()
    conn.close()
    logger.info("Database schema initialised successfully")
