"""Tests for the audio module commands with chained flags."""

import pytest
from click.testing import CliRunner

from semantics.cli import main


class TestAudioModule:
    """Tests for the audio module commands with chained flags."""

    def test_audio_help(self, runner: CliRunner) -> None:
        """Test audio subcommand help."""
        result = runner.invoke(main, ["audio", "--help"])
        assert result.exit_code == 0
        assert "--transcribe" in result.output
        assert "--extract-metadata" in result.output
        assert "--verbose" in result.output

    def test_audio_requires_operation(self, runner: CliRunner, tmp_path) -> None:
        """Test that audio requires at least one operation flag."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy")
        result = runner.invoke(main, ["audio", str(input_file), "-o", str(tmp_path / "out")])
        assert result.exit_code != 0
        assert "At least one operation" in result.output

    def test_audio_transcribe(self, runner: CliRunner, tmp_path) -> None:
        """Test audio transcription with --transcribe flag."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["audio", str(input_file), "-o", str(output_dir), "--transcribe"],
        )
        assert result.exit_code == 0
        assert "Transcribing" in result.output
        assert "complete" in result.output.lower()

    def test_audio_extract_metadata(self, runner: CliRunner, tmp_path) -> None:
        """Test audio metadata extraction with --extract-metadata flag."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["audio", str(input_file), "-o", str(output_dir), "--extract-metadata"],
        )
        assert result.exit_code == 0
        assert "Extracting metadata" in result.output
        assert "complete" in result.output.lower()

    def test_audio_chained_operations(self, runner: CliRunner, tmp_path) -> None:
        """Test chaining multiple audio operations."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["audio", str(input_file), "-o", str(output_dir), "--transcribe", "--extract-metadata"],
        )
        assert result.exit_code == 0
        assert "Transcribing" in result.output
        assert "Extracting metadata" in result.output

    def test_audio_verbose_flag(self, runner: CliRunner, tmp_path) -> None:
        """Test that --verbose flag produces additional output."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["audio", str(input_file), "-o", str(output_dir), "--transcribe", "-v"],
        )
        assert result.exit_code == 0
        assert "[OPTIONS]" in result.output
