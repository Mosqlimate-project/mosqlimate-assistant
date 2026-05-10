"""Environment-driven runtime settings for the package.

This module centralizes cache and persistence paths used during document
ingestion and vector-store storage. Values have safe defaults and can be
overridden through environment variables when needed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _get_path_setting(var_name: str, default: Path) -> Path:
    """Return a path from the environment or fall back to ``default``."""
    raw_value = os.getenv(var_name)
    return Path(raw_value).expanduser() if raw_value else default


def _default_cache_dir() -> Path:
    """Return a cache directory near the script that invokes the assistant."""
    main_module = sys.modules.get("__main__")
    main_file = getattr(main_module, "__file__", None)
    if main_file:
        return Path(main_file).resolve().parent / ".mosqlimate-assistant"
    return Path.cwd() / ".mosqlimate-assistant"


DEFAULT_CACHE_DIR = _default_cache_dir()


PACKAGE_CACHE_DIR: Path = _get_path_setting(
    "MOSQLIMATE_ASSISTANT_CACHE_DIR",
    DEFAULT_CACHE_DIR,
)
VECTORSTORE_CACHE_DIR: Path = _get_path_setting(
    "MOSQLIMATE_ASSISTANT_VECTORSTORE_DIR",
    PACKAGE_CACHE_DIR / "vectorstores",
)
HTTP_CACHE_ENABLED: bool = (
    os.getenv("HTTP_CACHE_ENABLED", "true").lower() == "true"
)
HTTP_CACHE_DIR: str = str(
    _get_path_setting("HTTP_CACHE_DIR", PACKAGE_CACHE_DIR / "http")
)
HTTP_CACHE_TTL_SECONDS: int = int(
    os.getenv("HTTP_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60))
)
