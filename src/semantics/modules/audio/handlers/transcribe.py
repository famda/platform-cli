"""Audio transcription handler."""

from pathlib import Path

import click


def handle(input_path: Path, output_path: Path, verbose: bool = False, **options) -> None:
    """
    Handle audio transcription.

    Args:
        input_path: Path to the input audio file.
        output_path: Path to the output folder.
        verbose: Enable verbose output.
        **options: Additional options (language, model).
    """
    language = options.get("language", "en")
    model = options.get("model", "base")

    if verbose:
        click.echo(f"[OPTIONS] language={language}, model={model}")

    click.echo(f"[AUDIO] Transcribing audio: {input_path.name}")
    click.echo(f"   Output folder: {output_path}")

    # TODO: Implement actual transcription with heavy dependencies
    # try:
    #     import whisper
    #     model_obj = whisper.load_model(model)
    #     result = model_obj.transcribe(str(input_path))
    # except ImportError:
    #     raise click.ClickException(
    #         'This feature requires additional dependencies. '
    #         'Run: uv pip install -e ".[audio]"'
    #     )

    click.echo("[OK] Transcription complete (dummy)")
