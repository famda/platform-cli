"""Document module CLI - chain multiple operations together.

This module provides document processing commands that can be chained
to perform multiple operations in a single invocation.
"""

from __future__ import annotations

from pathlib import Path

import click
from click_help_colors import HelpColorsCommand

from semantics.modules.document.handlers import extract_text

_DOCUMENT_HELP = """\
Semantics Documents CLI - Unified interface for media intelligence

Extract meaning, not just metadata. Composable AI operations designed for developers scaling intelligent workflows

\b
Examples:
  semantics document document.pdf -o ./output --extract-text
  semantics document scan.png -o ./output --extract-text --format json
"""


@click.command(
    cls=HelpColorsCommand,
    help=_DOCUMENT_HELP,
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
@click.option("--extract-text", "do_extract_text", is_flag=True, help="Extract text from document")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="text",
    type=click.Choice(["text", "json"]),
    help="Output format (default: text)",
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
    do_extract_text: bool,
    output_format: str,
    verbose: bool,
) -> None:
    if not do_extract_text:
        raise click.ClickException("At least one operation required: --extract-text")

    input_path = Path(input)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    if do_extract_text:
        extract_text.handle(input_path, output_path, verbose=verbose, format=output_format)

