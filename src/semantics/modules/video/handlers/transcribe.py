"""Video transcription handler."""

from pathlib import Path

import click


def handle(input_path: Path, output_path: Path, verbose: bool = False, **options) -> None:
    """
    Handle video audio transcription.

    Args:
        input_path: Path to the input video file.
        output_path: Path to the output folder.
        verbose: Enable verbose output.
        **options: Additional options (language, model).
    """
    language = options.get("language", "en")
    model = options.get("model", "base")

    if verbose:
        click.echo(f"[OPTIONS] language={language}, model={model}")

    click.echo(f"[VIDEO] Transcribing video audio: {input_path.name}")
    click.echo(f"   Output folder: {output_path}")

    # TODO: Implement actual transcription with heavy dependencies
    # try:
    #     import whisper
    #     model_obj = whisper.load_model(model)
    #     result = model_obj.transcribe(str(input_path))
    # except ImportError:
    #     raise click.ClickException(
    #         'This feature requires additional dependencies. '
    #         'Run: uv pip install -e ".[video]"'
    #     )

    click.echo("[OK] Video transcription complete (dummy)")
