from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.logger import get_logger, setup_logging
from app.database.connection import init_db, create_mock_data
from app.routers import auth, parents, teachers, classes, students, schools, terms, meal_menus

# Initialise logging as the very first step
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    logger.info("Kinder Tracker API starting up …")
    init_db()
    create_mock_data()  # Create mock users for development
    logger.info("Startup complete — ready to serve requests")
    yield
    logger.info("Kinder Tracker API shutting down …")


app = FastAPI(
    title="Kinder Tracker API",
    description="Backend API for managing daycare/preschool students, parents, teachers, and classes.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# Allow all common development origins:
# - localhost ports for web dev servers (Expo, CRA, Vite, etc.)
# - 127.0.0.1 variants (some tools use this instead of localhost)
# - Any local IP (192.168.x.x, 10.x.x.x) for physical device testing
# - file:// protocol (for some mobile webview scenarios)
# - null origin (some mobile apps send this)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Localhost variants
        "http://localhost:8000",
        "http://localhost:8081",   # Expo web dev server (default)
        "http://localhost:19000",  # Expo dev tools
        "http://localhost:19006",  # Expo web (legacy)
        "http://localhost:3000",   # React/Vite default
        "http://localhost:5173",   # Vite default
        # 127.0.0.1 variants
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:19000",
        "http://127.0.0.1:19006",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Capacitor/Cordova app origins
        "capacitor://localhost",
        "ionic://localhost",
        "http://localhost",
        "https://localhost",
        # File protocol (some mobile scenarios)
        "file://",
        "null",  # Some WebView contexts send this
    ],
    allow_origin_regex=r"https?://(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3})(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],  # Allow all headers for maximum compatibility
    expose_headers=["*"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Include routers (all use /api/v1 prefix)
app.include_router(auth.router)
app.include_router(schools.router)
app.include_router(parents.router)
app.include_router(teachers.router)
app.include_router(classes.router)
app.include_router(students.router)
app.include_router(terms.router)
app.include_router(meal_menus.router)

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
