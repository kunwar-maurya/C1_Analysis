"""Shared CLI parameter parsing for Databricks Workflow task runners.

Does not contain Bronze/Silver/Gold business logic — only job parameter plumbing.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict


DEFAULT_RAW_DATA_PATH = "/Volumes/ecommerce/landing/raw_files/raw_data"
DEFAULT_CATALOG = "ecommerce"


def build_overrides_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--raw_data_path",
        default=DEFAULT_RAW_DATA_PATH,
        help="Unity Catalog Volume path containing raw CSVs",
    )
    parser.add_argument(
        "--catalog",
        default=DEFAULT_CATALOG,
        help="Unity Catalog name for bronze/silver/gold schemas",
    )
    parser.add_argument(
        "--bronze_schema",
        default="",
        help="Optional override for bronze schema (empty = config default)",
    )
    parser.add_argument(
        "--silver_schema",
        default="",
        help="Optional override for silver schema (empty = config default)",
    )
    parser.add_argument(
        "--gold_schema",
        default="",
        help="Optional override for gold schema (empty = config default)",
    )
    parser.add_argument(
        "--pipeline_run_id",
        default="",
        help="Optional pipeline run id propagated to Bronze ingestion metadata",
    )
    return parser


def overrides_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    overrides: Dict[str, Any] = {
        "raw_data_path": args.raw_data_path,
        "catalog": args.catalog,
    }
    if args.bronze_schema:
        overrides["bronze_schema"] = args.bronze_schema
    if args.silver_schema:
        overrides["silver_schema"] = args.silver_schema
    if args.gold_schema:
        overrides["gold_schema"] = args.gold_schema
    if args.pipeline_run_id:
        overrides["pipeline_run_id"] = args.pipeline_run_id
    return overrides
