import sqlite3
import os
import bcrypt
from datetime import datetime, timedelta

# DB path
DB_PATH = os.path.join(os.getcwd(), "kinder_tracker.db")

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
    cursor.execute("SELECT school_id FROM schools LIMIT 1")
    school_row = cursor.fetchone()
    if not school_row:
        print("No school found, creating one...")
        cursor.execute("""
            INSERT INTO schools (school_name, address, phone, email, director_name, license_number, capacity, created_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, ("Sunshine Daycare Center", "123 Learning Lane, Education City", "555-123-4567",
              "director@sunshine.edu", "Jane Smith", "DC-2024-001", 50, now))
        school_id = cursor.lastrowid
    else:
        school_id = school_row["school_id"]

    # 2. Add classes
    cursor.execute("INSERT INTO classes (class_name, school_id, capacity, created_date, is_deleted) VALUES (?, ?, ?, ?, 0)",
                   ("Preschool A", school_id, 20, now))
    class_a_id = cursor.lastrowid
    cursor.execute("INSERT INTO classes (class_name, school_id, capacity, created_date, is_deleted) VALUES (?, ?, ?, ?, 0)",
                   ("Toddler B", school_id, 15, now))
    class_b_id = cursor.lastrowid
    print(f"Created classes: A({class_a_id}), B({class_b_id})")

    # 3. Add student user
    student_pass = hash_password("student123")
    cursor.execute("""
        INSERT OR IGNORE INTO users (email, password_hash, first_name, last_name, role, school_id, phone, address, created_date, is_deleted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, ("student@example.com", student_pass, "Billy", "Kid", "STUDENT", school_id, "555-000-0005", "123 Kid St", now))
    student_user_id = cursor.lastrowid
    print(f"Created student user: student@example.com (ID: {student_user_id})")

    # 4. Get other users
    cursor.execute("SELECT user_id FROM users WHERE email = 'teacher@example.com'")
    teacher_user_id = cursor.fetchone()["user_id"]
    cursor.execute("SELECT user_id FROM users WHERE email = 'parent@example.com'")
    parent_user_id = cursor.fetchone()["user_id"]

    # 5. Link teacher to class
    cursor.execute("INSERT OR IGNORE INTO teacher_classes (user_id, class_id) VALUES (?, ?)", (teacher_user_id, class_a_id))
    print(f"Linked teacher to class {class_a_id}")

    # 6. Add students (in students table)
    cursor.execute("""
        INSERT INTO students (first_name, last_name, school_id, date_of_birth, created_date, is_deleted)
        VALUES (?, ?, ?, ?, ?, 0)
    """, ("Billy", "Kid", school_id, "2020-05-15", now))
    student_billy_id = cursor.lastrowid
    
    cursor.execute("""
        INSERT INTO students (first_name, last_name, school_id, date_of_birth, created_date, is_deleted)
        VALUES (?, ?, ?, ?, ?, 0)
    """, ("Sally", "Student", school_id, "2021-02-10", now))
    student_sally_id = cursor.lastrowid
    print(f"Created students: {student_billy_id}, {student_sally_id}")

    # 7. Link students to parent and classes
    cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)", (student_billy_id, class_a_id))
    cursor.execute("INSERT INTO student_classes (student_id, class_id) VALUES (?, ?)", (student_sally_id, class_b_id))
    
    cursor.execute("INSERT INTO student_parents (student_id, user_id) VALUES (?, ?)", (student_billy_id, parent_user_id))
    cursor.execute("INSERT INTO student_parents (student_id, user_id) VALUES (?, ?)", (student_sally_id, parent_user_id))
    print("Linked students to classes and parent")

    # 8. Add meal menus
    meals = [
        (school_id, None, today, "Oatmeal with berries", "Turkey and cheese sandwich", "Pasta with tomato sauce", teacher_user_id, now),
        (school_id, class_a_id, today, "Yogurt and granola", "Chicken salad", "Grilled cheese", teacher_user_id, now),
        (school_id, None, tomorrow, "Pancakes", "Beef stew", "Chicken nuggets", teacher_user_id, now),
    ]
    for meal in meals:
        cursor.execute("""
            INSERT OR IGNORE INTO meal_menus (school_id, class_id, menu_date, breakfast, lunch, dinner, created_by, created_date, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, meal)
    print("Added meal menus")

    conn.commit()
    conn.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed()
