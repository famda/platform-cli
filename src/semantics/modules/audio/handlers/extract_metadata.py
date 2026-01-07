"""Audio metadata extraction handler."""

from pathlib import Path

import click


def handle(input_path: Path, output_path: Path, verbose: bool = False, **options) -> None:
    """
    Handle audio metadata extraction.

    Args:
        input_path: Path to the input audio file.
        output_path: Path to the output folder.
        verbose: Enable verbose output.
        **options: Additional options (unused for this handler).
    """
    if verbose:
        click.echo("[OPTIONS] Extracting metadata with verbose output")

    click.echo(f"[METADATA] Extracting metadata from: {input_path.name}")
    click.echo(f"   Output folder: {output_path}")

    # TODO: Implement actual metadata extraction with heavy dependencies
    # try:
    #     import mutagen
    #     audio = mutagen.File(str(input_path))
    #     metadata = dict(audio.tags) if audio.tags else {}
    # except ImportError:
    #     raise click.ClickException(
    #         'This feature requires additional dependencies. '
    #         'Run: uv pip install -e ".[audio]"'
    #     )

    click.echo("[OK] Metadata extraction complete (dummy)")
