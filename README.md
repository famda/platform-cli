# platform-cli

A semantic analysis CLI tool for processing multiple file types including audio, documents, video, 3D models, and images.

## Overview

`semantics` is a Python-based CLI tool designed for semantic analysis of media files. It provides a modular architecture where different analysis modules can be executed independently or combined.

## Installation

### Option 1: Download Pre-built Release (Recommended for Users)

Download the latest release for your operating system from the [Releases page](https://github.com/famda/platform-cli/releases):

- **Linux**: `semantics-vX.Y.Z-linux-x86_64.zip`
- **Windows**: `semantics-vX.Y.Z-windows-x86_64.zip`
- **macOS**: `semantics-vX.Y.Z-macos-x86_64.zip`

**Prerequisites for pre-built releases:**
- Python 3.12 or higher must be installed on your system

**Usage:**
1. Download the ZIP file for your OS
2. Extract the archive
3. Run the CLI:
   - **Linux/macOS**: `./semantics --help`
   - **Windows**: `semantics.bat --help`

### Option 2: Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

**Prerequisites:**
- Python 3.12 or higher
- uv (install with `pip install uv`)

**Setup:**

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
uv run semantics --help

# Process a video file with transcription
uv run semantics -i video.mp4 -o ./output --transcribe

# Process an audio file with transcription
uv run semantics -i audio.mp3 -o ./results --transcribe

# Process an image file with object detection
uv run semantics -i image.jpg -o ./output --objects

# Process a video file with multiple modules
uv run semantics -i video.mp4 -o ./results --transcribe --objects

# Using short options
uv run semantics -i document.pdf -o /tmp/output --transcribe
```

**Required Arguments:**
- `-i, --input`: Input file path (supports video, audio, images, documents, 3D models)
- `-o, --output`: Output folder path where results will be saved

**Processing Modules** (at least one required):
- `--transcribe`: Enable transcription module
- `--objects`: Enable object detection module

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

## CI/CD and Releases

This project uses GitHub Actions for continuous integration and automated releases.

### Continuous Integration

Every pull request and push to `main` triggers CI checks:
- Tests run across Python 3.12, 3.13, and 3.14
- Tests run on Linux, Windows, and macOS
- Package build verification

### Automated Releases

Releases are automatically created when changes are merged to `main`:
- Version numbers follow **Semantic Versioning** (MAJOR.MINOR.PATCH)
- Versions are determined automatically from commit messages using **Conventional Commits**
- GitHub Releases include auto-generated release notes grouped by change type
- Each release includes downloadable ZIP artifacts for Linux, Windows, and macOS

### Release Artifacts

Each release provides self-contained bundles:
- **Linux**: Includes bash launcher script (`./semantics`)
- **Windows**: Includes batch launcher script (`semantics.bat`)
- **macOS**: Includes bash launcher script (`./semantics`)

All bundles include:
- The semantics CLI tool
- A Python virtual environment with all dependencies
- Platform-specific launcher script
- README with usage instructions

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Commit message conventions (Conventional Commits)
- Pull request process
- Code style guidelines

## License

<!-- Add your license information here -->