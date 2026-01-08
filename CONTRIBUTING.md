# Contributing to Semantics CLI

Thank you for your interest in contributing to Semantics CLI! This guide covers development setup, architecture, and how to extend the project.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Getting Started

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
│           │   ├── cli.py  # Audio commands with chained flags
│           │   └── handlers/
│           │       ├── transcribe.py
│           │       └── extract_metadata.py
│           ├── video/
│           │   ├── __init__.py
│           │   ├── cli.py  # Video commands with chained flags
│           │   └── handlers/
│           │       ├── transcribe.py
│           │       └── detect_objects.py
│           └── document/
│               ├── __init__.py
│               ├── cli.py  # Document commands with chained flags
│               └── handlers/
│                   └── extract_text.py
├── tests/                  # Test suite
├── pyproject.toml          # Project configuration
├── build.py                # PyInstaller build script
└── README.md
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=semantics

# Run specific test file
uv run pytest tests/unit/test_cli_main.py -v
```

## Adding New Modules

1. Create a new folder in `src/semantics/modules/` (e.g., `src/semantics/modules/image/`)
2. Add `__init__.py` and `cli.py` with a Click command named `cli`
3. Add a `handlers/` folder with handler scripts
4. Use chained flags for operations (e.g., `--resize`, `--compress`)
5. The module will be auto-discovered by `ModuleRegistry`

### Example Module Structure

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

### Handler Pattern

Each operation flag has a corresponding handler script:

```python
# src/semantics/modules/image/handlers/resize.py
from pathlib import Path
import click

def handle(input_path: Path, output_path: Path, verbose: bool = False, **options) -> None:
    """Handle image resizing."""
    if verbose:
        click.echo(f"🔧 Resizing: {input_path.name}")
    
    # Import heavy dependencies inside the function (lazy loading)
    # from PIL import Image
    # ...
    
    click.echo("✅ Resize complete")
```

## Building Executables

The project uses PyInstaller to create standalone executables.

```bash
# Build all variants
python build.py all

# Build specific variant
python build.py launcher
python build.py audio
python build.py video
python build.py document

# Clean build artifacts
python build.py clean
```

### Executable Variants

| Variant | Command | Includes |
|---------|---------|----------|
| Launcher | `python build.py launcher` | Entry point that discovers module executables |
| Audio | `python build.py audio` | Audio module only |
| Video | `python build.py video` | Video module only |
| Document | `python build.py document` | Document module only |

## Architecture

### Core Components

- **Click-based CLI**: Modern command-line interface with chained flag operations
- **ModuleRegistry**: Dynamic module discovery from `src/semantics/modules/` directory
- **Lazy Loading**: Heavy dependencies imported only when needed in handlers
- **Chained Operations**: Multiple operations can be run in a single command
- **Graceful Degradation**: Clear error messages when modules unavailable

### Key Design Decisions

1. **Chained Flags vs Subcommands**: Operations are flags (`--transcribe`) not subcommands, enabling `semantics audio file.wav --transcribe --extract-metadata`

2. **Handler Isolation**: Each operation is a separate handler file with a `handle()` function

3. **Lazy Imports**: Heavy dependencies (whisper, opencv, etc.) are imported inside handler functions, not at module level

4. **Auto-Discovery**: New modules are automatically discovered without manual registration

## CI/CD and Releases

### Workflows

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | Run tests on PR/push, trigger builds |
| `build.yml` | Reusable workflow for PyInstaller builds |
| `dev-build.yml` | Rolling dev prerelease on main push |
| `pr-build.yml` | PR preview builds with install comments |
| `release.yml` | Semantic release with artifacts |
| `test-install.yml` | Validate install script syntax |

### Versioning

- **Semantic Versioning**: Versions derived from git tags via `hatch-vcs`
- **Conventional Commits**: Automated versioning based on commit messages
- **Release Artifacts**: Multiple executable variants per release per platform

### Release Naming

```
semantics-vX.Y.Z-linux-x86_64.zip
semantics-audio-vX.Y.Z-windows-x86_64.zip
semantics-video-vX.Y.Z-macos-arm64.zip
```

## Code Style

- **Formatter**: Black
- **Linter**: Ruff
- **Type Hints**: Required for function signatures
- **Docstrings**: Required for public functions and classes

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/
```

## Dependency Management

### Single Lock File Strategy

This project uses a **single `pyproject.toml` at the root** with optional dependencies per module. All dependencies are locked in the root `uv.lock` file.

```toml
# pyproject.toml structure
[project.optional-dependencies]
audio = ["openai-whisper", "librosa"]      # Audio module deps
video = ["ultralytics", "opencv-python"]   # Video module deps
document = ["pdf2image", "pytesseract"]    # Document module deps
all = ["semantics[audio,video,document]"]  # All modules
dev = ["pytest", "black", "ruff", ...]     # Development tools
```

### Adding New Dependencies

1. Add the dependency to the appropriate optional-dependencies group in `pyproject.toml`
2. Regenerate the lock file: `uv lock`
3. Install locally: `uv sync --extra <module>`
4. Commit both `pyproject.toml` and `uv.lock`

### Module Isolation

Each module variant is built with only its own dependencies:

- **CI builds** use `uv sync --extra dev --extra <module>` per variant
- **Launcher** uses `uv sync --extra dev --extra all` for validation
- **PyInstaller** bundles only the resolved dependencies for that variant

This ensures:
- Module executables are smaller (no unused dependencies)
- Future dependency conflicts are isolated per module
- Users download only what they need

### Shared Utilities (core/)

The `src/semantics/core/` folder contains shared utilities used by all modules:

- `path.py` - Path and file handling utilities
- Future: logging, configuration, common helpers

Core utilities should have minimal dependencies (ideally only stdlib + click).

## Pull Request Guidelines

1. Create a feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass: `uv run pytest`
4. Follow conventional commit messages
5. Update documentation if needed

## License

This project is licensed under the MIT License.
