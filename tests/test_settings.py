import importlib
import sys
import types
from pathlib import Path

import mosqlimate_assistant.settings as settings


def test_settings_types():
    assert isinstance(settings.HTTP_CACHE_ENABLED, bool)
    assert isinstance(settings.HTTP_CACHE_DIR, str)
    assert isinstance(settings.HTTP_CACHE_TTL_SECONDS, int)
    assert isinstance(settings.PACKAGE_CACHE_DIR, Path)
    assert isinstance(settings.VECTORSTORE_CACHE_DIR, Path)


def test_default_cache_dir_uses_invoking_script_directory(
    monkeypatch,
    tmp_path: Path,
):
    main_module = types.SimpleNamespace(__file__=str(tmp_path / "app.py"))
    monkeypatch.setitem(sys.modules, "__main__", main_module)

    assert settings._default_cache_dir() == (
        tmp_path / ".mosqlimate-assistant"
    )


def test_default_cache_dir_falls_back_to_cwd(
    monkeypatch,
    tmp_path: Path,
):
    main_module = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "__main__", main_module)
    monkeypatch.chdir(tmp_path)

    assert settings._default_cache_dir() == (
        tmp_path / ".mosqlimate-assistant"
    )


def test_env_override_still_wins_for_package_cache_dir(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setenv(
        "MOSQLIMATE_ASSISTANT_CACHE_DIR",
        str(tmp_path / "custom-cache"),
    )

    reloaded = importlib.reload(settings)
    try:
        assert reloaded.PACKAGE_CACHE_DIR == tmp_path / "custom-cache"
    finally:
        importlib.reload(reloaded)
