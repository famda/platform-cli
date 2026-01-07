"""Audio module CLI - chain multiple operations together.

This module provides audio processing commands that can be chained
to perform multiple operations in a single invocation.
"""

from __future__ import annotations

from pathlib import Path

import click
from click_help_colors import HelpColorsCommand

from semantics.modules.audio.handlers import extract_metadata, transcribe

_AUDIO_HELP = """\
Semantics Audio CLI - Unified interface for media intelligence

Extract meaning, not just metadata. Composable AI operations designed for developers scaling intelligent workflows

\b
Examples:
  semantics audio input.wav -o ./output --transcribe
  semantics audio input.wav -o ./output --transcribe --extract-metadata
  semantics audio input.wav -o ./output --extract-metadata --transcribe
"""


@click.command(
    cls=HelpColorsCommand,
    help=_AUDIO_HELP,
    help_headers_color="yellow",
    help_options_color="green",
)
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False),
    required=True,
    help="Output folder for results",
)
@click.option("--transcribe", "do_transcribe", is_flag=True, help="Transcribe audio to text")
@click.option("--extract-metadata", "do_extract_metadata", is_flag=True, help="Extract audio metadata")
@click.option(
    "--language",
    "-l",
    default="en",
    help="Language code for transcription (default: en)",
)
@click.option(
    "--model",
    "-m",
    default="base",
    type=click.Choice(["tiny", "base", "small", "medium", "large"]),
    help="Model size for transcription (default: base)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def cli(
    input: str,
    output: str,
    do_transcribe: bool,
    do_extract_metadata: bool,
    language: str,
    model: str,
    verbose: bool,
) -> None:
    if not do_transcribe and not do_extract_metadata:
        raise click.ClickException(
            "At least one operation required: --transcribe or --extract-metadata"
        )

    input_path = Path(input)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    if do_transcribe:
        transcribe.handle(
            input_path, output_path, verbose=verbose, language=language, model=model
        )

    if do_extract_metadata:
        extract_metadata.handle(input_path, output_path, verbose=verbose)

