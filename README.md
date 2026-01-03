# platform-cli

A semantic analysis CLI tool for video processing.

## Overview

`semantics` is a Python-based CLI tool designed for semantic analysis of media files. It provides a modular architecture where different analysis modules can be executed independently or combined.

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Prerequisites

- Python 3.12 or higher
- uv (install with `pip install uv`)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/famda/platform-cli.git
   cd platform-cli
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Install development dependencies:
   ```bash
   uv sync --extra dev
   ```

## Usage

Run the CLI using `uv`:

```bash
# Show help
uv run semantics

# Process a video file with transcription
uv run semantics -i video.mp4 --transcribe

# Process a video file with object detection
uv run semantics -i video.mp4 --objects

# Process a video file with multiple modules
uv run semantics -i video.mp4 --transcribe --objects
```

## Project Structure

```
platform-cli/
├── src/
│   └── semantics/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point for -m execution
│       ├── cli.py              # CLI orchestrator with argument parsing
│       └── modules/            # Functional modules
│           ├── __init__.py
│           ├── transcribe.py   # Transcription module
│           └── objects.py      # Object detection module
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_transcribe.py
│   └── test_objects.py
├── pyproject.toml              # Project configuration
└── README.md
```

## Development

### Running Tests

Run the test suite with pytest:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=semantics
```

### Adding New Modules

To add a new analysis module:

1. Create a new file in `src/semantics/modules/` (e.g., `sentiment.py`)
2. Implement an `execute(input_file)` function
3. Add the module to `src/semantics/modules/__init__.py`
4. Add command-line arguments in `src/semantics/cli.py`
5. Add tests in `tests/`

## Architecture

The CLI follows a modular architecture:

- **CLI Orchestrator** (`cli.py`): Handles argument parsing and module orchestration
- **Modules** (`modules/`): Independent functional modules that can be imported and executed
- **Entry Point** (`__main__.py`): Minimal entry point that delegates to the orchestrator

This design keeps the main script simple while allowing modules to be complex and feature-rich.

## License

<!-- Add your license information here -->