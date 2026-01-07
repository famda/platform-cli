#!/usr/bin/env python3
"""Build script for creating PyInstaller executables.

This script creates standalone executables for different module variants:
- semantics-audio: Audio processing only
- semantics-video: Video processing only
- semantics-document: Document processing only
- semantics: Full version with all modules

Usage:
    python build.py all       # Build all variants
    python build.py audio     # Build audio variant only
    python build.py video     # Build video variant only
    python build.py document  # Build document variant only
    python build.py full      # Build full variant only
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).parent
DIST_DIR = ROOT_DIR / "dist"
BUILD_DIR = ROOT_DIR / "build"

# Module configurations
VARIANTS = {
    "audio": {
        "modules": ["audio"],
        "hidden_imports": [
            "semantics.modules.audio",
            "semantics.modules.audio.cli",
        ],
    },
    "video": {
        "modules": ["video"],
        "hidden_imports": [
            "semantics.modules.video",
            "semantics.modules.video.cli",
        ],
    },
    "document": {
        "modules": ["document"],
        "hidden_imports": [
            "semantics.modules.document",
            "semantics.modules.document.cli",
        ],
    },
    "full": {
        "modules": ["audio", "video", "document"],
        "hidden_imports": [
            "semantics.modules.audio",
            "semantics.modules.audio.cli",
            "semantics.modules.video",
            "semantics.modules.video.cli",
            "semantics.modules.document",
            "semantics.modules.document.cli",
        ],
    },
}


def get_version() -> str:
    """Get the current version from the package."""
    try:
        from semantics import __version__
        return __version__
    except ImportError:
        return "dev"


def build_variant(name: str) -> bool:
    """Build a specific variant using PyInstaller.

    Args:
        name: The variant name ('audio', 'video', 'document', or 'full')

    Returns:
        True if build succeeded, False otherwise
    """
    if name not in VARIANTS:
        print(f"[ERROR] Unknown variant: {name}")
        return False

    config = VARIANTS[name]

    # Determine executable name (without version - CI adds it)
    if name == "full":
        exe_name = "semantics"
    else:
        exe_name = f"semantics-{name}"

    print(f"\n[BUILD] Building {exe_name}...")

    # Build PyInstaller command using uv to ensure correct environment
    cmd = [
        "uv",
        "run",
        "python",
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        exe_name,
        "--clean",
    ]

    # Add hidden imports
    for hidden in config["hidden_imports"]:
        cmd.extend(["--hidden-import", hidden])

    # Add data files for modules
    sep = ";" if sys.platform == "win32" else ":"
    for module in config["modules"]:
        module_path = ROOT_DIR / "src" / "semantics" / "modules" / module
        cmd.extend(["--add-data", f"{module_path}{sep}semantics/modules/{module}"])

    # Add the main entry point
    cmd.append(str(ROOT_DIR / "src" / "semantics" / "__main__.py"))

    try:
        subprocess.run(cmd, check=True)
        print(f"[OK] Built: {DIST_DIR / exe_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed for {name}: {e}")
        return False


def clean_build() -> None:
    """Clean build artifacts."""
    print("[CLEAN] Cleaning build artifacts...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    for spec_file in ROOT_DIR.glob("*.spec"):
        spec_file.unlink()


def main() -> int:
    """Main entry point for the build script."""
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    target = sys.argv[1].lower()

    if target == "all":
        success = True
        for variant in VARIANTS:
            if not build_variant(variant):
                success = False
        clean_build()
        return 0 if success else 1

    elif target == "clean":
        clean_build()
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        print("[OK] Cleaned all build artifacts")
        return 0

    elif target in VARIANTS:
        success = build_variant(target)
        clean_build()
        return 0 if success else 1

    else:
        print(f"[ERROR] Unknown target: {target}")
        print("Valid targets: all, clean, audio, video, document, full")
        return 1


if __name__ == "__main__":
    sys.exit(main())
