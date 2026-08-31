"""Tests for data-quality detection (local CSV mirror of Silver rules).

Full Spark Silver execution must be run in Databricks (or local Spark+Delta).
These tests validate that intended issues are detectable and metrics compute.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from data_generation.generate_sample_data import generate_all  # noqa: E402
from dq_local import compute_quality_metrics, validate_intentional_issues  # noqa: E402


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory):
    repo_data = ROOT / "data"
    expected_keys = [
        "null_emails",
        "null_order_customer_id",
        "null_order_product_id",
        "orphan_customer_id",
        "orphan_product_id",
        "duplicate_customer_id_records",
        "duplicate_order_id_records",
    ]
    if (repo_data / "customers.csv").exists():
        stats = validate_intentional_issues(repo_data)
        if stats["null_emails"] == 50 and stats["orders_rows"] == 100020:
            return repo_data
    out = tmp_path_factory.mktemp("dqdata")
    generate_all(out, seed=42)
    return out


def _by_id(metrics):
    return {m["rule_id"]: m for m in metrics}


def test_completeness_checks_detect_issues(data_dir):
    m = _by_id(compute_quality_metrics(data_dir))
    assert m["COMP_CUST_EMAIL"]["failed"] == 50
    assert m["COMP_ORD_CUST"]["failed"] == 100
    assert m["COMP_ORD_PROD"]["failed"] == 200
    assert m["COMP_CUST_EMAIL"]["pass_percentage"] < 100


def test_uniqueness_checks_flag_duplicate_rows(data_dir):
    stats = validate_intentional_issues(data_dir)
    m = _by_id(compute_quality_metrics(data_dir))
    # Policy: all rows sharing a duplicated key fail → >= 2 * duplicate_records
    assert m["UNIQ_CUST_ID"]["failed"] == stats["uniq_cust_fail_rows"]
    assert m["UNIQ_ORD_ID"]["failed"] == stats["uniq_ord_fail_rows"]
    assert m["UNIQ_CUST_ID"]["failed"] >= 20  # 10 dups → at least 20 flagged rows
    assert m["UNIQ_ORD_ID"]["failed"] >= 40


def test_referential_integrity_checks(data_dir):
    m = _by_id(compute_quality_metrics(data_dir))
    assert m["RI_ORD_CUST"]["failed"] == 50
    assert m["RI_ORD_PROD"]["failed"] == 30


def test_bad_records_are_flagged_not_removed(data_dir):
    stats = validate_intentional_issues(data_dir)
    # Row counts preserved (no silent deletion)
    assert stats["customers_rows"] == 10010
    assert stats["orders_rows"] == 100020
    metrics = compute_quality_metrics(data_dir)
    assert any(m["failed"] > 0 for m in metrics)


def test_pass_percentage_math(data_dir):
    for m in compute_quality_metrics(data_dir):
        expected = round((m["passed"] / m["total_records"]) * 100.0, 4)
        assert m["pass_percentage"] == expected
        assert m["passed"] + m["failed"] == m["total_records"]


def test_bronze_artifact_contracts():
    """Bronze scripts expose expected metadata columns in code."""
    bronze = (ROOT / "src" / "common" / "spark_utils.py").read_text(encoding="utf-8")
    assert "_ingested_at" in bronze
    assert "_source_file" in bronze
    assert "_pipeline_run_id" in bronze
    schemas = (ROOT / "src" / "common" / "schemas.py").read_text(encoding="utf-8")
    assert "CUSTOMERS_SCHEMA" in schemas
    assert "ORDERS_SCHEMA" in schemas
    assert "PRODUCTS_SCHEMA" in schemas


def test_silver_modules_exist_and_flag_not_delete():
    silver_create = (ROOT / "src" / "silver" / "create_silver_tables.py").read_text(encoding="utf-8")
    assert "dq_passed" in silver_create
    assert "dq_fail_flags" in silver_create
    assert "quality_metrics" in silver_create
    # Ensure no drop/filter that removes failed rows before write
    assert "write_delta(silver_customers" in silver_create
    assert "filter(dq_passed" not in silver_create.replace(" ", "")
