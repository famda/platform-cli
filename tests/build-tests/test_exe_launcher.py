"""Tests for the launcher executable behavior."""

from pathlib import Path
import subprocess
import sys
import shutil

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
class TestLauncherHelp:
    """Test launcher help and version output."""

    def test_launcher_help(self, launcher_exe: Path) -> None:
        """Test launcher --help shows available modules."""
        result = run_executable(launcher_exe, ["--help"])
        assert result.returncode == 0
        assert "Semantics CLI" in result.stdout

    def test_launcher_version(self, launcher_exe: Path) -> None:
        """Test launcher --version works."""
        result = run_executable(launcher_exe, ["--version"])
        assert result.returncode == 0
        # Should show 'semantics' but NOT 'launcher'
        assert "semantics" in result.stdout.lower()
        assert "launcher" not in result.stdout.lower()


@pytest.mark.build
class TestLauncherModuleDiscovery:
    """Test launcher discovers and delegates to module executables."""

    def test_launcher_discovers_audio_module(
        self, launcher_exe: Path, audio_exe: Path, tmp_path: Path
    ) -> None:
        """Test launcher can discover and delegate to audio module."""
        # Copy launcher and audio exe to a temp directory
        test_dir = tmp_path / "bin"
        test_dir.mkdir()
        
        # Copy launcher
        launcher_name = "semantics.exe" if sys.platform == "win32" else "semantics"
        shutil.copy(launcher_exe, test_dir / launcher_name)
        
        # Copy audio module
        audio_name = "semantics-audio.exe" if sys.platform == "win32" else "semantics-audio"
        shutil.copy(audio_exe, test_dir / audio_name)
        
        # Run launcher with audio subcommand
        test_launcher = test_dir / launcher_name
        result = run_executable(test_launcher, ["audio", "--help"])
        
        # Should successfully delegate to audio module
        assert result.returncode == 0
        assert "audio" in result.stdout.lower() or "transcribe" in result.stdout.lower()

    def test_launcher_shows_installed_modules(
        self, launcher_exe: Path, audio_exe: Path, video_exe: Path, tmp_path: Path
    ) -> None:
        """Test launcher shows only installed modules in help."""
        # Copy launcher and modules to temp directory
        test_dir = tmp_path / "bin"
        test_dir.mkdir()
        
        launcher_name = "semantics.exe" if sys.platform == "win32" else "semantics"
        shutil.copy(launcher_exe, test_dir / launcher_name)
        
        audio_name = "semantics-audio.exe" if sys.platform == "win32" else "semantics-audio"
        shutil.copy(audio_exe, test_dir / audio_name)
        
        video_name = "semantics-video.exe" if sys.platform == "win32" else "semantics-video"
        shutil.copy(video_exe, test_dir / video_name)
        
        # Run launcher help
        test_launcher = test_dir / launcher_name
        result = run_executable(test_launcher, ["--help"])
        
        assert result.returncode == 0
        # Should show both installed modules
        assert "audio" in result.stdout
        assert "video" in result.stdout


@pytest.mark.build
class TestLauncherMissingModule:
    """Test launcher error handling for missing modules."""

    def test_launcher_error_for_missing_module(
        self, launcher_exe: Path, tmp_path: Path
    ) -> None:
        """Test launcher shows error when module is not installed."""
        # Copy only the launcher (no modules)
        test_dir = tmp_path / "bin"
        test_dir.mkdir()
        
        launcher_name = "semantics.exe" if sys.platform == "win32" else "semantics"
        shutil.copy(launcher_exe, test_dir / launcher_name)
        
        # Run launcher with a module that doesn't exist
        test_launcher = test_dir / launcher_name
        result = run_executable(test_launcher, ["audio", "--help"])
        
        assert result.returncode != 0
        # Click shows "No such command" for unknown commands
        assert "no such command" in result.stderr.lower()

    def test_launcher_shows_no_modules_help(
        self, launcher_exe: Path, tmp_path: Path
    ) -> None:
        """Test launcher help when no modules are installed."""
        # Copy only the launcher
        test_dir = tmp_path / "bin"
        test_dir.mkdir()
        
        launcher_name = "semantics.exe" if sys.platform == "win32" else "semantics"
        shutil.copy(launcher_exe, test_dir / launcher_name)
        
        test_launcher = test_dir / launcher_name
        result = run_executable(test_launcher, ["--help"])
        
        assert result.returncode == 0
        assert "no modules installed" in result.stdout.lower()


@pytest.mark.build
class TestLauncherWithMultipleModules:
    """Test launcher with multiple individual module executables."""

    def test_launcher_with_all_modules_shows_all_commands(
        self, launcher_exe: Path, audio_exe: Path, video_exe: Path, document_exe: Path, tmp_path: Path
    ) -> None:
        """Test launcher with all module executables shows all commands."""
        # Copy launcher and all module executables to temp directory
        test_dir = tmp_path / "bin"
        test_dir.mkdir()
        
        launcher_name = "semantics.exe" if sys.platform == "win32" else "semantics"
        audio_name = "semantics-audio.exe" if sys.platform == "win32" else "semantics-audio"
        video_name = "semantics-video.exe" if sys.platform == "win32" else "semantics-video"
        document_name = "semantics-document.exe" if sys.platform == "win32" else "semantics-document"
        
        shutil.copy(launcher_exe, test_dir / launcher_name)
        shutil.copy(audio_exe, test_dir / audio_name)
        shutil.copy(video_exe, test_dir / video_name)
        shutil.copy(document_exe, test_dir / document_name)
        
        # Run launcher help
        test_launcher = test_dir / launcher_name
        result = run_executable(test_launcher, ["--help"])
        
        assert result.returncode == 0
        # Should show audio, video, document as available commands
        assert "audio" in result.stdout
        assert "video" in result.stdout
        assert "document" in result.stdout

    def test_launcher_delegates_to_individual_modules(
        self, launcher_exe: Path, audio_exe: Path, tmp_path: Path
    ) -> None:
        """Test launcher delegates to individual module executable."""
        test_dir = tmp_path / "bin"
        test_dir.mkdir()
        
        launcher_name = "semantics.exe" if sys.platform == "win32" else "semantics"
        audio_name = "semantics-audio.exe" if sys.platform == "win32" else "semantics-audio"
        
        shutil.copy(launcher_exe, test_dir / launcher_name)
        shutil.copy(audio_exe, test_dir / audio_name)
        
        # Run launcher with audio subcommand
        test_launcher = test_dir / launcher_name
        result = run_executable(test_launcher, ["audio", "--help"])
        
        # Should successfully delegate to audio module
        assert result.returncode == 0
        assert "transcribe" in result.stdout.lower() or "audio" in result.stdout.lower()
