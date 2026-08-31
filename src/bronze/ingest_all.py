"""Orchestrate Bronze ingestion for all entities + row-count validation."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from importlib.machinery import SourceFileLoader
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
except NameError:
    # __file__ not available in Databricks REPL, use current directory
    sys.path.insert(0, str(Path.cwd().parent))

from common.config import apply_runtime_overrides, load_config
from common.spark_utils import get_spark


EXPECTED_ROWS = {
    "customers": 10010,
    "orders": 100020,
    "products": 500,
}


def ingest_all(overrides=None):
    config = apply_runtime_overrides(load_config(), overrides)
    spark = get_spark("bronze-ingest-all")
    run_id = (overrides or {}).get("pipeline_run_id") or datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    overrides = dict(overrides or {})
    overrides["pipeline_run_id"] = run_id

    try:
        bronze_dir = Path(__file__).resolve().parent
    except NameError:
        # __file__ not available in Databricks REPL, use current directory
        bronze_dir = Path.cwd()
    cust_mod = SourceFileLoader("ingest_customers", str(bronze_dir / "01_ingest_customers.py")).load_module()
    ord_mod = SourceFileLoader("ingest_orders", str(bronze_dir / "02_ingest_orders.py")).load_module()
    prod_mod = SourceFileLoader("ingest_products", str(bronze_dir / "03_ingest_products.py")).load_module()

    results = {
        "customers": cust_mod.ingest_customers(config=config, overrides=overrides, spark=spark),
        "orders": ord_mod.ingest_orders(config=config, overrides=overrides, spark=spark),
        "products": prod_mod.ingest_products(config=config, overrides=overrides, spark=spark),
    }

    validation = {}
    for entity, expected in EXPECTED_ROWS.items():
        actual = results[entity]["rows"]
        ok = actual == expected
        validation[entity] = {"expected": expected, "actual": actual, "passed": ok}
        status = "PASS" if ok else "FAIL"
        print(f"Row-count validation [{entity}]: {status} expected={expected} actual={actual}")

    if not all(v["passed"] for v in validation.values()):
        raise AssertionError(f"Bronze row-count validation failed: {validation}")

    return {"results": results, "validation": validation, "pipeline_run_id": run_id}


if __name__ == "__main__":
    ingest_all()
