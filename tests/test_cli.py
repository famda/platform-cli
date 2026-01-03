"""Tests for the CLI module."""

from semantics.cli import create_parser


def test_create_parser():
    """Test that parser is created with expected arguments."""
    parser = create_parser()
    
    # Parse with no arguments
    args = parser.parse_args([])
    assert args.input is None
    assert args.transcribe is False
    assert args.objects is False


def test_parser_with_input():
    """Test parser with input file."""
    parser = create_parser()
    args = parser.parse_args(["-i", "video.mp4"])
    assert args.input == "video.mp4"


def test_parser_with_transcribe():
    """Test parser with transcribe flag."""
    parser = create_parser()
    args = parser.parse_args(["--transcribe"])
    assert args.transcribe is True


def test_parser_with_objects():
    """Test parser with objects flag."""
    parser = create_parser()
    args = parser.parse_args(["--objects"])
    assert args.objects is True


def test_parser_with_all_options():
    """Test parser with all options."""
    parser = create_parser()
    args = parser.parse_args(["-i", "video.mp4", "--transcribe", "--objects"])
    assert args.input == "video.mp4"
    assert args.transcribe is True
    assert args.objects is True
