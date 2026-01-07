"""Audio handlers package.

This package contains handler modules for audio processing operations.
Each handler module exports a `handle()` function as its entry point.
"""

from semantics.modules.audio.handlers import extract_metadata, transcribe

__all__ = ["transcribe", "extract_metadata"]
