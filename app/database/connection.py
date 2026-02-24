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
            active_term_id INTEGER,
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

        CREATE TABLE IF NOT EXISTS terms (
            term_id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER NOT NULL,
            term_name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            activity_status INTEGER NOT NULL DEFAULT 1,
            term_img_url TEXT,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS class_terms (
            class_id INTEGER NOT NULL,
            term_id INTEGER NOT NULL,
            PRIMARY KEY (class_id, term_id),
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            FOREIGN KEY (term_id) REFERENCES terms(term_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS meal_menus (
            menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_id INTEGER NOT NULL,
            class_id INTEGER,
            menu_date TEXT NOT NULL,
            breakfast TEXT,
            lunch TEXT,
            dinner TEXT,
            breakfast_img_url TEXT,
            lunch_img_url TEXT,
            dinner_img_url TEXT,
            created_by INTEGER,
            created_date TEXT NOT NULL,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            UNIQUE (school_id, menu_date, class_id),
            FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT,
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES teachers(teacher_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'present',
            recorded_by INTEGER,
            recorded_at TEXT NOT NULL,
            notes TEXT,
            is_deleted INTEGER NOT NULL DEFAULT 0,
            UNIQUE (class_id, student_id, attendance_date),
            FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (recorded_by) REFERENCES teachers(teacher_id) ON DELETE SET NULL
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

    # Migration: if the schools table doesn't have the active_term_id column, add it
    cursor.execute("PRAGMA table_info(schools)")
    columns = [row[1] for row in cursor.fetchall()]
    if "active_term_id" not in columns:
        logger.info("Adding active_term_id column to schools table")
        cursor.execute("ALTER TABLE schools ADD COLUMN active_term_id INTEGER")
        logger.info("active_term_id column added to schools table successfully")

    # Migration: if meal_menus table exists with old schema, migrate to new schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meal_menus'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(meal_menus)")
        columns = [row[1] for row in cursor.fetchall()]
        if "meal_type" in columns:
            logger.info("Migrating meal_menus table from old schema to new schema")
            # Drop the old table and recreate with new schema
            cursor.executescript("""
                DROP TABLE IF EXISTS meal_menus;
                CREATE TABLE meal_menus (
                    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_id INTEGER NOT NULL,
                    class_id INTEGER,
                    menu_date TEXT NOT NULL,
                    breakfast TEXT,
                    lunch TEXT,
                    dinner TEXT,
                    breakfast_img_url TEXT,
                    lunch_img_url TEXT,
                    dinner_img_url TEXT,
                    created_by INTEGER,
                    created_date TEXT NOT NULL,
                    is_deleted INTEGER NOT NULL DEFAULT 0,
                    UNIQUE (school_id, menu_date, class_id),
                    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE RESTRICT,
                    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES teachers(teacher_id) ON DELETE SET NULL
                );
            """)
            logger.info("meal_menus table migrated successfully")

    conn.commit()
    conn.close()
    logger.info("Database schema initialised successfully")
