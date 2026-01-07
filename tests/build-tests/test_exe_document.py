"""Tests for document processing functionality in built executables."""

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
class TestDocumentExecution:
    """Test document processing functionality in built executables."""

    def test_document_exe_extract_text(self, document_exe: Path, tmp_path: Path) -> None:
        """Test document text extraction works in document executable."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document content")
        output_dir = tmp_path / "output"

        result = run_executable(
            document_exe, ["document", str(input_file), "-o", str(output_dir), "--extract-text"]
        )
        assert result.returncode == 0
        assert "Extracting" in result.stdout or "extract" in result.stdout.lower()

    def test_document_exe_extract_text_json_format(self, document_exe: Path, tmp_path: Path) -> None:
        """Test document text extraction with JSON format."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document content")
        output_dir = tmp_path / "output"

        result = run_executable(
            document_exe,
            ["document", str(input_file), "-o", str(output_dir), "--extract-text", "-f", "json"],
        )
        assert result.returncode == 0

    def test_document_exe_verbose(self, document_exe: Path, tmp_path: Path) -> None:
        """Test verbose flag works in document executable."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy document content")
        output_dir = tmp_path / "output"

        result = run_executable(
            document_exe,
            ["document", str(input_file), "-o", str(output_dir), "--extract-text", "-v"],
        )
        assert result.returncode == 0
