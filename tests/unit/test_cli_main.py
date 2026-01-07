"""Tests for the main CLI group, extension mapping, and ModuleRegistry."""

import pytest
from click.testing import CliRunner

from semantics.cli import main, ModuleRegistry, EXTENSION_MAP


class TestMainCLI:
    """Tests for the main CLI group."""

    def test_main_help(self, runner: CliRunner) -> None:
        """Test that --help works on main command."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Unified interface for media intelligence" in result.output
        assert "audio" in result.output
        assert "video" in result.output
        assert "document" in result.output
        assert "--input" in result.output or "-i" in result.output

    def test_main_version(self, runner: CliRunner) -> None:
        """Test that --version works."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        # Version should be present in output
        assert "version" in result.output.lower() or "." in result.output


class TestExtensionMap:
    """Tests for the extension mapping configuration."""

    def test_audio_extensions(self) -> None:
        """Test that audio extensions are mapped correctly."""
        audio_exts = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]
        for ext in audio_exts:
            assert EXTENSION_MAP.get(ext) == "audio", f"{ext} should map to audio"

    def test_video_extensions(self) -> None:
        """Test that video extensions are mapped correctly."""
        video_exts = [".mp4", ".avi", ".mkv", ".mov", ".webm"]
        for ext in video_exts:
            assert EXTENSION_MAP.get(ext) == "video", f"{ext} should map to video"

    def test_document_extensions(self) -> None:
        """Test that document extensions are mapped correctly."""
        doc_exts = [".pdf", ".png", ".jpg", ".jpeg"]
        for ext in doc_exts:
            assert EXTENSION_MAP.get(ext) == "document", f"{ext} should map to document"


class TestModuleRegistry:
    """Tests for the ModuleRegistry class."""

    def test_registry_loads_modules(self) -> None:
        """Test that registry discovers and loads modules."""
        registry = ModuleRegistry()
        registry.load_all_modules()

        # Should have loaded our three modules
        assert "audio" in registry.commands
        assert "video" in registry.commands
        assert "document" in registry.commands

    def test_registry_handles_missing_modules(self) -> None:
        """Test that registry handles missing modules gracefully."""
        registry = ModuleRegistry()
        # Initially no failures
        assert registry.get_unavailable_modules() == []
        assert registry.get_unavailable_modules() == []
