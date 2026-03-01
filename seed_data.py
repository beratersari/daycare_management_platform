import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add current directory to python path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import get_connection, init_db, create_mock_data
from app.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("seed_data")

def seed_database():
    # Ensure DB is initialized
    init_db()
    create_mock_data()

    conn = get_connection()
    cursor = conn.cursor()
    
    logger.info("Starting database seeding...")
    
    # 1. Get existing IDs (School, Users)
    cursor.execute("SELECT school_id FROM schools WHERE is_deleted = 0")
    school_rows = [row["school_id"] for row in cursor.fetchall()]
    if not school_rows:
        logger.error("No school found.")
        return

    # Get user IDs by role
    users = {}
    for role in ["ADMIN", "DIRECTOR", "TEACHER", "PARENT"]:
        cursor.execute("SELECT user_id, first_name, last_name FROM users WHERE role = ?", (role,))
        users[role] = [dict(r) for r in cursor.fetchall()]
        
    if not users["TEACHER"] or not users["PARENT"]:
        logger.error("Missing teachers or parents.")
        return

    teacher_id = users["TEACHER"][0]["user_id"]
    parent_id = users["PARENT"][0]["user_id"]
    
    now = datetime.now().isoformat()
    
    # 2. Create Classes for each school
    base_classes = [
        {"name": "Sunshine Toddlers", "capacity": 15},
        {"name": "Rainbow Preschool", "capacity": 20},
        {"name": "Starlight Pre-K", "capacity": 18},
    ]

    class_ids_by_school: dict[int, list[int]] = {}
    for school_id in school_rows:
        class_ids_by_school[school_id] = []
        for cls in base_classes:
            cursor.execute(
                "SELECT class_id FROM classes WHERE class_name = ? AND school_id = ?",
                (cls["name"], school_id),
            )
            row = cursor.fetchone()
            if row:
                class_ids_by_school[school_id].append(row["class_id"])
                logger.info(f"Class '{cls['name']}' already exists for school {school_id}.")
            else:
                cursor.execute(
                    """
                    INSERT INTO classes (class_name, school_id, capacity, created_date, is_deleted)
                    VALUES (?, ?, ?, ?, 0)
                    """,
                    (cls["name"], school_id, cls["capacity"], now),
                )
                class_ids_by_school[school_id].append(cursor.lastrowid)
                logger.info(f"Created class: {cls['name']} for school {school_id}")

    # 3. Assign Teacher to Classes
    for school_id, class_ids in class_ids_by_school.items():
        for cid in class_ids:
            cursor.execute("INSERT OR IGNORE INTO teacher_classes (user_id, class_id) VALUES (?, ?)", (teacher_id, cid))
            logger.info(f"Assigned teacher {teacher_id} to class {cid}")

    # 4. Create Students
    students_data = [
        {"first": "Alice", "last": "Brown", "dob": "2020-05-15", "photo": None},
        {"first": "Bob", "last": "Brown", "dob": "2022-08-20", "photo": None},
        {"first": "Charlie", "last": "Davis", "dob": "2021-03-10", "photo": None},
        {"first": "Diana", "last": "Prince", "dob": "2019-11-25", "photo": None},
        {"first": "Ethan", "last": "Hunt", "dob": "2020-01-12", "photo": None},
    ]
    
    # Get more parents if available
    cursor.execute("SELECT user_id FROM users WHERE role = 'PARENT'")
    parent_ids = [r["user_id"] for r in cursor.fetchall()]

    for school_id in school_rows:
        class_ids = class_ids_by_school.get(school_id, [])
        for i, s in enumerate(students_data):
            cursor.execute(
                "SELECT student_id FROM students WHERE first_name = ? AND last_name = ? AND school_id = ?",
                (s["first"], s["last"], school_id),
            )
            row = cursor.fetchone()

            if row:
                student_id = row["student_id"]
                logger.info(f"Student {s['first']} already exists for school {school_id}.")
            else:
                cursor.execute(
                    """
                    INSERT INTO students (first_name, last_name, school_id, student_photo, date_of_birth, created_date, is_deleted)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                    """,
                    (s["first"], s["last"], school_id, s["photo"], s["dob"], now),
                )
                student_id = cursor.lastrowid
                logger.info(f"Created student: {s['first']} {s['last']} for school {school_id}")

                # Add Allergies
                if i == 0:
                    cursor.execute(
                        """
                        INSERT INTO student_allergies (student_id, allergy_name, severity, notes, created_date, is_deleted)
                        VALUES (?, ?, ?, ?, ?, 0)
                        """,
                        (student_id, "Peanuts", "High", "Carry EpiPen", now),
                    )

                # Add HW Info
                cursor.execute(
                    """
                    INSERT INTO student_hw_info (student_id, height, weight, measurement_date, created_date, is_deleted)
                    VALUES (?, ?, ?, ?, ?, 0)
                    """,
                    (student_id, 100.0 + i * 5, 15.0 + i * 2, now.split("T")[0], now),
                )

            # Link to Parent
            # Alice and Bob to parent 0, Charlie to parent 1 (if exists), etc.
            p_idx = i // 2 if i // 2 < len(parent_ids) else 0
            pid = parent_ids[p_idx]
            cursor.execute(
                "INSERT OR IGNORE INTO student_parents (student_id, user_id) VALUES (?, ?)",
                (student_id, pid),
            )
            logger.info(f"Linked student {student_id} to parent {pid}")

            # Enroll in Class
            if class_ids:
                class_idx = i % len(class_ids)
                cid = class_ids[class_idx]
                cursor.execute(
                    "INSERT OR IGNORE INTO student_classes (student_id, class_id) VALUES (?, ?)",
                    (student_id, cid),
                )
                logger.info(f"Enrolled student {student_id} in class {cid}")

    # 5. Create Meal Menus
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    for school_id in school_rows:
        class_ids = class_ids_by_school.get(school_id, [])
        menu_class_id = class_ids[0] if class_ids else None
        meals = [
            (school_id, None, today, "Oatmeal with berries", "Turkey and cheese sandwich", "Pasta with tomato sauce", teacher_id, now),
            (school_id, menu_class_id, today, "Yogurt and granola", "Chicken salad", "Grilled cheese", teacher_id, now),
            (school_id, None, tomorrow, "Pancakes", "Beef stew", "Chicken nuggets", teacher_id, now),
        ]
        for meal in meals:
            cursor.execute(
                """
                INSERT OR IGNORE INTO meal_menus (school_id, class_id, menu_date, breakfast, lunch, dinner, created_by, created_date, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """,
                meal,
            )
    logger.info("Added meal menus.")

    conn.commit()
    conn.close()
    logger.info("Database seeding completed.")

if __name__ == "__main__":
    seed_database()
