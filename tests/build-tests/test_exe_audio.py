"""Tests for audio processing functionality in built executables."""

from pathlib import Path
import subprocess
import sys

import pytest


def run_executable(exe_path: Path, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run an executable with the given arguments."""
    return subprocess.run(
        [str(exe_path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


@pytest.mark.build
class TestAudioExecution:
    """Test audio processing functionality in built executables."""

    def test_audio_exe_transcribe(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio transcription works in audio executable."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["audio", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode == 0
        assert "Transcribing" in result.stdout or "transcrib" in result.stdout.lower()

    def test_audio_exe_extract_metadata(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio metadata extraction works in audio executable."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["audio", str(input_file), "-o", str(output_dir), "--extract-metadata"]
        )
        assert result.returncode == 0
        assert "metadata" in result.stdout.lower() or "Extracting" in result.stdout

    def test_audio_exe_chained_operations(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test chained audio operations work in audio executable."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe,
            ["audio", str(input_file), "-o", str(output_dir), "--transcribe", "--extract-metadata"],
        )
        assert result.returncode == 0
        # Both operations should run
        stdout_lower = result.stdout.lower()
        assert "transcrib" in stdout_lower
        assert "metadata" in stdout_lower or "extract" in stdout_lower

    def test_audio_exe_verbose(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test verbose flag works in audio executable."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["audio", str(input_file), "-o", str(output_dir), "--transcribe", "-v"]
        )
        assert result.returncode == 0
        # Verbose output should include options info
        assert "Options" in result.stdout or "language" in result.stdout.lower()
