"""Workflow task: Silver validation / transformation.

Calls existing entry point ``src/silver/create_silver_tables.py`` → ``create_silver_tables()``.
Does not duplicate Silver quality logic.
"""

from __future__ import annotations

import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

_TASKS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TASKS_DIR.parents[1]
_SRC = _REPO_ROOT / "src"
sys.path.insert(0, str(_SRC))
sys.path.insert(0, str(_TASKS_DIR))

from _params import build_overrides_parser, overrides_from_args  # noqa: E402


def main(argv: list[str] | None = None) -> None:
    parser = build_overrides_parser("Databricks Workflow — Silver create_silver_tables")
    args = parser.parse_args(argv)
    overrides = overrides_from_args(args)

    silver_mod = SourceFileLoader(
        "create_silver_tables",
        str(_SRC / "silver" / "create_silver_tables.py"),
    ).load_module()
    silver_mod.create_silver_tables(overrides=overrides)


if __name__ == "__main__":
    main()
