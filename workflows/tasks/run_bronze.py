"""Workflow task: Bronze ingestion.

Calls existing entry point ``src/bronze/ingest_all.py`` → ``ingest_all()``.
Does not duplicate Bronze business logic.
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
    parser = build_overrides_parser("Databricks Workflow — Bronze ingest_all")
    args = parser.parse_args(argv)
    overrides = overrides_from_args(args)

    ingest_mod = SourceFileLoader(
        "ingest_all",
        str(_SRC / "bronze" / "ingest_all.py"),
    ).load_module()
    ingest_mod.ingest_all(overrides=overrides)


if __name__ == "__main__":
    main()
