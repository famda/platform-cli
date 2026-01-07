"""Document handlers package.

This package contains handler modules for document processing operations.
Each handler module exports a `handle()` function as its entry point.
"""

from semantics.modules.document.handlers import extract_text

__all__ = ["extract_text"]
