"""Databricks validation helpers — run AFTER Bronze/Silver on a cluster.

These assertions prove intentional DQ issues were detected in Silver metrics.
Do not claim success unless this module is actually executed in Databricks.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import apply_runtime_overrides, fully_qualified_table, load_config
from common.spark_utils import get_spark


def validate_silver_detects_intentional_issues(overrides=None):
    config = apply_runtime_overrides(load_config(), overrides)
    spark = get_spark("validate-silver-dq")
    metrics = spark.table(fully_qualified_table(config, "silver", "quality_metrics"))
    rows = {r["rule_id"]: r for r in metrics.collect()}

    expectations = {
        "COMP_CUST_EMAIL": 50,
        "COMP_ORD_CUST": 100,
        "COMP_ORD_PROD": 200,
        "RI_ORD_CUST": 50,
        "RI_ORD_PROD": 30,
    }
    results = {}
    for rule, expected_failed in expectations.items():
        actual = int(rows[rule]["failed"]) if rule in rows else None
        results[rule] = {
            "expected_failed": expected_failed,
            "actual_failed": actual,
            "passed": actual == expected_failed,
        }

    # Uniqueness: at least 2 * introduced duplicate records
    results["UNIQ_CUST_ID"] = {
        "expected_failed_min": 20,
        "actual_failed": int(rows["UNIQ_CUST_ID"]["failed"]) if "UNIQ_CUST_ID" in rows else None,
        "passed": "UNIQ_CUST_ID" in rows and int(rows["UNIQ_CUST_ID"]["failed"]) >= 20,
    }
    results["UNIQ_ORD_ID"] = {
        "expected_failed_min": 40,
        "actual_failed": int(rows["UNIQ_ORD_ID"]["failed"]) if "UNIQ_ORD_ID" in rows else None,
        "passed": "UNIQ_ORD_ID" in rows and int(rows["UNIQ_ORD_ID"]["failed"]) >= 40,
    }

    for k, v in results.items():
        print(k, v)

    if not all(v["passed"] for v in results.values()):
        raise AssertionError(f"Silver intentional-issue validation failed: {results}")
    return results


if __name__ == "__main__":
    validate_silver_detects_intentional_issues()
