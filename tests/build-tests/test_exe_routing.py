"""Tests for extension-based routing and cross-module routing in built executables."""

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
class TestExtensionRouting:
    """Test extension-based auto-routing in module executables."""

    def test_auto_route_audio_extension(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test auto-routing for audio file extensions."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["-i", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode == 0
        assert "Transcribing" in result.stdout or "transcrib" in result.stdout.lower()

    def test_auto_route_video_extension(self, video_exe: Path, tmp_path: Path) -> None:
        """Test auto-routing for video file extensions."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe, ["-i", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode == 0
        assert "Transcribing" in result.stdout or "transcrib" in result.stdout.lower()

    def test_auto_route_document_extension(self, document_exe: Path, tmp_path: Path) -> None:
        """Test auto-routing for document file extensions."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document content")
        output_dir = tmp_path / "output"

        result = run_executable(
            document_exe, ["-i", str(input_file), "-o", str(output_dir), "--extract-text"]
        )
        assert result.returncode == 0
        assert "Extracting" in result.stdout or "extract" in result.stdout.lower()

    def test_unsupported_extension_error(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test error for unsupported file extension."""
        input_file = tmp_path / "test.xyz"
        input_file.write_text("dummy content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["-i", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "unsupported" in combined_output.lower() or "extension" in combined_output.lower()

@pytest.mark.build
class TestCrossModuleRouting:
    """Test cross-module fallback routing (e.g., audio module handling video files)."""

    def test_audio_exe_transcribe_video_file(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio executable can transcribe video files (audio extraction)."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        # This should work - audio module can handle video files for transcription
        result = run_executable(
            audio_exe, ["-i", str(input_file), "-o", str(output_dir), "--transcribe"]
        )
        assert result.returncode == 0
        assert "Transcribing" in result.stdout or "transcrib" in result.stdout.lower()

    def test_audio_exe_rejects_video_detect_objects(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio executable rejects video-only operations on video files."""
        input_file = tmp_path / "test.mp4"
        input_file.write_text("dummy video content")
        output_dir = tmp_path / "output"

        # --detect-objects is video-only, should fail on audio-only executable
        result = run_executable(
            audio_exe, ["-i", str(input_file), "-o", str(output_dir), "--detect-objects"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        # Should mention video module not available
        assert "video" in combined_output.lower() or "not available" in combined_output.lower()

    def test_audio_exe_rejects_document_file(self, audio_exe: Path, tmp_path: Path) -> None:
        """Test audio executable rejects document files with extract-text."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document content")
        output_dir = tmp_path / "output"

        result = run_executable(
            audio_exe, ["-i", str(input_file), "-o", str(output_dir), "--extract-text"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        # Should mention document module not available or suggest alternative
        assert "document" in combined_output.lower() or "not available" in combined_output.lower()

    def test_video_exe_cannot_extract_metadata(self, video_exe: Path, tmp_path: Path) -> None:
        """Test video executable cannot use audio-only extract-metadata on audio files."""
        input_file = tmp_path / "test.wav"
        input_file.write_text("dummy audio content")
        output_dir = tmp_path / "output"

        result = run_executable(
            video_exe, ["-i", str(input_file), "-o", str(output_dir), "--extract-metadata"]
        )
        assert result.returncode != 0
        combined_output = result.stdout + result.stderr
        assert "audio" in combined_output.lower() or "not available" in combined_output.lower()
