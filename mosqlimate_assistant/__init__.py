from importlib import metadata as importlib_metadata
from typing import List

from . import (api_consumer, assistant, faiss_db, muni_codes, schemas,
               settings, utils)
from .prompts import eng, por


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "0.1.0"  # changed by semantic-release


version: str = get_version()
__version__: str = version
__all__: List[str] = [
    "assistant",
    "settings",
    "schemas",
    "faiss_db",
    "utils",
    "api_consumer",
    "muni_codes",
    "eng",
    "por",
]  # noqa: WPS410 (the only __variable__ we use)
