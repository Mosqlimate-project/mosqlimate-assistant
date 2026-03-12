from mosqlimate_assistant.settings import (
    HTTP_CACHE_DIR,
    HTTP_CACHE_ENABLED,
    HTTP_CACHE_TTL_SECONDS,
)


def test_settings_types():
    assert isinstance(HTTP_CACHE_ENABLED, bool)
    assert isinstance(HTTP_CACHE_DIR, str)
    assert isinstance(HTTP_CACHE_TTL_SECONDS, int)
