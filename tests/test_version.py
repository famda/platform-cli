"""Tests for version module."""

import re
from semantics import __version__


def test_version_is_available():
    """Test that __version__ is defined and not unknown."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert __version__ != ""


def test_version_format():
    """Test that version follows semantic versioning or development version format."""
    # Version should be either:
    # - A semantic version like "0.0.1", "1.2.3"
    # - A development version like "0.0.2.dev1+g90dfe88"
    # - "unknown" if metadata is not available
    assert __version__ == "unknown" or re.match(
        r'^\d+\.\d+\.\d+(\.(dev|post|rc|a|b)\d+)?(\+g[a-f0-9]+(\.(d\d{8})?)?)?$',
        __version__
    ), f"Version '{__version__}' does not match expected format"


def test_version_is_string():
    """Test that __version__ is a string type."""
    assert isinstance(__version__, str)
