"""Command-line interface for the Ronix executor helper.

The CLI focuses on organizing Lua scripts locally so they can be fed into any
Roblox injector. It intentionally avoids performing injection itself.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import ScriptManager, default_scripts_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Roblox Lua scripts")
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=default_scripts_dir(),
        help="Folder to store and read Lua scripts",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available Lua scripts")

    add_parser = subparsers.add_parser("add", help="Create a new Lua script")
    add_parser.add_argument("name", help="Name of the Lua script (without extension)")
    add_parser.add_argument(
        "--content",
        help="Lua source code. If omitted, content is read from stdin.",
    )

    run_parser = subparsers.add_parser(
        "run", help="Print the contents of a Lua script for injection"
    )
    run_parser.add_argument("name", help="Name of the Lua script to print")

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    manager = ScriptManager(args.scripts_dir)
    manager.ensure_default_scripts()

    if args.command == "list":
        scripts = manager.list_scripts()
        for script in scripts:
            print(f"- {script.name} ({script.path})")
        return 0

    if args.command == "add":
        content = args.content if args.content is not None else sys.stdin.read()
        script = manager.add_script(args.name, content)
        print(f"Created script at {script.path}")
        return 0

    if args.command == "run":
        print(manager.run_script(args.name))
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
