import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta

# DB path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kinder_tracker.db")


def ensure_mock_users(cursor, school_id: int, now: str) -> dict:
    """Ensure core mock users exist and return their IDs."""
    users = {
        "admin@example.com": {
            "first_name": "System",
            "last_name": "Administrator",
            "role": "ADMIN",
            "password": "admin123",
            "phone": "555-000-0001",
            "address": "1 Admin Plaza, System City",
            "school_id": None,
        },
        "director@example.com": {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "role": "DIRECTOR",
            "password": "director123",
            "phone": "555-000-0002",
            "address": "42 Director Drive, Management Town",
            "school_id": school_id,
        },
        "teacher@example.com": {
            "first_name": "Emily",
            "last_name": "Davis",
            "role": "TEACHER",
            "password": "teacher123",
            "phone": "555-000-0003",
            "address": "101 Teacher Terrace, Classroom City",
            "school_id": school_id,
        },
        "parent@example.com": {
            "first_name": "Michael",
            "last_name": "Brown",
            "role": "PARENT",
            "password": "parent123",
            "phone": "555-000-0004",
            "address": "789 Family Lane, Parentville",
            "school_id": school_id,
        },
        "student@example.com": {
            "first_name": "Billy",
            "last_name": "Kid",
            "role": "STUDENT",
            "password": "student123",
            "phone": "555-000-0005",
            "address": "123 Kid St",
            "school_id": school_id,
        },
    }

    ids: dict[str, int] = {}
    for email, details in users.items():
        cursor.execute("SELECT user_id FROM users WHERE email = ? AND is_deleted = 0", (email,))
        row = cursor.fetchone()
        if row:
            ids[email] = row["user_id"]
            continue
        password_hash = hash_password(details["password"])
        cursor.execute(
            """
            INSERT INTO users (email, password_hash, first_name, last_name, role, school_id, phone, address, created_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                email,
                password_hash,
                details["first_name"],
                details["last_name"],
                details["role"],
                details["school_id"],
                details["phone"],
                details["address"],
                now,
            ),
        )
        ids[email] = cursor.lastrowid
    return ids


def ensure_class(cursor, school_id: int, now: str, name: str, capacity: int) -> int:
    cursor.execute(
        "SELECT class_id FROM classes WHERE class_name = ? AND school_id = ? AND is_deleted = 0",
        (name, school_id),
    )
    row = cursor.fetchone()
    if row:
        return row["class_id"]
    cursor.execute(
        "INSERT INTO classes (class_name, school_id, capacity, created_date, is_deleted) VALUES (?, ?, ?, ?, 0)",
        (name, school_id, capacity, now),
    )
    return cursor.lastrowid


def ensure_student(cursor, school_id: int, now: str, first_name: str, last_name: str, dob: str) -> int:
    cursor.execute(
        "SELECT student_id FROM students WHERE first_name = ? AND last_name = ? AND school_id = ? AND is_deleted = 0",
        (first_name, last_name, school_id),
    )
    row = cursor.fetchone()
    if row:
        return row["student_id"]
    cursor.execute(
        "INSERT INTO students (first_name, last_name, school_id, date_of_birth, created_date, is_deleted) VALUES (?, ?, ?, ?, ?, 0)",
        (first_name, last_name, school_id, dob, now),
    )
    return cursor.lastrowid


def ensure_student_link(cursor, student_id: int, class_id: int, parent_user_id: int | None = None) -> None:
    cursor.execute("INSERT OR IGNORE INTO student_classes (student_id, class_id) VALUES (?, ?)", (student_id, class_id))
    if parent_user_id:
        cursor.execute("INSERT OR IGNORE INTO student_parents (student_id, user_id) VALUES (?, ?)", (student_id, parent_user_id))


def ensure_teacher_link(cursor, teacher_user_id: int, class_id: int) -> None:
    cursor.execute("INSERT OR IGNORE INTO teacher_classes (user_id, class_id) VALUES (?, ?)", (teacher_user_id, class_id))


def ensure_meal_menus(cursor, school_id: int, class_id: int, teacher_user_id: int, today: str, tomorrow: str, now: str) -> None:
    meals = [
        (school_id, None, today, "Oatmeal with berries", "Turkey and cheese sandwich", "Pasta with tomato sauce", teacher_user_id, now),
        (school_id, class_id, today, "Yogurt and granola", "Chicken salad", "Grilled cheese", teacher_user_id, now),
        (school_id, None, tomorrow, "Pancakes", "Beef stew", "Chicken nuggets", teacher_user_id, now),
    ]
    for meal in meals:
        cursor.execute(
            """
            INSERT OR IGNORE INTO meal_menus (school_id, class_id, menu_date, breakfast, lunch, dinner, created_by, created_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            meal,
        )


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def seed():
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"Seeding more data to {DB_PATH}...")

    # 1. Get existing school
    cursor.execute("SELECT school_id FROM schools WHERE is_deleted = 0 LIMIT 1")
    school_row = cursor.fetchone()
    if not school_row:
        print("No school found, creating one...")
        cursor.execute(
            """
            INSERT INTO schools (school_name, address, phone, email, director_name, license_number, capacity, created_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                "Sunshine Daycare Center",
                "123 Learning Lane, Education City",
                "555-123-4567",
                "director@sunshine.edu",
                "Jane Smith",
                "DC-2024-001",
                50,
                now,
            ),
        )
        school_id = cursor.lastrowid
    else:
        school_id = school_row["school_id"]

    user_ids = ensure_mock_users(cursor, school_id, now)

    # 2. Add classes
    class_a_id = ensure_class(cursor, school_id, now, "Preschool A", 20)
    class_b_id = ensure_class(cursor, school_id, now, "Toddler B", 15)
    print(f"Ensured classes: A({class_a_id}), B({class_b_id})")

    # 3. Link teacher to class
    teacher_user_id = user_ids["teacher@example.com"]
    parent_user_id = user_ids["parent@example.com"]
    ensure_teacher_link(cursor, teacher_user_id, class_a_id)
    print(f"Linked teacher to class {class_a_id}")

    # 4. Add students (in students table)
    student_billy_id = ensure_student(cursor, school_id, now, "Billy", "Kid", "2020-05-15")
    student_sally_id = ensure_student(cursor, school_id, now, "Sally", "Student", "2021-02-10")
    print(f"Ensured students: {student_billy_id}, {student_sally_id}")

    # 5. Link students to parent and classes
    ensure_student_link(cursor, student_billy_id, class_a_id, parent_user_id)
    ensure_student_link(cursor, student_sally_id, class_b_id, parent_user_id)
    print("Linked students to classes and parent")

    # 6. Add meal menus
    ensure_meal_menus(cursor, school_id, class_a_id, teacher_user_id, today, tomorrow, now)
    print("Added meal menus")

    conn.commit()
    conn.close()
    print("Seeding complete!")


if __name__ == "__main__":
    seed()
