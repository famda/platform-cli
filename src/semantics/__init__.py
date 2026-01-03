"""Semantics - A semantic analysis CLI tool."""

from semantics.cli import main

# Version injected by hatch-vcs
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version("semantics")
    except PackageNotFoundError:
        __version__ = "unknown"
except ImportError:
    __version__ = "unknown"

__all__ = ["main", "__version__"]
