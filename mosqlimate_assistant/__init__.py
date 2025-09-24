from importlib import metadata as importlib_metadata
from typing import List

from . import (
    assistant,
    docs_consumer,
    func_tools,
    main,
    muni_codes,
    prompts,
    settings,
    utils,
    vector_db,
)


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "1.7.2"  # changed by semantic-release


version: str = get_version()
__version__: str = version
__all__: List[str] = [
    "assistant",
    "docs_consumer",
    "func_tools",
    "vector_db",
    "muni_codes",
    "settings",
    "utils",
    "prompts",
    "main",
]  # noqa: WPS410 (the only __variable__ we use)
