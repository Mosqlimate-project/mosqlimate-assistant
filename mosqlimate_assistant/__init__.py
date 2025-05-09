from importlib import metadata as importlib_metadata
from typing import List

from . import (
    api_consumer,
    assistant,
    assistant_ollama,
    docs_consumer,
    faiss_db,
    muni_codes,
    schemas,
    settings,
    utils,
)
from .prompts import eng, por


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "0.1.0"  # changed by semantic-release


version: str = get_version()
__version__: str = version
__all__: List[str] = [
    "api_consumer",
    "assistant_ollama",
    "assistant",
    "docs_consumer",
    "faiss_db",
    "muni_codes",
    "schemas",
    "settings",
    "utils",
    "eng",
    "por",
]  # noqa: WPS410 (the only __variable__ we use)
