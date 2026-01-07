"""Tests for dynamic help text generation and extension configuration."""

import pytest


class TestDynamicHelpGeneration:
    """Tests for dynamic help text generation."""

    def test_generate_help_with_all_modules(self) -> None:
        """Test help generation includes all module examples when all available."""
        from semantics.cli import generate_dynamic_help

        help_text = generate_dynamic_help({"audio", "video", "document"})

        # Should contain examples for all modules
        assert "input.wav" in help_text
        assert "input.mp4" in help_text
        assert "document.pdf" in help_text
        assert "--transcribe" in help_text
        assert "--detect-objects" in help_text
        assert "--extract-text" in help_text

    def test_generate_help_audio_only(self) -> None:
        """Test help generation with only audio module available."""
        from semantics.cli import generate_dynamic_help

        help_text = generate_dynamic_help({"audio"})

        # Should contain audio examples
        assert "input.wav" in help_text
        assert "--transcribe" in help_text

        # Should NOT contain video-specific or document examples
        assert "--detect-objects" not in help_text
        assert "document.pdf" not in help_text
        assert "--extract-text" not in help_text

    def test_generate_help_video_only(self) -> None:
        """Test help generation with only video module available."""
        from semantics.cli import generate_dynamic_help

        help_text = generate_dynamic_help({"video"})

        # Should contain video examples
        assert "input.mp4" in help_text
        assert "--detect-objects" in help_text

        # Should NOT contain audio-only examples (extract-metadata is audio-only)
        assert "--extract-metadata" not in help_text
        assert "document.pdf" not in help_text

    def test_generate_help_document_only(self) -> None:
        """Test help generation with only document module available."""
        from semantics.cli import generate_dynamic_help

        help_text = generate_dynamic_help({"document"})

        # Should contain document examples
        assert "document.pdf" in help_text
        assert "--extract-text" in help_text

        # Should NOT contain audio or video examples
        assert "input.wav" not in help_text
        assert "--detect-objects" not in help_text

    def test_generate_help_empty_modules(self) -> None:
        """Test help generation with no modules available."""
        from semantics.cli import generate_dynamic_help

        help_text = generate_dynamic_help(set())

        # Should still have base text
        assert "Unified interface for media intelligence" in help_text
        # But no examples
        assert "--transcribe" not in help_text
        assert "--detect-objects" not in help_text
        assert "--extract-text" not in help_text


class TestAudioCompatibleExtensions:
    """Tests for audio-compatible video extensions configuration."""

    def test_video_extensions_in_audio_compatible(self) -> None:
        """Test that video extensions are listed in audio compatible set."""
        from semantics.cli import AUDIO_COMPATIBLE_VIDEO_EXTENSIONS

        # These video formats should be processable by audio module for transcription
        video_exts = [".mp4", ".avi", ".mkv", ".mov", ".webm"]
        for ext in video_exts:
            assert ext in AUDIO_COMPATIBLE_VIDEO_EXTENSIONS, f"{ext} should be audio-compatible"

    def test_transcribe_is_audio_compatible_flag(self) -> None:
        """Test that --transcribe is listed as audio-compatible flag."""
        from semantics.cli import AUDIO_COMPATIBLE_FLAGS

        assert "--transcribe" in AUDIO_COMPATIBLE_FLAGS


class TestGetAvailableExtensions:
    """Tests for the get_available_extensions function."""

    def test_filters_extensions_by_module(self) -> None:
        """Test that only extensions for available modules are returned."""
        from semantics.cli import get_available_extensions

        # Only audio module available
        available = get_available_extensions({"audio"})

        # Should have audio extensions
        assert ".wav" in available
        assert ".mp3" in available

        # Should NOT have video or document extensions
        assert ".mp4" not in available
        assert ".pdf" not in available

    def test_all_modules_returns_full_map(self) -> None:
        """Test that all modules returns the full extension map."""
        from semantics.cli import get_available_extensions, EXTENSION_MAP

        available = get_available_extensions({"audio", "video", "document"})

        # Should have same number of entries as EXTENSION_MAP
        assert len(available) == len(EXTENSION_MAP)
