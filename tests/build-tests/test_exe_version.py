"""Tests for --version functionality in built executables."""

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
class TestExecutableVersion:
    """Test --version works for all executable variants."""

    def test_audio_exe_version(self, audio_exe: Path) -> None:
        """Test semantics-audio --version shows version."""
        result = run_executable(audio_exe, ["--version"])
        assert result.returncode == 0
        # Version should be in output (could be semver or dev format)
        assert "version" in result.stdout.lower() or "." in result.stdout

    def test_video_exe_version(self, video_exe: Path) -> None:
        """Test semantics-video --version shows version."""
        result = run_executable(video_exe, ["--version"])
        assert result.returncode == 0

    def test_document_exe_version(self, document_exe: Path) -> None:
        """Test semantics-document --version shows version."""
        result = run_executable(document_exe, ["--version"])
        assert result.returncode == 0
