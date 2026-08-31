"""Shared configuration and path helpers for Databricks Medallion pipeline.

Paths are config-driven. Prefer Unity Catalog Volume paths for raw CSVs, e.g.:
  /Volumes/<catalog>/<schema>/<volume>/raw_data

Do not hard-code local Windows filesystem paths, /FileStore, /dbfs, DBFS mounts,
or cloud object-store URIs in Databricks runtime code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def repo_root() -> Path:
    """Best-effort local repo root (for local scripts/tests only)."""
    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    env = os.environ.get("PIPELINE_CONFIG_PATH")
    if env:
        return Path(env)
    return repo_root() / "config" / "pipeline_config.json"


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    path = Path(config_path) if config_path else default_config_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Pipeline config not found at {path}. "
            "Set PIPELINE_CONFIG_PATH or provide config_path."
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fully_qualified_table(config: Dict[str, Any], layer: str, table_key: str) -> str:
    """Return catalog.schema.table for Unity Catalog style names."""
    catalog = config["catalog"]
    schema = config[f"{layer}_schema"]
    table = config["tables"][table_key]
    return f"{catalog}.{schema}.{table}"


def raw_file_path(config: Dict[str, Any], filename: str) -> str:
    """Join configurable raw_data_path with a CSV filename.

    Expects ``raw_data_path`` to be a Unity Catalog Volume path such as
    ``/Volumes/<catalog>/<schema>/<volume>/raw_data``.
    """
    base = config["raw_data_path"].rstrip("/")
    return f"{base}/{filename}"


def apply_runtime_overrides(config: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Shallow-merge runtime overrides (e.g. Databricks widgets)."""
    if not overrides:
        return config
    merged = dict(config)
    for k, v in overrides.items():
        if v is not None and v != "":
            merged[k] = v
    return merged
