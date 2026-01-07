"""Tests for direct input processing and extension-based routing."""

import pytest
from click.testing import CliRunner

from semantics.cli import main


class TestDirectInputProcessing:
    """Tests for direct input processing using -i/--input option."""

    def test_direct_audio_transcribe(self, runner: CliRunner, tmp_path) -> None:
        """Test direct audio transcription with -i option."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir), "--transcribe"],
        )
        assert result.exit_code == 0
        assert "Transcribing" in result.output

    def test_direct_video_detect_objects(self, runner: CliRunner, tmp_path) -> None:
        """Test direct video object detection with -i option."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir), "--detect-objects"],
        )
        assert result.exit_code == 0
        assert "Detecting objects" in result.output

    def test_direct_document_extract_text(self, runner: CliRunner, tmp_path) -> None:
        """Test direct document text extraction with -i option."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy pdf")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir), "--extract-text"],
        )
        assert result.exit_code == 0
        assert "Extracting text" in result.output

    def test_direct_chained_operations(self, runner: CliRunner, tmp_path) -> None:
        """Test chaining multiple operations with -i option."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir), "--transcribe", "--extract-metadata"],
        )
        assert result.exit_code == 0
        assert "Transcribing" in result.output
        assert "Extracting metadata" in result.output

    def test_direct_with_options(self, runner: CliRunner, tmp_path) -> None:
        """Test direct input with additional options passed through."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir), "--transcribe", "-v", "-l", "es"],
        )
        assert result.exit_code == 0
        assert "[OPTIONS]" in result.output

    def test_direct_requires_output(self, runner: CliRunner, tmp_path) -> None:
        """Test that --output is required when processing a file."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video")

        result = runner.invoke(
            main,
            ["-i", str(input_file), "--transcribe"],
        )
        assert result.exit_code != 0
        assert "--output" in result.output or "-o" in result.output

    def test_direct_unsupported_extension(self, runner: CliRunner, tmp_path) -> None:
        """Test error for unsupported file extension."""
        input_file = tmp_path / "test.xyz"
        input_file.write_text("dummy")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir), "--transcribe"],
        )
        assert result.exit_code != 0
        assert "Unsupported file extension" in result.output

    def test_direct_requires_operation(self, runner: CliRunner, tmp_path) -> None:
        """Test that direct input requires at least one operation flag."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["-i", str(input_file), "-o", str(output_dir)],
        )
        assert result.exit_code != 0
        assert "At least one operation" in result.output
