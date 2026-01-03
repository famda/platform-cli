"""Tests for the CLI module."""

import pytest
from semantics.cli import create_parser


def test_parser_requires_input_and_output():
    """Test that parser requires both input and output arguments."""
    parser = create_parser()
    
    # Should fail without required arguments
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_with_input_and_output():
    """Test parser with required input and output arguments."""
    parser = create_parser()
    args = parser.parse_args(["-i", "video.mp4", "-o", "/output/folder"])
    assert args.input == "video.mp4"
    assert args.output == "/output/folder"


def test_parser_with_transcribe():
    """Test parser with transcribe flag."""
    parser = create_parser()
    args = parser.parse_args(["-i", "video.mp4", "-o", "/output", "--transcribe"])
    assert args.transcribe is True
    assert args.input == "video.mp4"
    assert args.output == "/output"


def test_parser_with_objects():
    """Test parser with objects flag."""
    parser = create_parser()
    args = parser.parse_args(["-i", "image.jpg", "-o", "/output", "--objects"])
    assert args.objects is True
    assert args.input == "image.jpg"
    assert args.output == "/output"


def test_parser_with_all_options():
    """Test parser with all options."""
    parser = create_parser()
    args = parser.parse_args(["-i", "video.mp4", "-o", "/output", "--transcribe", "--objects"])
    assert args.input == "video.mp4"
    assert args.output == "/output"
    assert args.transcribe is True
    assert args.objects is True


def test_parser_short_options():
    """Test parser with short option flags."""
    parser = create_parser()
    args = parser.parse_args(["-i", "audio.mp3", "-o", "/results", "--transcribe"])
    assert args.input == "audio.mp3"
    assert args.output == "/results"
