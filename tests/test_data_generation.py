"""Tests for sample data generation and intentional DQ issues."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from data_generation.generate_sample_data import generate_all  # noqa: E402
from dq_local import compute_quality_metrics, validate_intentional_issues  # noqa: E402

EXPECTED = {
    "customers_rows": 10010,
    "orders_rows": 100020,
    "products_rows": 500,
    "null_emails": 50,
    "duplicate_customer_id_records": 10,
    "null_order_customer_id": 100,
    "null_order_product_id": 200,
    "orphan_customer_id": 50,
    "orphan_product_id": 30,
    "duplicate_order_id_records": 20,
}


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory):
    """Generate into temp dir OR reuse repo data/ if already valid."""
    repo_data = ROOT / "data"
    if (repo_data / "customers.csv").exists():
        stats = validate_intentional_issues(repo_data)
        if all(stats[k] == EXPECTED[k] for k in EXPECTED):
            return repo_data
    out = tmp_path_factory.mktemp("data")
    generate_all(out, seed=42)
    return out


def test_row_counts(data_dir):
    stats = validate_intentional_issues(data_dir)
    assert stats["customers_rows"] == 10010
    assert stats["orders_rows"] == 100020
    assert stats["products_rows"] == 500


def test_intentional_null_counts(data_dir):
    stats = validate_intentional_issues(data_dir)
    assert stats["null_emails"] == 50
    assert stats["null_order_customer_id"] == 100
    assert stats["null_order_product_id"] == 200


def test_intentional_duplicate_counts(data_dir):
    stats = validate_intentional_issues(data_dir)
    assert stats["duplicate_customer_id_records"] == 10
    assert stats["duplicate_order_id_records"] == 20


def test_intentional_orphan_fk_counts(data_dir):
    stats = validate_intentional_issues(data_dir)
    assert stats["orphan_customer_id"] == 50
    assert stats["orphan_product_id"] == 30


def test_expected_columns_exist(data_dir):
    import csv

    with (data_dir / "customers.csv").open(newline="", encoding="utf-8") as f:
        assert set(next(csv.reader(f))) == {
            "customer_id",
            "customer_name",
            "email",
            "country",
            "signup_date",
            "customer_segment",
            "lifetime_value",
        }
    with (data_dir / "orders.csv").open(newline="", encoding="utf-8") as f:
        assert set(next(csv.reader(f))) == {
            "order_id",
            "customer_id",
            "order_date",
            "product_id",
            "quantity",
            "unit_price",
            "total_amount",
            "order_status",
            "payment_date",
        }
    with (data_dir / "products.csv").open(newline="", encoding="utf-8") as f:
        assert set(next(csv.reader(f))) == {
            "product_id",
            "product_name",
            "category",
            "price",
            "cost",
            "stock_quantity",
            "reorder_level",
        }


def test_generation_function_validation_dict():
    # Unit-level: generate_all returns matching validation dict
    import tempfile
    from pathlib import Path as P

    with tempfile.TemporaryDirectory() as td:
        result = generate_all(P(td), seed=42)
        for k, v in EXPECTED.items():
            assert result.validation[k] == v
