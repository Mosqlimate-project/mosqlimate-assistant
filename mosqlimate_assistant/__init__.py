from importlib import metadata as importlib_metadata
from typing import List

from . import (
    api_consumer,
    assistant,
    docs_consumer,
    main,
    muni_codes,
    prompts,
    schemas,
    settings,
    utils,
    vector_db,
)


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "1.5.0"  # changed by semantic-release


version: str = get_version()
__version__: str = version
__all__: List[str] = [
    "api_consumer",
    "assistant",
    "docs_consumer",
    "vector_db",
    "muni_codes",
    "schemas",
    "settings",
    "utils",
    "prompts",
    "main",
]  # noqa: WPS410 (the only __variable__ we use)
