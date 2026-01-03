"""CLI orchestrator for semantics.

This module handles argument parsing and orchestrates the execution
of various CLI modules based on user input.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="semantics",
        description="Semantic analysis CLI tool",
    )
    
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Input file path (e.g., video.mp4)",
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
    
    # Import modules dynamically to avoid loading unnecessary dependencies
    if args.transcribe:
        from semantics.modules import transcribe
        print(f"Executing transcribe module on: {args.input}")
        transcribe.execute(args.input)
    
    if args.objects:
        from semantics.modules import objects
        print(f"Executing objects module on: {args.input}")
        objects.execute(args.input)
    
    # If no module is specified, show help
    if not args.transcribe and not args.objects:
        parser.print_help()
        return 0
    
    return 0
