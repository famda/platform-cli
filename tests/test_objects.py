"""Tests for the objects module."""

import pytest
from semantics.modules import objects


def test_objects_execute():
    """Test that objects module executes without errors."""
    # This should not raise any exceptions
    objects.execute("test_video.mp4")


def test_objects_execute_none_input():
    """Test that objects module handles None input."""
    # This should not raise any exceptions
    objects.execute(None)
