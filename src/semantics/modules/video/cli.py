"""Video module CLI - chain multiple operations together.

This module provides video processing commands that can be chained
to perform multiple operations in a single invocation.
"""

from __future__ import annotations

from pathlib import Path

import click
from click_help_colors import HelpColorsCommand

from semantics.modules.video.handlers import detect_objects, transcribe

_VIDEO_HELP = """\
Semantics Video CLI - Unified interface for media intelligence

Extract meaning, not just metadata. Composable AI operations designed for developers scaling intelligent workflows

\b
Examples:
  semantics video video.mp4 -o ./output --transcribe
  semantics video video.mp4 -o ./output --detect-objects
  semantics video video.mp4 -o ./output --transcribe --detect-objects
"""


@click.command(
    cls=HelpColorsCommand,
    help=_VIDEO_HELP,
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
@click.option("--transcribe", "do_transcribe", is_flag=True, help="Transcribe video audio to text")
@click.option("--detect-objects", "do_detect_objects", is_flag=True, help="Detect objects in video frames")
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
    help="Model size (default: base)",
)
@click.option(
    "--confidence",
    "-c",
    default=0.5,
    type=click.FloatRange(0.0, 1.0),
    help="Confidence threshold for object detection (default: 0.5)",
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
    do_detect_objects: bool,
    language: str,
    model: str,
    confidence: float,
    verbose: bool,
) -> None:
    if not do_transcribe and not do_detect_objects:
        raise click.ClickException(
            "At least one operation required: --transcribe or --detect-objects"
        )

    input_path = Path(input)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    if do_transcribe:
        transcribe.handle(
            input_path, output_path, verbose=verbose, language=language, model=model
        )

    if do_detect_objects:
        detect_objects.handle(
            input_path, output_path, verbose=verbose, model=model, confidence=confidence
        )

