import sqlite3
import os

DB_PATH = "/testbed/db/kinder_tracker.db"


def get_connection() -> sqlite3.Connection:
    """Get a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """FastAPI dependency that yields a database connection."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database schema."""
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
            class_id INTEGER,
            student_photo TEXT,
            date_of_birth TEXT,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE SET NULL
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

    conn.commit()
    conn.close()
