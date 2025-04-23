from importlib import metadata as importlib_metadata
from typing import List

from .assistant import *
from .configs import *
from .filters import *
from .input_validator import *
from .prompts import eng, por
from .utils import *


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "0.1.0"  # changed by semantic-release


version: str = get_version()
__version__: str = version
__all__: List[str] = []  # noqa: WPS410 (the only __variable__ we use)
