# Contributing to Semantics CLI

Thank you for your interest in contributing to the Semantics CLI project!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/famda/platform-cli.git
   cd platform-cli
   ```

2. **Install dependencies with uv:**
   ```bash
   # Install uv if you haven't already
   pip install uv
   
   # Install project dependencies
   uv sync --extra dev
   ```

3. **Run tests:**
   ```bash
   uv run pytest
   ```

## Commit Message Convention

This project uses **Conventional Commits** for commit messages. This enables automated versioning and changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature (triggers a MINOR version bump, e.g., 1.0.0 → 1.1.0)
- **fix**: A bug fix (triggers a PATCH version bump, e.g., 1.0.0 → 1.0.1)
- **perf**: A performance improvement (triggers a PATCH version bump)
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (formatting, whitespace, etc.)
- **refactor**: Code changes that neither fix bugs nor add features
- **test**: Adding or updating tests
- **build**: Changes to build system or dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files

### Breaking Changes

To indicate a breaking change (triggers a MAJOR version bump, e.g., 1.0.0 → 2.0.0):

1. Add `!` after the type: `feat!: change API`
2. Or include `BREAKING CHANGE:` in the footer:
   ```
   feat: add new parameter
   
   BREAKING CHANGE: The old parameter name is no longer supported
   ```

### Examples

**Feature (MINOR bump):**
```
feat: add object detection module for video files
```

**Bug fix (PATCH bump):**
```
fix: handle empty subtitle tracks correctly
```

**Performance improvement (PATCH bump):**
```
perf: optimize video frame processing
```

**Breaking change (MAJOR bump):**
```
feat!: change default output directory structure

BREAKING CHANGE: Output files are now organized by module type
```

**With scope:**
```
fix(cli): validate input file path before processing
```

**With body and footer:**
```
feat: add support for PDF transcription

This adds a new module for extracting text from PDF files
using the pypdf library.

Closes #42
```

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** and commit them using the Conventional Commits format.

3. **Run tests** to ensure everything works:
   ```bash
   uv run pytest
   ```

4. **Push your branch** and create a Pull Request to `main`.

5. **CI will run automatically** on your PR:
   - Tests across multiple Python versions (3.12, 3.13, 3.14)
   - Tests on multiple OS platforms (Linux, Windows, macOS)
   - Package build verification

6. Once approved and merged to `main`, the release workflow will:
   - Automatically determine the next version based on your commit messages
   - Create a GitHub Release with auto-generated release notes
   - Build and attach downloadable ZIP artifacts for each OS

## Code Style

- Follow existing code patterns in the repository
- Keep modules independent and testable
- Add tests for new features or bug fixes
- Update documentation when adding new features

## Questions?

Feel free to open an issue if you have questions about contributing!
