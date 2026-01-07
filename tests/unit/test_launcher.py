"""Tests for the launcher module."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from semantics import launcher


class TestGetInstallDir:
    """Tests for get_install_dir function."""

    def test_get_install_dir_from_source(self) -> None:
        """Test that get_install_dir returns launcher module directory when running from source."""
        install_dir = launcher.get_install_dir()
        # When running from source, should return the directory containing launcher.py
        assert install_dir.exists()
        assert install_dir.name == "semantics"

    def test_get_install_dir_when_frozen(self) -> None:
        """Test that get_install_dir returns executable directory when frozen."""
        with patch.object(sys, "frozen", True, create=True):
            with patch.object(sys, "executable", "/usr/local/bin/semantics"):
                install_dir = launcher.get_install_dir()
                assert install_dir == Path("/usr/local/bin")


class TestDiscoverModules:
    """Tests for discover_modules function."""

    def test_discover_modules_empty_dir(self, tmp_path: Path) -> None:
        """Test discover_modules with no module executables."""
        with patch.object(launcher, "get_install_dir", return_value=tmp_path):
            modules = launcher.discover_modules()
            assert modules == {}

    def test_discover_modules_finds_audio(self, tmp_path: Path) -> None:
        """Test discover_modules finds audio module executable."""
        # Create a fake semantics-audio executable
        audio_exe = tmp_path / "semantics-audio"
        audio_exe.touch()

        with patch.object(launcher, "get_install_dir", return_value=tmp_path):
            modules = launcher.discover_modules()
            assert "audio" in modules
            assert modules["audio"] == audio_exe

    def test_discover_modules_finds_multiple(self, tmp_path: Path) -> None:
        """Test discover_modules finds multiple module executables."""
        # Create fake module executables
        (tmp_path / "semantics-audio").touch()
        (tmp_path / "semantics-video").touch()
        (tmp_path / "semantics-document").touch()

        with patch.object(launcher, "get_install_dir", return_value=tmp_path):
            modules = launcher.discover_modules()
            assert set(modules.keys()) == {"audio", "video", "document"}

    def test_discover_modules_ignores_launcher(self, tmp_path: Path) -> None:
        """Test discover_modules ignores the launcher itself."""
        # Create launcher and a module
        (tmp_path / "semantics").touch()
        (tmp_path / "semantics-audio").touch()

        with patch.object(launcher, "get_install_dir", return_value=tmp_path):
            modules = launcher.discover_modules()
            # Should only have audio, not "semantics" itself
            assert "audio" in modules
            assert "" not in modules
            assert len(modules) == 1

    def test_discover_modules_windows_exe(self, tmp_path: Path) -> None:
        """Test discover_modules handles .exe suffix on Windows."""
        # Create Windows-style executables
        (tmp_path / "semantics.exe").touch()
        (tmp_path / "semantics-audio.exe").touch()
        (tmp_path / "semantics-video.exe").touch()

        with patch.object(launcher, "get_install_dir", return_value=tmp_path):
            with patch.object(sys, "platform", "win32"):
                modules = launcher.discover_modules()
                assert "audio" in modules
                assert "video" in modules

    def test_discover_modules_ignores_directories(self, tmp_path: Path) -> None:
        """Test discover_modules ignores directories matching the pattern."""
        # Create a directory that matches the pattern (shouldn't be picked up)
        (tmp_path / "semantics-audio").mkdir()
        # Create a real executable
        (tmp_path / "semantics-video").touch()

        with patch.object(launcher, "get_install_dir", return_value=tmp_path):
            modules = launcher.discover_modules()
            assert "audio" not in modules
            assert "video" in modules


class TestGetVersion:
    """Tests for get_version function."""

    def test_get_version(self) -> None:
        """Test get_version returns version info."""
        version = launcher.get_version()
        # Should return a version string (either actual or "unknown")
        assert isinstance(version, str)
        assert len(version) > 0


class TestLauncherCLI:
    """Tests for the Click-based launcher CLI."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI test runner."""
        return CliRunner()

    def test_main_no_args_shows_help(self, runner: CliRunner) -> None:
        """Test main with no arguments shows help."""
        # Patch discovered modules to empty for predictable output
        with patch.object(launcher, "_discovered_modules", {}):
            result = runner.invoke(launcher.main, [])
            assert result.exit_code == 0
            assert "Semantics CLI" in result.output

    def test_main_help_flag(self, runner: CliRunner) -> None:
        """Test main with --help flag shows help."""
        with patch.object(launcher, "_discovered_modules", {}):
            result = runner.invoke(launcher.main, ["--help"])
            assert result.exit_code == 0
            assert "Semantics CLI" in result.output

    def test_main_version_flag(self, runner: CliRunner) -> None:
        """Test main with --version flag shows version."""
        result = runner.invoke(launcher.main, ["--version"])
        assert result.exit_code == 0
        # Should show 'semantics' not 'semantics launcher'
        assert "semantics" in result.output.lower()
        assert "launcher" not in result.output.lower()

    def test_main_lists_installed_modules(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test main lists installed modules in help."""
        # Create fake module executables
        audio_exe = tmp_path / "semantics-audio"
        video_exe = tmp_path / "semantics-video"
        audio_exe.touch()
        video_exe.touch()

        fake_modules = {"audio": audio_exe, "video": video_exe}
        with patch.object(launcher, "_discovered_modules", fake_modules):
            result = runner.invoke(launcher.main, ["--help"])
            assert result.exit_code == 0
            # Check that modules are listed as commands
            assert "audio" in result.output
            assert "video" in result.output

    def test_main_missing_module_error(self, runner: CliRunner) -> None:
        """Test main with non-existent module shows error."""
        with patch.object(launcher, "_discovered_modules", {}):
            result = runner.invoke(launcher.main, ["nonexistent"])
            assert result.exit_code != 0

    def test_main_delegates_to_module(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test main creates a delegating command for installed modules."""
        # Create a fake module executable
        audio_exe = tmp_path / "semantics-audio"
        audio_exe.touch()

        fake_modules = {"audio": audio_exe}

        with patch.object(launcher, "_discovered_modules", fake_modules):
            # Verify the command is available
            result = runner.invoke(launcher.main, ["--help"])
            assert result.exit_code == 0
            # The 'audio' command should be listed
            assert "audio" in result.output

    def test_main_unknown_module_error(self, runner: CliRunner) -> None:
        """Test main shows error for unknown module."""
        with patch.object(launcher, "_discovered_modules", {}):
            result = runner.invoke(launcher.main, ["nonexistent"])
            assert result.exit_code != 0
            # Click shows "No such command" for unknown commands
            assert "No such command" in result.output or "nonexistent" in result.output

    def test_main_module_execution_integration(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that module command is set up correctly for execution."""
        # This test verifies the command structure, not actual subprocess execution
        audio_exe = tmp_path / "semantics-audio"
        audio_exe.touch()

        fake_modules = {"audio": audio_exe}

        with patch.object(launcher, "_discovered_modules", fake_modules):
            # Get the dynamically created command
            ctx = launcher.main.make_context("main", [])
            cmd = launcher.main.get_command(ctx, "audio")

            assert cmd is not None
            assert cmd.name == "audio"


class TestGenerateHelpText:
    """Tests for generate_help_text function."""

    def test_help_with_modules(self) -> None:
        """Test help text includes examples for installed modules."""
        with patch.object(
            launcher,
            "_discovered_modules",
            {"audio": Path("/bin/semantics-audio"), "video": Path("/bin/semantics-video")},
        ):
            help_text = launcher.generate_help_text()
            assert "Semantics CLI" in help_text
            assert "audio" in help_text
            assert "video" in help_text

    def test_help_no_modules(self) -> None:
        """Test help text with no modules installed."""
        with patch.object(launcher, "_discovered_modules", {}):
            help_text = launcher.generate_help_text()
            assert "No modules installed" in help_text


class TestGetVirtualModules:
    """Tests for get_virtual_modules function."""

    def test_expands_full_to_individual_modules(self) -> None:
        """Test that 'full' is expanded to audio, video, document modules."""
        full_exe = Path("/bin/semantics-full")
        discovered = {"full": full_exe}

        result = launcher.get_virtual_modules(discovered)

        # Should have audio, video, document pointing to full
        assert "audio" in result
        assert "video" in result
        assert "document" in result
        assert result["audio"] == full_exe
        assert result["video"] == full_exe
        assert result["document"] == full_exe
        # 'full' should be hidden from user
        assert "full" not in result

    def test_does_not_override_existing_modules(self) -> None:
        """Test that existing modules are not overridden by full expansion."""
        full_exe = Path("/bin/semantics-full")
        audio_exe = Path("/bin/semantics-audio")
        discovered = {"full": full_exe, "audio": audio_exe}

        result = launcher.get_virtual_modules(discovered)

        # audio should still point to its own executable
        assert result["audio"] == audio_exe
        # video and document should point to full
        assert result["video"] == full_exe
        assert result["document"] == full_exe

    def test_no_full_returns_unchanged(self) -> None:
        """Test that without 'full', modules are returned unchanged."""
        audio_exe = Path("/bin/semantics-audio")
        discovered = {"audio": audio_exe}

        result = launcher.get_virtual_modules(discovered)

        assert result == {"audio": audio_exe}
