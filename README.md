# Kinder Tracker – Daycare Management Platform

A FastAPI backend for managing daycare centers and preschools. Track students, parents, teachers, classes, allergies, and height/weight measurements.

## Features

- **N-Layered Architecture**: Routers → Services → Repositories
- **Soft Delete**: All entities use `is_deleted` flag (no hard deletes)
- **Validation**: Email and phone regex validation
- **Audit Fields**: `created_date` on all entities
- **API Versioning**: All endpoints under `/api/v1`

## Quick Start

```bash
pip install fastapi uvicorn pydantic
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

## Database

SQLite database is automatically initialized at `/testbed/db/kinder_tracker.db` on first startup.

## Project Structure (N-Layered Architecture)

```
app/
├── main.py                  # FastAPI app entry point
├── database/
│   └── connection.py        # SQLite connection & schema init
├── schemas/                 # DTOs / Pydantic models
│   ├── parent.py            # Parent DTOs (with email/phone validation)
│   ├── teacher.py           # Teacher DTOs (with email/phone validation)
│   ├── student.py           # Student, Allergy, HWInfo DTOs
│   └── class_dto.py         # Class DTOs
├── repositories/            # Data access layer
│   ├── base_repository.py   # Base repository with common operations
│   ├── parent_repository.py
│   ├── teacher_repository.py
│   ├── student_repository.py
│   └── class_repository.py
├── services/                # Business logic layer
│   ├── parent_service.py
│   ├── teacher_service.py
│   ├── student_service.py
│   └── class_service.py
└── routers/                 # API endpoints (presentation layer)
    ├── parents.py           # /api/v1/parents
    ├── teachers.py          # /api/v1/teachers
    ├── classes.py           # /api/v1/classes
    └── students.py          # /api/v1/students
```

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/api/v1/health` | API v1 health check |

### Parents (`/api/v1/parents`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/parents/` | Create a parent |
| GET | `/api/v1/parents/` | List all parents |
| GET | `/api/v1/parents/{id}` | Get parent with linked student IDs |
| PUT | `/api/v1/parents/{id}` | Update a parent |
| DELETE | `/api/v1/parents/{id}` | Soft delete a parent |

### Teachers (`/api/v1/teachers`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/teachers/` | Create a teacher |
| GET | `/api/v1/teachers/` | List all teachers |
| GET | `/api/v1/teachers/{id}` | Get a teacher |
| PUT | `/api/v1/teachers/{id}` | Update a teacher |
| DELETE | `/api/v1/teachers/{id}` | Soft delete a teacher |
| GET | `/api/v1/teachers/{id}/classes` | **View all classes with full student info** |

### Classes (`/api/v1/classes`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/classes/` | Create a class (with teacher IDs) |
| GET | `/api/v1/classes/` | List all classes (with students & teachers) |
| GET | `/api/v1/classes/{id}` | Get class with all students & teachers |
| PUT | `/api/v1/classes/{id}` | Update a class |
| DELETE | `/api/v1/classes/{id}` | Soft delete a class |

### Students (`/api/v1/students`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/students/` | Create student (with parents, allergies, HW info) |
| GET | `/api/v1/students/` | List all students |
| GET | `/api/v1/students/{id}` | Get student with all details |
| PUT | `/api/v1/students/{id}` | Update student |
| DELETE | `/api/v1/students/{id}` | Soft delete student |
| POST | `/api/v1/students/{id}/allergies` | Add an allergy |
| DELETE | `/api/v1/students/{id}/allergies/{aid}` | Soft delete an allergy |
| POST | `/api/v1/students/{id}/hw-info` | Add height/weight measurement |
| DELETE | `/api/v1/students/{id}/hw-info/{hid}` | Soft delete a measurement |

## Data Models

### Student DTO
```json
{
  "student_id": 1,
  "first_name": "Charlie",
  "last_name": "Smith",
  "class_id": 1,
  "student_photo": "https://...",
  "date_of_birth": "2021-03-15",
  "created_date": "2025-01-15T10:30:00",
  "parents": [1, 2],
  "student_allergies": [
    {
      "allergy_id": 1,
      "student_id": 1,
      "allergy_name": "Peanuts",
      "severity": "High",
      "notes": "Carries EpiPen",
      "created_date": "2025-01-15T10:30:00"
    }
  ],
  "student_hw_info": [
    {
      "hw_id": 1,
      "student_id": 1,
      "height": 95.5,
      "weight": 14.2,
      "measurement_date": "2025-01-15",
      "created_date": "2025-01-15T10:30:00"
    }
  ]
}
```

### Parent DTO
```json
{
  "parent_id": 1,
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice@example.com",
  "phone": "555-0001",
  "address": "123 Main St",
  "created_date": "2025-01-15T10:30:00"
}
```

### Teacher DTO
```json
{
  "teacher_id": 1,
  "first_name": "Ms.",
  "last_name": "Johnson",
  "email": "johnson@school.com",
  "phone": "555-1234",
  "address": "456 School Ave",
  "created_date": "2025-01-15T10:30:00"
}
```

### Class DTO
```json
{
  "class_id": 1,
  "class_name": "Sunflower Room",
  "capacity": 20,
  "created_date": "2025-01-15T10:30:00",
  "students": [ /* full StudentResponse objects */ ],
  "teachers": [ /* TeacherResponse objects */ ]
}
```

## Validation

### Email
Must match pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

### Phone
Must match pattern: `^\+?[0-9\s\-\(\)]{7,20}$`

## Soft Delete

All DELETE operations perform soft deletes by setting `is_deleted = 1`. Soft-deleted records are excluded from all GET queries.

## Teacher → Class View

`GET /api/v1/teachers/{id}/classes` returns all classes assigned to the teacher, with **complete student information** including:
- Allergies (name, severity, notes)
- Height/weight history with measurement dates
- Parent IDs
- Student photos