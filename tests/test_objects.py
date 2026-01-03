"""Tests for the objects module."""

from semantics.modules import objects


def test_objects_execute():
    """Test that objects module executes without errors."""
    # This should not raise any exceptions
    objects.execute("test_video.mp4", "/output/folder")


def test_objects_execute_with_different_formats():
    """Test that objects module handles different file formats."""
    # This should not raise any exceptions
    objects.execute("test_image.jpg", "/results")
    objects.execute("test_video.mp4", "/results")
