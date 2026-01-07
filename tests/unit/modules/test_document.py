"""Tests for the document module commands with chained flags."""

import pytest
from click.testing import CliRunner

from semantics.cli import main


class TestDocumentModule:
    """Tests for the document module commands with chained flags."""

    def test_document_help(self, runner: CliRunner) -> None:
        """Test document subcommand help."""
        result = runner.invoke(main, ["document", "--help"])
        assert result.exit_code == 0
        assert "--extract-text" in result.output
        assert "--verbose" in result.output

    def test_document_requires_operation(self, runner: CliRunner, tmp_path) -> None:
        """Test that document requires at least one operation flag."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy")
        result = runner.invoke(main, ["document", str(input_file), "-o", str(tmp_path / "out")])
        assert result.exit_code != 0
        assert "At least one operation" in result.output

    def test_document_extract_text(self, runner: CliRunner, tmp_path) -> None:
        """Test document text extraction with --extract-text flag."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy pdf")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["document", str(input_file), "-o", str(output_dir), "--extract-text"],
        )
        assert result.exit_code == 0
        assert "Extracting text" in result.output
        assert "complete" in result.output.lower()

    def test_document_extract_text_json_format(self, runner: CliRunner, tmp_path) -> None:
        """Test text extraction with JSON output format."""
        input_file = tmp_path / "test.pdf"
        input_file.write_text("dummy pdf")
        output_dir = tmp_path / "output"

        result = runner.invoke(
            main,
            ["document", str(input_file), "-o", str(output_dir), "--extract-text", "-f", "json"],
        )
        assert result.exit_code == 0
        assert "Format: json" in result.output
