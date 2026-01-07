"""Tests for the video module commands with chained flags."""

import pytest
from click.testing import CliRunner

from semantics.cli import main


class TestVideoModule:
    """Tests for the video module commands with chained flags."""

    def test_video_help(self, runner: CliRunner) -> None:
        """Test video subcommand help."""
        result = runner.invoke(main, ["video", "--help"])
        assert result.exit_code == 0
        assert "--transcribe" in result.output
        assert "--detect-objects" in result.output
        assert "--verbose" in result.output

    def test_video_requires_operation(self, runner: CliRunner, tmp_path) -> None:
        """Test that video requires at least one operation flag."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy")
        result = runner.invoke(main, ["video", str(input_file), "-o", str(tmp_path / "out")])
        assert result.exit_code != 0
        assert "At least one operation" in result.output

    def test_video_detect_objects(self, runner: CliRunner, tmp_path) -> None:
        """Test video object detection with --detect-objects flag."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["video", str(input_file), "-o", str(output_dir), "--detect-objects"],
        )
        assert result.exit_code == 0
        assert "Detecting objects" in result.output
        assert "complete" in result.output.lower()

    def test_video_chained_operations(self, runner: CliRunner, tmp_path) -> None:
        """Test chaining multiple video operations."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["video", str(input_file), "-o", str(output_dir), "--transcribe", "--detect-objects"],
        )
        assert result.exit_code == 0
        assert "Transcribing" in result.output
        assert "Detecting objects" in result.output
