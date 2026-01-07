"""Video object detection handler."""

from pathlib import Path

import click


def handle(input_path: Path, output_path: Path, verbose: bool = False, **options) -> None:
    """
    Handle video object detection.

    Args:
        input_path: Path to the input video file.
        output_path: Path to the output folder.
        verbose: Enable verbose output.
        **options: Additional options (model, confidence).
    """
    model = options.get("model", "yolov8n")
    confidence = options.get("confidence", 0.5)

    if verbose:
        click.echo(f"[OPTIONS] model={model}, confidence={confidence}")

    click.echo(f"[DETECT] Detecting objects in video: {input_path.name}")
    click.echo(f"   Output folder: {output_path}")

    # TODO: Implement actual object detection with heavy dependencies
    # try:
    #     from ultralytics import YOLO
    #     model_obj = YOLO(model)
    #     results = model_obj(str(input_path), conf=confidence)
    # except ImportError:
    #     raise click.ClickException(
    #         'This feature requires additional dependencies. '
    #         'Run: uv pip install -e ".[video]"'
    #     )

    click.echo("[OK] Object detection complete (dummy)")
