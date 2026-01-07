"""Shared test fixtures for all tests."""

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()
