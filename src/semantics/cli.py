"""CLI orchestrator for semantics.

This module handles argument parsing and orchestrates the execution
of various CLI modules based on user input.
"""

import argparse
import sys


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="semantics",
        description="Semantic analysis CLI tool",
    )
    
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input file path (e.g., video.mp4, audio.mp3, document.pdf)",
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output folder path for results",
    )
    
    parser.add_argument(
        "--transcribe",
        action="store_true",
        help="Enable transcription module",
    )
    
    parser.add_argument(
        "--objects",
        action="store_true",
        help="Enable object detection module",
    )
    
    return parser


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate that at least one processing module is specified
    if not args.transcribe and not args.objects:
        parser.error("At least one processing module (--transcribe or --objects) must be specified")
        return 1
    
    # Import modules dynamically to avoid loading unnecessary dependencies
    if args.transcribe:
        from semantics.modules import transcribe
        print(f"Executing transcribe module on: {args.input}")
        print(f"Output will be saved to: {args.output}")
        transcribe.execute(args.input, args.output)
    
    if args.objects:
        from semantics.modules import objects
        print(f"Executing objects module on: {args.input}")
        print(f"Output will be saved to: {args.output}")
        objects.execute(args.input, args.output)
    
    return 0
