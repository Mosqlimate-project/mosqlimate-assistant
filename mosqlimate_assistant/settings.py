import os

HTTP_CACHE_ENABLED: bool = (
    os.getenv("HTTP_CACHE_ENABLED", "true").lower() == "true"
)
HTTP_CACHE_DIR: str = os.getenv("HTTP_CACHE_DIR", ".http_cache")
HTTP_CACHE_TTL_SECONDS: int = int(
    os.getenv("HTTP_CACHE_TTL_SECONDS", str(7 * 24 * 60 * 60))
)
