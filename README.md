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
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

## Mock Users (Development)

The following mock users are automatically created when the server starts for the first time:

| Email | Password | Role | Name |
|-------|----------|------|------|
| `admin@example.com` | `admin123` | ADMIN | System Administrator |
| `director@example.com` | `director123` | DIRECTOR | Sarah Johnson |
| `teacher@example.com` | `teacher123` | TEACHER | Emily Davis |
| `parent@example.com` | `parent123` | PARENT | Michael Brown |

Use these credentials to log in via the mobile app or API.

## Database

SQLite database is automatically initialized at `kinder_tracker.db` in the project root on first startup.

## Project Structure (N-Layered Architecture)

```
app/
├── main.py                  # FastAPI app entry point
├── database/
│   └── connection.py        # SQLite connection & schema init
├── schemas/                 # DTOs / Pydantic models
│   ├── auth.py              # User DTOs (registration/login)
│   ├── student.py           # Student, Allergy, HWInfo DTOs
│   └── class_dto.py         # Class DTOs
├── repositories/            # Data access layer
│   ├── base_repository.py   # Base repository with common operations
│   ├── user_repository.py
│   ├── student_repository.py
│   └── class_repository.py
├── services/                # Business logic layer
│   ├── auth_service.py
│   ├── student_service.py
│   └── class_service.py
└── routers/                 # API endpoints (presentation layer)
    ├── auth.py              # /api/v1/auth
    ├── parents.py           # /api/v1/parents (user-role listing)
    ├── teachers.py          # /api/v1/teachers (user-role listing)
    ├── classes.py           # /api/v1/classes
    └── students.py          # /api/v1/students
```

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create a new user account |
| POST | `/api/v1/auth/login` | Authenticate and receive tokens |
| POST | `/api/v1/auth/refresh` | Exchange refresh token for new pair |
| POST | `/api/v1/auth/logout` | Revoke all tokens (requires auth) |
| GET | `/api/v1/auth/me` | Get current user profile (requires auth) |

**Registration Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "PARENT",
  "school_id": null,
  "phone": "555-123-4567",
  "address": "123 Main St"
}
```

**Login Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Token Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root health check |
| GET | `/api/v1/health` | API v1 health check |

### Parents (`/api/v1/parents`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/parents/` | List all parents (role-based users) |
| GET | `/api/v1/parents/{id}` | Get a parent profile (user) |

### Teachers (`/api/v1/teachers`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/teachers/` | List all teachers (role-based users) |
| GET | `/api/v1/teachers/{id}` | Get a teacher profile (user) |
| GET | `/api/v1/teachers/{id}/classes` | View assigned classes |
| POST | `/api/v1/teachers/{id}/classes/{class_id}` | Assign a teacher to a class |
| DELETE | `/api/v1/teachers/{id}/classes/{class_id}` | Unassign a teacher from a class |

### Classes (`/api/v1/classes`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/classes/` | Create a class |
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
  "class_ids": [1, 2],
  "student_photo": "https://...",
  "date_of_birth": "2021-03-15",
  "created_date": "2025-01-15T10:30:00",
  "parents": [10, 11],
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

### User DTO (Teacher/Parent)
```json
{
  "user_id": 10,
  "first_name": "Alice",
  "last_name": "Smith",
  "email": "alice@example.com",
  "phone": "555-0001",
  "address": "123 Main St",
  "role": "PARENT",
  "school_id": 1,
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
  "teachers": [ /* UserResponse objects */ ]
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
- Parent user IDs
- Student photos