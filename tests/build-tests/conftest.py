"""Build-specific test fixtures for PyInstaller executable tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.parent
DIST_DIR = ROOT_DIR / "dist"


def get_executable_path(variant: str) -> Path:
    """Get the platform-aware path for an executable variant.

    Args:
        variant: The variant name ('launcher', 'full', 'audio', 'video', 'document')

    Returns:
        Path to the executable with platform-appropriate extension.
    """
    if variant == "launcher":
        exe_name = "semantics"
    elif variant == "full":
        exe_name = "semantics-full"
    else:
        exe_name = f"semantics-{variant}"

    if sys.platform == "win32":
        exe_name += ".exe"

    return DIST_DIR / exe_name


def run_executable(exe_path: Path, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run an executable with the given arguments.

    Args:
        exe_path: Path to the executable.
        args: Command-line arguments to pass.
        timeout: Maximum execution time in seconds.

    Returns:
        CompletedProcess with stdout, stderr, and returncode.
    """
    return subprocess.run(
        [str(exe_path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


@pytest.fixture(scope="session")
def build_all_executables() -> Generator[Path, None, None]:
    """Build all executable variants once per test session.

    This fixture runs `python build.py all` and yields the dist directory.
    If executables already exist, it skips rebuilding.

    Yields:
        Path to the dist directory containing built executables.
    """
    # Check if all executables already exist
    all_variants = ["launcher", "full", "audio", "video", "document"]
    all_exist = all(get_executable_path(v).exists() for v in all_variants)

    if not all_exist:
        print("\n[BUILD] Building all executable variants...")
        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "build.py"), "all"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 10 minute timeout for full build
            cwd=str(ROOT_DIR),
        )
        if result.returncode != 0:
            pytest.fail(f"Build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}")

    # Verify executables exist
    for variant in all_variants:
        exe_path = get_executable_path(variant)
        if not exe_path.exists():
            pytest.skip(f"Executable not built: {exe_path}")

    yield DIST_DIR


@pytest.fixture
def launcher_exe(build_all_executables: Path) -> Path:
    """Get path to the launcher executable."""
    return get_executable_path("launcher")


@pytest.fixture
def full_exe(build_all_executables: Path) -> Path:
    """Get path to the full semantics-full executable."""
    return get_executable_path("full")


@pytest.fixture
def audio_exe(build_all_executables: Path) -> Path:
    """Get path to the audio-only executable."""
    return get_executable_path("audio")


@pytest.fixture
def video_exe(build_all_executables: Path) -> Path:
    """Get path to the video-only executable."""
    return get_executable_path("video")


@pytest.fixture
def document_exe(build_all_executables: Path) -> Path:
    """Get path to the document-only executable."""
    return get_executable_path("document")
