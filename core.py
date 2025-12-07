"""Core logic for managing Roblox executor scripts.

This module does not perform any injection into Roblox; it simply tracks and
executes Lua scripts locally so users can organize their library before using
an external injector.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


def default_scripts_dir() -> Path:
    """Return the cross-platform default scripts directory.

    The folder lives under the user's home directory so the tool works on
    Windows, Android (e.g., Termux), iOS Python apps, and desktop platforms
    without requiring write access to the package installation path.
    """

    return Path.home() / ".ronix_executor" / "scripts"


@dataclass
class Script:
    """Represents a Roblox Lua script on disk."""

    name: str
    path: Path

    def load(self) -> str:
        """Return the contents of the script."""
        return self.path.read_text(encoding="utf-8")


class ScriptManager:
    """Manage a collection of Lua scripts for Roblox executors."""

    def __init__(self, scripts_dir: Path | str | None = None) -> None:
        # Default to a user-writable location for Windows, Android/Termux, iOS
        # Python environments, and POSIX systems.
        self.scripts_dir = Path(scripts_dir) if scripts_dir is not None else default_scripts_dir()
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

    def list_scripts(self) -> List[Script]:
        """Return all scripts available in the scripts directory."""
        scripts: Iterable[Path] = sorted(self.scripts_dir.glob("*.lua"))
        return [Script(path.stem, path) for path in scripts]

    def add_script(self, name: str, content: str) -> Script:
        """Create a new script with the provided name and content."""
        sanitized = name.replace(" ", "_")
        target = self.scripts_dir / f"{sanitized}.lua"
        target.write_text(content, encoding="utf-8")
        return Script(sanitized, target)

    def run_script(self, name: str) -> str:
        """Return the script contents to be executed by an external injector.

        This method does not interact with Roblox directly; instead it returns
        the script body so callers can pipe it into their preferred injector.
        """

        script = next((s for s in self.list_scripts() if s.name == name), None)
        if script is None:
            available = ", ".join(s.name for s in self.list_scripts()) or "none"
            raise FileNotFoundError(
                f"Script '{name}' not found. Available scripts: {available}"
            )
        return script.load()

    def ensure_default_scripts(self) -> List[Script]:
        """Create bundled scripts for popular games if missing.

        The goal is to ship placeholder Lua files for frequently requested games
        so users can immediately tailor them to their own injector setups.
        """

        defaults: dict[str, str] = {
            "hello_world": """-- Ronix sample script\nprint("Hello from Ronix executor!")\n""",
            "blox_fruits": """-- Blox Fruits helper\n-- Add your preferred Blox Fruits script below\nprint("Load your Blox Fruits routine here")\n""",
            "doors": """-- DOORS helper\n-- Insert your DOORS script or loot notifier here\nprint("Load your DOORS routine here")\n""",
            "pet_simulator": """-- Pet Simulator helper\n-- Customize with your favorite pet farming script\nprint("Load your Pet Simulator routine here")\n""",
            "brookhaven": """-- Brookhaven helper\n-- Drop in RP automation or quality-of-life scripts\nprint("Load your Brookhaven routine here")\n""",
            "grow_a_garden": """-- Grow a Garden helper\n-- Plant your automation or farming logic here\nprint("Load your Grow a Garden routine here")\n""",
            "rivals_99": """-- Rivals 99 helper\n-- Add combat, loot, or QoL tweaks for Rivals 99\nprint("Load your Rivals 99 routine here")\n""",
            "night_in_the_forest": """-- Night in the Forest helper\n-- Slot in survival or resource scripts for Night in the Forest\nprint("Load your Night in the Forest routine here")\n""",
        }

        created: List[Script] = []
        for name, content in defaults.items():
            target = self.scripts_dir / f"{name}.lua"
            if not target.exists():
                created.append(self.add_script(name, content))
        return created or self.list_scripts()
