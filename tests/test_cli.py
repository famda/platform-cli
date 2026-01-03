"""Tests for the CLI module."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from semantics.cli import create_parser, main


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


# Integration tests for main() function

def test_main_with_transcribe_module():
    """Test that main() calls transcribe module when --transcribe flag is set."""
    test_args = ["-i", "test.mp4", "-o", "/output", "--transcribe"]
    
    with patch('sys.argv', ['semantics'] + test_args):
        with patch('semantics.modules.transcribe.execute') as mock_transcribe:
            result = main()
            
            assert result == 0
            mock_transcribe.assert_called_once_with("test.mp4", "/output")


def test_main_with_objects_module():
    """Test that main() calls objects module when --objects flag is set."""
    test_args = ["-i", "test.jpg", "-o", "/output", "--objects"]
    
    with patch('sys.argv', ['semantics'] + test_args):
        with patch('semantics.modules.objects.execute') as mock_objects:
            result = main()
            
            assert result == 0
            mock_objects.assert_called_once_with("test.jpg", "/output")


def test_main_with_both_modules():
    """Test that main() calls both modules when both flags are set."""
    test_args = ["-i", "test.mp4", "-o", "/output", "--transcribe", "--objects"]
    
    with patch('sys.argv', ['semantics'] + test_args):
        with patch('semantics.modules.transcribe.execute') as mock_transcribe:
            with patch('semantics.modules.objects.execute') as mock_objects:
                result = main()
                
                assert result == 0
                mock_transcribe.assert_called_once_with("test.mp4", "/output")
                mock_objects.assert_called_once_with("test.mp4", "/output")


def test_main_without_modules_exits_with_error():
    """Test that main() exits with error when no processing module is specified."""
    test_args = ["-i", "test.mp4", "-o", "/output"]
    
    with patch('sys.argv', ['semantics'] + test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Should exit with non-zero status
        assert exc_info.value.code == 2


def test_main_validates_module_execution_order():
    """Test that main() executes modules in the correct order."""
    test_args = ["-i", "test.mp4", "-o", "/output", "--transcribe", "--objects"]
    call_order = []
    
    def mock_transcribe(input_file, output_folder):
        call_order.append('transcribe')
    
    def mock_objects(input_file, output_folder):
        call_order.append('objects')
    
    with patch('sys.argv', ['semantics'] + test_args):
        with patch('semantics.modules.transcribe.execute', side_effect=mock_transcribe):
            with patch('semantics.modules.objects.execute', side_effect=mock_objects):
                result = main()
                
                assert result == 0
                assert call_order == ['transcribe', 'objects']
