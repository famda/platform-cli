"""Tests for error handling in built executables."""

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
class TestErrorHandling:
    """Test error handling in built executables."""

    def test_missing_operation_flag(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test error when no operation flag is provided."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["audio", str(input_file), "-o", str(output_dir)]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "at least one operation" in combined_output.lower()

    def test_missing_input_file(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test error when input file doesn't exist."""
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe,
            ["audio", str(tmp_path / "nonexistent.wav"), "-o", str(output_dir), "--transcribe"],
        )
        assert result.returncode != 0

    def test_missing_output_option(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test error when --output option is missing."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")

        result = run_executable(audio_exe, ["audio", str(input_file), "--transcribe"])
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "required" in combined_output.lower() or "missing" in combined_output.lower()
