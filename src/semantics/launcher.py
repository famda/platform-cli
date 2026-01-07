#!/usr/bin/env python3
"""Lightweight launcher for unified semantics CLI experience.

This module provides a unified entry point that discovers and delegates to
installed module executables. When users install individual modules (audio,
video, document), this launcher allows them to use a single `semantics`
command that routes to the appropriate module.

Architecture Note:
-----------------
This launcher is different from cli.py because:
- cli.py: Modules are bundled INSIDE the executable (used by semantics-full, semantics-audio, etc.)
- launcher.py: Modules are SEPARATE executables that need subprocess delegation

When a user installs only the audio module, they get:
  ~/.semantics/bin/semantics       <- This launcher
  ~/.semantics/bin/semantics-audio <- The actual audio module

The launcher discovers semantics-* executables and delegates to them.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup


def get_install_dir() -> Path:
    """Get the directory where semantics executables are installed.

    Returns:
        Path to the installation directory containing module executables.
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle - executable is in install dir
        return Path(sys.executable).parent
    # Running from source - shouldn't happen in production
    return Path(__file__).parent


def discover_modules() -> dict[str, Path]:
    """Find installed module executables in the installation directory.

    Scans the installation directory for executables matching the pattern
    'semantics-{module}' (or 'semantics-{module}.exe' on Windows).

    Returns:
        Dictionary mapping module names to their executable paths.
    """
    install_dir = get_install_dir()
    modules: dict[str, Path] = {}

    # Determine executable extension based on platform
    exe_suffix = ".exe" if sys.platform == "win32" else ""

    # Look for semantics-{module} executables
    for item in install_dir.iterdir():
        if not item.is_file():
            continue

        name = item.name
        # Skip the launcher itself
        if name == f"semantics{exe_suffix}":
            continue

        # Match semantics-{module} pattern
        prefix = "semantics-"
        if name.startswith(prefix):
            # Extract module name, removing .exe suffix if present
            module_name = name[len(prefix) :]
            if exe_suffix and module_name.endswith(exe_suffix):
                module_name = module_name[: -len(exe_suffix)]
            if module_name:
                modules[module_name] = item

    return modules


def get_version() -> str:
    """Get the launcher version."""
    try:
        from semantics import __version__
        return __version__
    except ImportError:
        return "unknown"


# Discover modules at import time for help generation
_discovered_modules = discover_modules()


def generate_help_text() -> str:
    """Generate dynamic help text based on discovered modules."""
    lines = [
        "Semantics CLI - Unified interface for media intelligence",
        "",
        "Extract meaning, not just metadata. Composable AI operations designed for developers scaling intelligent workflows",
        "",
        "Process files directly with auto-detection based on extension:",
    ]

    if _discovered_modules:
        lines.append("")
        lines.append("Examples:")
        if "audio" in _discovered_modules:
            lines.append("  semantics audio input.wav -o ./output --transcribe")
        if "video" in _discovered_modules:
            lines.append("  semantics video video.mp4 -o ./output --detect-objects")
        if "document" in _discovered_modules:
            lines.append("  semantics document scan.pdf -o ./output --extract-text")
        if "full" in _discovered_modules:
            lines.append("  semantics -i input.wav -o ./output --transcribe")
    else:
        lines.append("")
        lines.append("No modules installed.")

    lines.append("")
    lines.append("Run 'semantics <module> --help' for module-specific options.")

    return "\n".join(lines)


class LauncherGroup(HelpColorsGroup):
    """Custom group that delegates unknown commands to module executables."""

    def list_commands(self, ctx: click.Context) -> list[str]:
        """List available module commands."""
        return sorted(_discovered_modules.keys())

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Get a command that delegates to the module executable."""
        if cmd_name not in _discovered_modules:
            return None

        exe_path = _discovered_modules[cmd_name]

        @click.command(
            cls=HelpColorsCommand,
            name=cmd_name,
            context_settings={"allow_extra_args": True, "allow_interspersed_args": True},
            help=f"Delegate to {cmd_name} module executable.",
            help_headers_color="yellow",
            help_options_color="green",
        )
        @click.pass_context
        def delegate_command(ctx: click.Context) -> None:
            """Delegate to the module executable."""
            try:
                result = subprocess.run([str(exe_path)] + ctx.args)
                ctx.exit(result.returncode)
            except FileNotFoundError:
                raise click.ClickException(f"Could not execute module '{cmd_name}'.")
            except KeyboardInterrupt:
                ctx.exit(130)

        return delegate_command


@click.group(
    cls=LauncherGroup,
    invoke_without_command=True,
    help=generate_help_text(),
    help_headers_color="yellow",
    help_options_color="green",
)
@click.version_option(version=get_version(), prog_name="semantics launcher")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Unified launcher for semantics CLI modules."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


if __name__ == "__main__":
    sys.exit(main())
