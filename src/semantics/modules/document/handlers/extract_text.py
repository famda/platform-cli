"""Document text extraction handler."""

from pathlib import Path

import click


def handle(input_path: Path, output_path: Path, verbose: bool = False, **options) -> None:
    """
    Handle document text extraction.

    Args:
        input_path: Path to the input document file.
        output_path: Path to the output folder.
        verbose: Enable verbose output.
        **options: Additional options (format).
    """
    output_format = options.get("format", "text")

    if verbose:
        click.echo(f"[OPTIONS] format={output_format}")

    click.echo(f"[DOCUMENT] Extracting text from document: {input_path.name}")
    click.echo(f"   Output folder: {output_path}")
    click.echo(f"   Format: {output_format}")

    # TODO: Implement actual text extraction with heavy dependencies
    # try:
    #     import pytesseract
    #     from pdf2image import convert_from_path
    #     # Process based on file type
    # except ImportError:
    #     raise click.ClickException(
    #         'This feature requires additional dependencies. '
    #         'Run: uv pip install -e ".[document]"'
    #     )

    click.echo("[OK] Text extraction complete (dummy)")
