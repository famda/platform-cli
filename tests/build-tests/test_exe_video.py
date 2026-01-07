"""Tests for video processing functionality in built executables."""

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
class TestVideoExecution:
    """Test video processing functionality in built executables."""

    def test_video_exe_transcribe(self, video_exe: Path, tmp_path: Path) -> None:
        """Test video transcription works in video executable."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe, ["video", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode == 0
        assert "Transcribing" in result.stdout or "transcrib" in result.stdout.lower()

    def test_video_exe_detect_objects(self, video_exe: Path, tmp_path: Path) -> None:
        """Test video object detection works in video executable."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe, ["video", str(input_file), "-o", str(output_dir), "--detect-objects"]
        )
        assert result.returncode == 0
        assert "Detecting" in result.stdout or "detect" in result.stdout.lower()

    def test_video_exe_detect_objects_with_confidence(self, video_exe: Path, tmp_path: Path) -> None:
        """Test video object detection with confidence threshold."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe,
            ["video", str(input_file), "-o", str(output_dir), "--detect-objects", "-c", "0.7"],
        )
        assert result.returncode == 0

    def test_video_exe_chained_operations(self, video_exe: Path, tmp_path: Path) -> None:
        """Test chained video operations work in video executable."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe,
            ["video", str(input_file), "-o", str(output_dir), "--transcribe", "--detect-objects"],
        )
        assert result.returncode == 0
        stdout_lower = result.stdout.lower()
        assert "transcrib" in stdout_lower
        assert "detect" in stdout_lower
