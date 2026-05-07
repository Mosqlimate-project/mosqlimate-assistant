"""Environment-driven runtime settings for the package.

This module currently centralizes HTTP-cache configuration used during
document ingestion. Values are intentionally simple, have safe defaults,
and can be overridden through environment variables when needed.
"""

import os

HTTP_CACHE_ENABLED: bool = (
    os.getenv("HTTP_CACHE_ENABLED", "true").lower() == "true"
)
HTTP_CACHE_DIR: str = os.getenv("HTTP_CACHE_DIR", ".http_cache")
HTTP_CACHE_TTL_SECONDS: int = int(
    os.getenv("HTTP_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60))
)
