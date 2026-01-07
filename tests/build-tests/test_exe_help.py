"""Tests for --help functionality in built executables."""

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
class TestExecutableHelp:
    """Test --help works for all executable variants."""

    def test_full_exe_help(self, full_exe: Path) -> None:
        """Test semantics --help shows all subcommands."""
        result = run_executable(full_exe, ["--help"])
        assert result.returncode == 0
        assert "Unified interface for media intelligence" in result.stdout
        # Check Commands section has all modules
        commands_section = result.stdout.split("Commands:")[1] if "Commands:" in result.stdout else ""
        assert "audio" in commands_section
        assert "video" in commands_section
        assert "document" in commands_section

    def test_audio_exe_help(self, audio_exe: Path) -> None:
        """Test semantics-audio --help shows audio subcommand only."""
        result = run_executable(audio_exe, ["--help"])
        assert result.returncode == 0
        assert "Unified interface for media intelligence" in result.stdout
        # Check Commands section has only audio module
        commands_section = result.stdout.split("Commands:")[1] if "Commands:" in result.stdout else ""
        assert "audio" in commands_section
        assert "video" not in commands_section
        assert "document" not in commands_section

    def test_video_exe_help(self, video_exe: Path) -> None:
        """Test semantics-video --help shows video subcommand only."""
        result = run_executable(video_exe, ["--help"])
        assert result.returncode == 0
        assert "Unified interface for media intelligence" in result.stdout
        # Check Commands section has only video module
        commands_section = result.stdout.split("Commands:")[1] if "Commands:" in result.stdout else ""
        assert "video" in commands_section
        assert "audio" not in commands_section
        assert "document" not in commands_section

    def test_document_exe_help(self, document_exe: Path) -> None:
        """Test semantics-document --help shows document subcommand only."""
        result = run_executable(document_exe, ["--help"])
        assert result.returncode == 0
        assert "Unified interface for media intelligence" in result.stdout
        # Check Commands section has only document module
        commands_section = result.stdout.split("Commands:")[1] if "Commands:" in result.stdout else ""
        assert "document" in commands_section
        assert "audio" not in commands_section
        assert "video" not in commands_section


@pytest.mark.build
class TestDynamicHelp:
    """Test that help text is dynamically generated based on available modules."""

    def test_audio_exe_help_no_video_examples(self, audio_exe: Path) -> None:
        """Test audio executable help does not contain video examples."""
        result = run_executable(audio_exe, ["--help"])
        assert result.returncode == 0

        # Split at Examples: to get the examples section
        if "Examples:" in result.stdout:
            examples_section = result.stdout.split("Examples:")[1].split("Or use explicit")[0]
            # Should have audio examples
            assert "input.wav" in examples_section
            # Should NOT have video-specific examples (detect-objects is video-only)
            assert "--detect-objects" not in examples_section
            # Should NOT have document examples
            assert "document.pdf" not in examples_section
            assert "--extract-text" not in examples_section

    def test_video_exe_help_no_audio_examples(self, video_exe: Path) -> None:
        """Test video executable help does not contain audio examples."""
        result = run_executable(video_exe, ["--help"])
        assert result.returncode == 0

        if "Examples:" in result.stdout:
            examples_section = result.stdout.split("Examples:")[1].split("Or use explicit")[0]
            # Should have video examples
            assert "input.mp4" in examples_section
            # Should NOT have audio-only examples (extract-metadata is audio-only)
            assert "--extract-metadata" not in examples_section
            # Should NOT have document examples
            assert "document.pdf" not in examples_section
            assert "--extract-text" not in examples_section

    def test_document_exe_help_no_audio_video_examples(self, document_exe: Path) -> None:
        """Test document executable help does not contain audio/video examples."""
        result = run_executable(document_exe, ["--help"])
        assert result.returncode == 0

        if "Examples:" in result.stdout:
            examples_section = result.stdout.split("Examples:")[1].split("Or use explicit")[0]
            # Should have document examples
            assert "document.pdf" in examples_section or ".pdf" in examples_section
            # Should NOT have audio examples
            assert "input.wav" not in examples_section
            assert "--extract-metadata" not in examples_section
            # Should NOT have video examples
            assert "--detect-objects" not in examples_section

    def test_full_exe_help_has_all_examples(self, full_exe: Path) -> None:
        """Test full executable help contains all module examples."""
        result = run_executable(full_exe, ["--help"])
        assert result.returncode == 0

        if "Examples:" in result.stdout:
            examples_section = result.stdout.split("Examples:")[1].split("Or use explicit")[0]
            # Should have examples for all modules
            assert "input.wav" in examples_section
            assert "input.mp4" in examples_section
            assert "document.pdf" in examples_section
