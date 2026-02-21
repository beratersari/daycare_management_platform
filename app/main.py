from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connection import init_db
from app.routers import parents, teachers, classes, students


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    init_db()
    yield


app = FastAPI(
    title="Kinder Tracker API",
    description="Backend API for managing daycare/preschool students, parents, teachers, and classes.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers (all use /api/v1 prefix)
app.include_router(parents.router)
app.include_router(teachers.router)
app.include_router(classes.router)
app.include_router(students.router)


@app.get("/", tags=["Health"])
def root():
    """Root health check endpoint."""
    return {"message": "Kinder Tracker API is running", "version": "1.0.0"}


@app.get("/api/v1/health", tags=["Health"])
def health():
    """API v1 health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
