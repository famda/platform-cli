# Semantics CLI

Process different file types with specialized AI handlers. A modular, extensible CLI tool for audio, video, and document processing.

## Overview

`semantics` is a Python-based CLI tool that processes various file types using specialized handlers. It features a modular architecture with dynamic module discovery, allowing you to use only the functionality you need.

## Installation

### Option 1: Download Pre-built Executable (Recommended)

Download the appropriate executable for your needs from the [Releases page](https://github.com/famda/platform-cli/releases):

| Executable | Description |
|------------|-------------|
| `semantics-audio.exe` | Audio processing only |
| `semantics-video.exe` | Video processing only |
| `semantics-document.exe` | Document processing only |
| `semantics.exe` | Full version with all modules |

No Python installation required - executables are standalone.

### Option 2: Development Setup

**Prerequisites:**
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

**Setup:**

```bash
# Clone the repository
git clone https://github.com/famda/platform-cli.git
cd platform-cli

# Install core dependencies
uv sync

# Install with specific module dependencies
uv sync --extra audio
uv sync --extra video
uv sync --extra document

# Install all dependencies
uv sync --extra all

# Install development tools
uv sync --extra dev
```

## Usage

### Audio Processing

```bash
# Transcribe audio to text
semantics audio input.wav -o ./output --transcribe
semantics audio input.mp3 -o ./output --transcribe --language es --model large

# Extract audio metadata
semantics audio input.wav -o ./output --extract-metadata

# Chain multiple operations
semantics audio input.wav -o ./output --transcribe --extract-metadata
```

### Video Processing

```bash
# Transcribe video audio track
semantics video video.mp4 -o ./output --transcribe

# Detect objects in video
semantics video video.mp4 -o ./output --detect-objects
semantics video video.mp4 -o ./output --detect-objects --confidence 0.7

# Chain multiple operations
semantics video video.mp4 -o ./output --transcribe --detect-objects
```

### Document Processing

```bash
# Extract text from documents
semantics document document.pdf -o ./output --extract-text
semantics document scan.png -o ./output --extract-text --format json
```

### Getting Help

```bash
# Main help
semantics --help

# Module help
semantics audio --help
semantics video --help
semantics document --help
```

## Command Reference

### Audio Module

| Flag | Description | Additional Options |
|------|-------------|-------------------|
| `--transcribe` | Convert audio to text | `--language`, `--model` |
| `--extract-metadata` | Get audio file metadata | - |

### Video Module

| Flag | Description | Additional Options |
|------|-------------|-------------------|
| `--transcribe` | Transcribe video audio track | `--language`, `--model` |
| `--detect-objects` | Detect objects in frames | `--confidence`, `--model` |

### Document Module

| Flag | Description | Additional Options |
|------|-------------|-------------------|
| `--extract-text` | Extract text from PDF/images | `--format` (text/json) |

## Project Structure

```
platform-cli/
├── src/
│   └── semantics/          # Main package
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py          # Click-based CLI with ModuleRegistry
│       └── modules/        # Processing modules
│           ├── audio/
│           │   ├── __init__.py
│           │   └── cli.py  # Audio commands with chained flags
│           ├── video/
│           │   ├── __init__.py
│           │   └── cli.py  # Video commands with chained flags
│           └── document/
│               ├── __init__.py
│               └── cli.py  # Document commands with chained flags
├── tests/                  # Test suite
├── pyproject.toml          # Project configuration
├── build.py                # PyInstaller build script
└── README.md
```

## Development

### Running Tests

```bash
uv run pytest
uv run pytest --cov=semantics
```

### Adding New Modules

1. Create a new folder in `src/semantics/modules/` (e.g., `src/semantics/modules/image/`)
2. Add `__init__.py` and `cli.py` with a Click command named `cli`
3. Use chained flags for operations (e.g., `--resize`, `--compress`)
4. The module will be auto-discovered by `ModuleRegistry`

Example module structure:
```python
# src/semantics/modules/image/cli.py
import click
from pathlib import Path

@click.command()
@click.argument("input", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", type=click.Path(file_okay=False), required=True)
@click.option("--resize", is_flag=True, help="Resize the image")
@click.option("--compress", is_flag=True, help="Compress the image")
def cli(input: str, output: str, resize: bool, compress: bool):
    """Image processing - chain multiple operations."""
    if not resize and not compress:
        raise click.ClickException("At least one operation required")
    
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if resize:
        # Handle resize
        pass
    if compress:
        # Handle compress
        pass
```

### Building Executables

```bash
# Build all variants
python build.py all

# Build specific variant
python build.py audio
python build.py video
python build.py document
python build.py full

# Clean build artifacts
python build.py clean
```

## Architecture

- **Click-based CLI**: Modern command-line interface with chained flag operations
- **ModuleRegistry**: Dynamic module discovery from `src/semantics/modules/` directory
- **Lazy Loading**: Heavy dependencies imported only when needed
- **Chained Operations**: Multiple operations can be run in a single command
- **Graceful Degradation**: Clear error messages when modules unavailable

## CI/CD and Releases

- **Semantic Versioning**: Versions derived from git tags via `hatch-vcs`
- **Conventional Commits**: Automated versioning based on commit messages
- **GitHub Releases**: Multiple executable variants per release per platform
- **Cross-platform**: Builds for Windows, Linux, and macOS

Release artifact naming:
- `semantics-vX.Y.Z-linux-x86_64.zip`
- `semantics-audio-vX.Y.Z-windows-x86_64.zip`
- etc.

## License

<!-- Add your license information here -->

<!-- Add your license information here -->
