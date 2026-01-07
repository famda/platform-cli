"""Video handlers package.

This package contains handler modules for video processing operations.
Each handler module exports a `handle()` function as its entry point.
"""

from semantics.modules.video.handlers import detect_objects, transcribe

__all__ = ["transcribe", "detect_objects"]
