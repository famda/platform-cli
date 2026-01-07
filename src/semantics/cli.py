"""Main CLI entry point with ModuleRegistry for dynamic module discovery.

This module provides the main Click-based CLI with automatic module loading
from the modules/ directory. It also supports extension-based file routing.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click
from click_help_colors import HelpColorsGroup

if TYPE_CHECKING:
    from types import ModuleType


# Extension to module mapping for auto-routing
EXTENSION_MAP: dict[str, str] = {
    # Audio formats
    ".wav": "audio",
    ".mp3": "audio",
    ".flac": "audio",
    ".ogg": "audio",
    ".m4a": "audio",
    ".aac": "audio",
    ".wma": "audio",
    # Video formats
    ".mp4": "video",
    ".avi": "video",
    ".mkv": "video",
    ".mov": "video",
    ".wmv": "video",
    ".webm": "video",
    ".flv": "video",
    # Document formats
    ".pdf": "document",
    ".png": "document",
    ".jpg": "document",
    ".jpeg": "document",
    ".tiff": "document",
    ".bmp": "document",
    ".gif": "document",
}

# Video extensions that can be handled by audio module for transcription
# (audio track extraction from video files)
AUDIO_COMPATIBLE_VIDEO_EXTENSIONS: set[str] = {
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm", ".flv",
}

# Audio-only operations that can work on video files
AUDIO_COMPATIBLE_FLAGS: set[str] = {"--transcribe"}


def get_available_extensions(available_modules: set[str]) -> dict[str, str]:
    """Get extension map filtered to only available modules.

    Args:
        available_modules: Set of module names that are loaded

    Returns:
        Filtered extension map with only available module mappings
    """
    return {ext: mod for ext, mod in EXTENSION_MAP.items() if mod in available_modules}


def generate_dynamic_help(available_modules: set[str]) -> str:
    """Generate help text dynamically based on available modules.

    Args:
        available_modules: Set of module names that are loaded

    Returns:
        Dynamic help text with examples only for available modules
    """
    lines = [
        "Semantics CLI - Unified interface for media intelligence",
        "",
        "Extract meaning, not just metadata. Composable AI operations designed for developers scaling intelligent workflows",
        "",
        "Process files directly with auto-detection based on extension:",
    ]

    # Add examples based on available modules
    examples = []
    if "audio" in available_modules:
        examples.append("  semantics -i input.wav -o ./output --transcribe")
        examples.append("  semantics -i input.wav -o ./output --transcribe --extract-metadata")
    if "video" in available_modules:
        examples.append("  semantics -i input.mp4 -o ./output --transcribe")
    if "document" in available_modules:
        examples.append("  semantics -i document.pdf -o ./output --extract-text")

    if examples:
        lines.append("")
        lines.append("\b")  # Actual backslash-b for Click
        lines.append("Examples:")
        lines.extend(examples)

    lines.append("")
    lines.append("Or use explicit subcommands:")

    subcommand_examples = []
    if "audio" in available_modules:
        subcommand_examples.append("  semantics audio input.wav -o ./output --transcribe")
    if "video" in available_modules:
        subcommand_examples.append("  semantics video video.mp4 -o ./output --detect-objects")
    if "document" in available_modules:
        subcommand_examples.append("  semantics document document.pdf -o ./output --extract-text")

    if subcommand_examples:
        lines.append("")
        lines.append("\b")  # Actual backslash-b for Click
        lines.extend(subcommand_examples)

    lines.append("")
    lines.append("Use 'semantics <module> --help' to see available options for each module.")

    return "\n".join(lines)


class ModuleRegistry:
    """Dynamically loads modules from the modules/ directory.

    This registry discovers and loads CLI modules that follow the convention
    of having a cli.py file with a 'cli' Click command exported.
    """

    def __init__(self) -> None:
        """Initialize the registry with empty command storage."""
        self._commands: dict[str, click.Command] = {}
        self._failed: list[str] = []

    def register(self, name: str, cli_path: Path) -> None:
        """Load a single module's CLI from its cli.py file.

        Args:
            name: The module name (e.g., 'audio', 'video')
            cli_path: Path to the module's cli.py file
        """
        try:
            spec = importlib.util.spec_from_file_location(
                f"semantics.modules.{name}.cli", cli_path
            )
            if spec is None or spec.loader is None:
                self._failed.append(name)
                return

            module: ModuleType = importlib.util.module_from_spec(spec)
            sys.modules[f"semantics.modules.{name}.cli"] = module
            spec.loader.exec_module(module)

            # Get the 'cli' command from the module
            if hasattr(module, "cli"):
                self._commands[name] = module.cli
            else:
                self._failed.append(name)
        except Exception:
            self._failed.append(name)

    def load_all_modules(self) -> None:
        """Discover and load all modules from the modules/ directory.

        Scans the modules/ directory for subdirectories containing a cli.py file
        and attempts to load each one. Failed loads are silently recorded.
        """
        modules_dir = Path(__file__).parent / "modules"

        if not modules_dir.is_dir():
            return

        for module_path in modules_dir.iterdir():
            if module_path.is_dir():
                cli_file = module_path / "cli.py"
                if cli_file.exists():
                    self.register(module_path.name, cli_file)

    def get_unavailable_modules(self) -> list[str]:
        """Return list of modules that failed to load.

        Returns:
            List of module names that couldn't be loaded
        """
        return self._failed.copy()

    @property
    def commands(self) -> dict[str, click.Command]:
        """Return the loaded commands dictionary.

        Returns:
            Dictionary mapping module names to their Click commands
        """
        return self._commands


# Load modules first so we can use them in main
registry = ModuleRegistry()
registry.load_all_modules()


class AutoRoutingGroup(HelpColorsGroup):
    """Custom Click Group that supports auto-routing based on -i/--input option.

    When -i/--input is provided, this group bypasses normal subcommand resolution
    and routes directly to the appropriate module based on file extension.
    Inherits from HelpColorsGroup to provide colorized help output.
    """

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra,
    ) -> click.Context:
        """Create context, enabling extra args mode if -i is detected."""
        # Check if -i or --input appears before any subcommand
        has_input = False
        subcommand_names = set(self.list_commands(click.Context(self)))

        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ("-i", "--input"):
                has_input = True
                break
            if arg.startswith("-i=") or arg.startswith("--input="):
                has_input = True
                break
            # Skip options with values
            if arg in ("-o", "--output"):
                i += 2
                continue
            if arg.startswith("-"):
                i += 1
                continue
            # Positional arg - check if it's a subcommand
            if arg in subcommand_names:
                break
            i += 1

        if has_input:
            # Enable mode to accept unknown options as extra args
            extra["allow_extra_args"] = True
            extra["allow_interspersed_args"] = True
            extra["ignore_unknown_options"] = True
            # Store original args for later
            self._auto_routing_args = args.copy()

        return super().make_context(info_name, args, parent, **extra)

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str | None, click.Command | None, list[str]]:
        """Resolve subcommand, but skip if in auto-routing mode."""
        # Check if we stored auto-routing args
        if hasattr(self, "_auto_routing_args"):
            # In auto-routing mode - return remaining args as-is
            return None, None, args
        return super().resolve_command(ctx, args)

    def invoke(self, ctx: click.Context) -> None:
        """Invoke the command, handling auto-routing when -i is provided."""
        # If we have a subcommand, let Click handle it normally
        if ctx.invoked_subcommand is not None:
            return super().invoke(ctx)

        # Get the input value
        input_file = ctx.params.get("input")

        if input_file is None:
            # No input file and no subcommand - let the callback show help
            return super().invoke(ctx)

        # Auto-routing mode: validate and route to module
        output = ctx.params.get("output")
        if output is None:
            raise click.ClickException("--output / -o is required when processing a file")

        # Extract module flags from original args first (needed for fallback logic)
        original_args = getattr(self, "_auto_routing_args", [])
        module_flags = []
        skip_next = False
        for i, arg in enumerate(original_args):
            if skip_next:
                skip_next = False
                continue
            if arg in ("-i", "--input", "-o", "--output"):
                skip_next = True
                continue
            if arg.startswith(("-i=", "--input=", "-o=", "--output=")):
                continue
            module_flags.append(arg)

        # Detect module from extension
        input_path = Path(input_file)
        ext = input_path.suffix.lower()
        module_name = EXTENSION_MAP.get(ext)

        if module_name is None:
            available = list(registry.commands.keys())
            raise click.ClickException(
                f"Unsupported file extension: {ext}. "
                f"Available modules: {', '.join(available) if available else 'none'}"
            )

        # Check if module is available, with fallback logic
        if module_name not in registry.commands:
            # Check for audio fallback: video files can be processed by audio module
            # for transcription (audio track extraction)
            can_fallback_to_audio = (
                ext in AUDIO_COMPATIBLE_VIDEO_EXTENSIONS
                and "audio" in registry.commands
                and any(flag in AUDIO_COMPATIBLE_FLAGS for flag in module_flags)
            )

            if can_fallback_to_audio:
                module_name = "audio"
            else:
                # Build helpful error message
                available = list(registry.commands.keys())
                available_str = ", ".join(available) if available else "none"

                # Suggest alternative if possible
                suggestions = []
                if ext in AUDIO_COMPATIBLE_VIDEO_EXTENSIONS and "audio" in registry.commands:
                    suggestions.append(
                        f"For transcription, use: semantics audio {input_file} -o {output} --transcribe"
                    )

                error_msg = (
                    f"Module '{module_name}' is not available in this executable. "
                    f"Available modules: {available_str}."
                )
                if suggestions:
                    error_msg += "\n" + "\n".join(suggestions)

                raise click.ClickException(error_msg)

        module_args = [input_file, "-o", output] + module_flags

        # Clean up
        if hasattr(self, "_auto_routing_args"):
            del self._auto_routing_args

        # Invoke the module's CLI command directly
        module_cmd = registry.commands[module_name]

        # Create a new context for the module command and invoke it
        with module_cmd.make_context(module_name, module_args, parent=ctx) as sub_ctx:
            module_cmd.invoke(sub_ctx)


# Create the main CLI group with auto-routing support
# Generate dynamic help based on available modules
_dynamic_help = generate_dynamic_help(set(registry.commands.keys()))


@click.group(
    cls=AutoRoutingGroup,
    invoke_without_command=True,
    help=_dynamic_help,
    help_headers_color="yellow",
    help_options_color="green",
)
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, dir_okay=False),
    help="Input file to process (auto-detects module from extension)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False),
    help="Output folder for results",
)
@click.version_option(package_name="semantics")
@click.pass_context
def main(ctx: click.Context, input: str | None, output: str | None) -> None:
    """Main entry point for the semantics CLI."""
    # AutoRoutingGroup handles the logic in its invoke() method
    # This callback only runs when no subcommand and no -i is provided
    if ctx.invoked_subcommand is None and input is None:
        click.echo(ctx.get_help())


# Register all loaded modules as subcommands
for name, cmd in registry.commands.items():
    main.add_command(cmd, name)
