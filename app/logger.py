"""
Centralized logging module for Kinder Tracker.

Provides a configurable logging system with five severity levels:
  TRACE (5), DEBUG (10), INFO (20), WARNING (30), ERROR (40).

Configuration is loaded from ``logging_config.yaml`` at the project root.
Each level can be individually enabled or disabled via the config file,
and output can be directed to both console and rotating log files.

Usage::

    from app.logger import get_logger

    logger = get_logger(__name__)
    logger.trace("Very detailed diagnostic info")
    logger.debug("Debugging information")
    logger.info("General information")
    logger.warning("Something unexpected")
    logger.error("A serious problem")
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Custom TRACE level (lower than DEBUG)
# ---------------------------------------------------------------------------
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


# ---------------------------------------------------------------------------
# Level-aware filter
# ---------------------------------------------------------------------------
class LevelToggleFilter(logging.Filter):
    """Suppress log records whose level has been disabled in the config."""

    def __init__(self, disabled_levels: set[int]):
        super().__init__()
        self.disabled_levels = disabled_levels

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno not in self.disabled_levels


# ---------------------------------------------------------------------------
# Extended Logger with .trace() convenience method
# ---------------------------------------------------------------------------
class KinderLogger(logging.Logger):
    """Custom Logger subclass that adds a ``trace`` method."""

    def trace(self, msg: str, *args, **kwargs):
        """Log a message with TRACE level."""
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, msg, args, **kwargs)


# Register our custom logger class so every ``getLogger`` call returns it.
logging.setLoggerClass(KinderLogger)

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------
_CONFIG_FILE = "logging_config.yaml"
_LOGGER_ROOT_NAME = "kinder_tracker"
_initialised = False


def _find_config_path() -> Optional[str]:
    """Search for the config file starting from the project root."""
    # Check common locations
    candidates = [
        os.path.join(os.getcwd(), _CONFIG_FILE),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), _CONFIG_FILE),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _load_config() -> dict:
    """Load and return the YAML configuration, or sensible defaults."""
    config_path = _find_config_path()
    if config_path and os.path.isfile(config_path):
        with open(config_path, "r") as fh:
            return yaml.safe_load(fh) or {}
    # Fallback defaults when no config file is found
    return {
        "log_levels": {
            "trace": True,
            "debug": True,
            "info": True,
            "warning": True,
            "error": True,
        },
        "log_format": "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "console": {"enabled": True, "level": "TRACE"},
        "file": {"enabled": False},
    }


def _level_name_to_int(name: str) -> int:
    """Convert a level name string to its integer value."""
    name = name.upper()
    if name == "TRACE":
        return TRACE_LEVEL
    return getattr(logging, name, logging.DEBUG)


def _build_disabled_levels(config: dict) -> set[int]:
    """Return the set of numeric levels that are disabled in the config."""
    level_map = {
        "trace": TRACE_LEVEL,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }
    disabled: set[int] = set()
    levels_cfg = config.get("log_levels", {})
    for name, numeric in level_map.items():
        if not levels_cfg.get(name, True):
            disabled.add(numeric)
    return disabled


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
def setup_logging() -> None:
    """
    Read ``logging_config.yaml`` and configure the root *kinder_tracker*
    logger accordingly.  Safe to call multiple times (idempotent).
    """
    global _initialised
    if _initialised:
        return

    config = _load_config()

    # Determine disabled levels and build filter
    disabled = _build_disabled_levels(config)
    toggle_filter = LevelToggleFilter(disabled)

    # Formatting
    fmt = config.get(
        "log_format",
        "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d - %(message)s",
    )
    datefmt = config.get("date_format", "%Y-%m-%d %H:%M:%S")
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    # Root application logger
    root_logger = logging.getLogger(_LOGGER_ROOT_NAME)
    root_logger.setLevel(TRACE_LEVEL)  # allow everything; filters decide
    root_logger.addFilter(toggle_filter)

    # --- Console handler ---
    console_cfg = config.get("console", {})
    if console_cfg.get("enabled", True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(_level_name_to_int(console_cfg.get("level", "TRACE")))
        console_handler.setFormatter(formatter)
        console_handler.addFilter(toggle_filter)
        root_logger.addHandler(console_handler)

    # --- File handler (rotating) ---
    file_cfg = config.get("file", {})
    if file_cfg.get("enabled", False):
        log_path = file_cfg.get("path", "logs/kinder_tracker.log")
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=file_cfg.get("max_bytes", 5_242_880),
            backupCount=file_cfg.get("backup_count", 3),
            encoding="utf-8",
        )
        file_handler.setLevel(_level_name_to_int(file_cfg.get("level", "TRACE")))
        file_handler.setFormatter(formatter)
        file_handler.addFilter(toggle_filter)
        root_logger.addHandler(file_handler)

    # --- Per-module overrides ---
    module_overrides = config.get("module_overrides", {})
    if module_overrides:
        for module_name, level_str in module_overrides.items():
            mod_logger = logging.getLogger(module_name)
            mod_logger.setLevel(_level_name_to_int(level_str))

    _initialised = True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_logger(name: str) -> KinderLogger:
    """
    Return a :class:`KinderLogger` scoped under the *kinder_tracker* namespace.

    Args:
        name: Typically ``__name__`` of the calling module.  The function
              automatically maps ``app.services.school_service`` →
              ``kinder_tracker.services.school_service`` so that the
              hierarchy stays consistent.

    Returns:
        A configured :class:`KinderLogger` instance.
    """
    # Ensure the logging subsystem has been initialised
    setup_logging()

    # Map 'app.xxx' to 'kinder_tracker.xxx' for cleaner log output
    if name.startswith("app."):
        name = _LOGGER_ROOT_NAME + name[3:]
    elif not name.startswith(_LOGGER_ROOT_NAME):
        name = f"{_LOGGER_ROOT_NAME}.{name}"

    return logging.getLogger(name)  # type: ignore[return-value]
