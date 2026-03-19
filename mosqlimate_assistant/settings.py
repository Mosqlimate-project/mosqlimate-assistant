"""Application settings loaded from environment variables.

Controls HTTP caching behavior for document fetching. All values have
sensible defaults and can be overridden via environment variables:

- ``HTTP_CACHE_ENABLED``  — enable/disable request caching (default: ``true``).
- ``HTTP_CACHE_DIR``      — directory for the SQLite cache (default: ``.http_cache``).
- ``HTTP_CACHE_TTL_SECONDS`` — cache time-to-live in seconds (default: 7 days).
"""

import os

HTTP_CACHE_ENABLED: bool = (
    os.getenv("HTTP_CACHE_ENABLED", "true").lower() == "true"
)
HTTP_CACHE_DIR: str = os.getenv("HTTP_CACHE_DIR", ".http_cache")
HTTP_CACHE_TTL_SECONDS: int = int(
    os.getenv("HTTP_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60))
)
