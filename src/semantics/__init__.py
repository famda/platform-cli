"""Semantics - Process different file types with specialized AI handlers."""

# Version injected by hatch-vcs
try:
    from semantics._version import __version__
except ImportError:
    try:
        from importlib.metadata import version, PackageNotFoundError

        try:
            __version__ = version("semantics")
        except PackageNotFoundError:
            __version__ = "unknown"
    except ImportError:
        __version__ = "unknown"

from semantics.cli import main

__all__ = ["main", "__version__"]
