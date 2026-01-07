"""Tests for module availability and rejection in built executables."""

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
class TestModuleAvailability:
    """Test that each variant has only its expected modules."""

    def test_full_exe_has_all_modules(self, full_exe: Path) -> None:
        """Test full executable can access all module subcommands."""
        for module in ["audio", "video", "document"]:
            result = run_executable(full_exe, [module, "--help"])
            assert result.returncode == 0, f"Module {module} should be available"

    def test_audio_exe_has_audio_only(self, audio_exe: Path) -> None:
        """Test audio executable has audio module."""
        result = run_executable(audio_exe, ["audio", "--help"])
        assert result.returncode == 0

    def test_video_exe_has_video_only(self, video_exe: Path) -> None:
        """Test video executable has video module."""
        result = run_executable(video_exe, ["video", "--help"])
        assert result.returncode == 0

    def test_document_exe_has_document_only(self, document_exe: Path) -> None:
        """Test document executable has document module."""
        result = run_executable(document_exe, ["document", "--help"])
        assert result.returncode == 0


@pytest.mark.build
class TestModuleRejection:
    """Test that single-module variants reject unavailable modules."""

    def test_audio_exe_rejects_video(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio executable rejects video subcommand."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["video", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode != 0
        # Check for "not available" or similar error
        combined_output = result.stdout + result.stderr
        assert "no such command" in combined_output.lower() or "not available" in combined_output.lower()

    def test_audio_exe_rejects_document(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio executable rejects document subcommand."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["document", str(input_file), "-o", str(output_dir), "--extract-text"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "no such command" in combined_output.lower() or "not available" in combined_output.lower()

    def test_video_exe_rejects_audio(self, video_exe: Path, tmp_path: Path) -> None:
        """Test video executable rejects audio subcommand."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe, ["audio", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "no such command" in combined_output.lower() or "not available" in combined_output.lower()

    def test_video_exe_rejects_document(self, video_exe: Path, tmp_path: Path) -> None:
        """Test video executable rejects document subcommand."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe, ["document", str(input_file), "-o", str(output_dir), "--extract-text"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "no such command" in combined_output.lower() or "not available" in combined_output.lower()

    def test_document_exe_rejects_audio(self, document_exe: Path, tmp_path: Path) -> None:
        """Test document executable rejects audio subcommand."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio")
        output_dir = tmp_path / "output"

        result = run_executable(
            document_exe, ["audio", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "no such command" in combined_output.lower() or "not available" in combined_output.lower()

    def test_document_exe_rejects_video(self, document_exe: Path, tmp_path: Path) -> None:
        """Test document executable rejects video subcommand."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video")
        output_dir = tmp_path / "output"

        result = run_executable(
            document_exe, ["video", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "no such command" in combined_output.lower() or "not available" in combined_output.lower()
