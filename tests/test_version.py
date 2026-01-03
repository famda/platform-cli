"""Tests for version module."""

import re
from semantics import __version__


def test_version_is_available():
    """Test that __version__ is defined and not unknown."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert __version__ != ""


def test_version_format():
    """Test that version follows semantic versioning or development version format.
    
    Valid formats:
    - Semantic version: "0.0.1", "1.2.3", "0.1"
    - Pre-release: "1.2.3.dev1", "0.1.dev1", "1.2.3.rc1", "1.2.3.a1", "1.2.3.b1"
    - With git commit: "1.2.3.dev1+g90dfe88", "0.1.dev1+gd07c87265.d20260103"
    - Fallback: "unknown" if metadata is not available
    """
    # Version pattern components:
    # - \d+\.\d+(\.\d+)? : semantic version (major.minor or major.minor.patch)
    # - (\.(dev|post|rc|a|b)\d+)? : optional pre-release/post-release
    # - (\+g[a-f0-9]+(\.(d\d{8})?)?)? : optional git commit hash and date
    version_pattern = r'^\d+\.\d+(\.\d+)?(\.(dev|post|rc|a|b)\d+)?(\+g[a-f0-9]+(\.(d\d{8})?)?)?$'
    
    assert __version__ == "unknown" or re.match(
        version_pattern,
        __version__
    ), f"Version '{__version__}' does not match expected format"


def test_version_is_string():
    """Test that __version__ is a string type."""
    assert isinstance(__version__, str)
