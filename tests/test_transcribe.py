"""Tests for the transcribe module."""

from semantics.modules import transcribe


def test_transcribe_execute():
    """Test that transcribe module executes without errors."""
    # This should not raise any exceptions
    transcribe.execute("test_video.mp4", "/output/folder")


def test_transcribe_execute_with_different_formats():
    """Test that transcribe module handles different file formats."""
    # This should not raise any exceptions
    transcribe.execute("test_audio.mp3", "/results")
    transcribe.execute("test_video.avi", "/results")
