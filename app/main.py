from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.logger import get_logger, setup_logging
from app.database.connection import init_db
from app.routers import parents, teachers, classes, students, schools

# Initialise logging as the very first step
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    logger.info("Kinder Tracker API starting up …")
    init_db()
    logger.info("Startup complete — ready to serve requests")
    yield
    logger.info("Kinder Tracker API shutting down …")


app = FastAPI(
    title="Kinder Tracker API",
    description="Backend API for managing daycare/preschool students, parents, teachers, and classes.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers (all use /api/v1 prefix)
app.include_router(schools.router)
app.include_router(parents.router)
app.include_router(teachers.router)
app.include_router(classes.router)
app.include_router(students.router)

logger.debug("All routers registered")


@app.get("/", tags=["Health"])
def root():
    """Root health check endpoint."""
    logger.trace("Health check: /")
    return {"message": "Kinder Tracker API is running", "version": "1.0.0"}


@app.get("/api/v1/health", tags=["Health"])
def health():
    """API v1 health check endpoint."""
    logger.trace("Health check: /api/v1/health")
    return {"status": "healthy", "version": "1.0.0"}
