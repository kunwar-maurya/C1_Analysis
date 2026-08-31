"""Tests for Gold aggregations and dashboard SQL artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from data_generation.generate_sample_data import generate_all  # noqa: E402
from dq_local import gold_sales_by_product_from_csv, read_csv  # noqa: E402


@pytest.fixture(scope="module")
def data_dir(tmp_path_factory):
    repo_data = ROOT / "data"
    if (repo_data / "orders.csv").exists():
        return repo_data
    out = tmp_path_factory.mktemp("golddata")
    generate_all(out, seed=42)
    return out


REQUIRED_SALES_COLS = {
    "product_id",
    "product_name",
    "category",
    "total_orders",
    "total_revenue",
    "avg_order_value",
}

REQUIRED_REV_COLS = {
    "customer_id",
    "customer_name",
    "customer_segment",
    "total_orders",
    "total_revenue",
    "avg_order_value",
    "lifetime_value_actual",
}

REQUIRED_SEG_COLS = {"segment_type", "customer_count", "avg_revenue", "total_revenue"}


def test_gold_sql_expected_columns():
    sales = (ROOT / "src" / "gold" / "01_sales_by_product.sql").read_text(encoding="utf-8")
    for col in REQUIRED_SALES_COLS:
        assert col in sales
    rev = (ROOT / "src" / "gold" / "02_revenue_by_customer.sql").read_text(encoding="utf-8")
    for col in REQUIRED_REV_COLS:
        assert col in rev
    seg = (ROOT / "src" / "gold" / "04_customer_segmentation.sql").read_text(encoding="utf-8")
    for col in REQUIRED_SEG_COLS:
        assert col in seg


def test_avg_order_value_math(data_dir):
    from decimal import Decimal, ROUND_HALF_UP

    rows = gold_sales_by_product_from_csv(data_dir)
    assert rows, "Expected at least one product aggregation row"
    for r in rows:
        if r["total_orders"]:
            expected = float(
                (Decimal(str(r["total_revenue"])) / Decimal(r["total_orders"])).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            assert r["avg_order_value"] == expected


def test_revenue_excludes_non_completed(data_dir):
    orders = read_csv(data_dir / "orders.csv")
    completed = [o for o in orders if o["order_status"] == "Completed"]
    cancelled = [o for o in orders if o["order_status"] == "Cancelled"]
    assert completed and cancelled
    # Local aggregator only sums Completed — cancelled revenue not included
    rows = gold_sales_by_product_from_csv(data_dir)
    total_rev = sum(r["total_revenue"] for r in rows)
    # Sanity: total gold revenue should be less than sum of ALL order amounts
    all_amt = sum(float(o["total_amount"]) for o in orders)
    assert total_rev < all_amt


def test_segmentation_consistency_rules():
    seg_sql = (ROOT / "src" / "gold" / "04_customer_segmentation.sql").read_text(encoding="utf-8")
    assert "High Value" in seg_sql
    assert "Medium Value" in seg_sql
    assert "Low Value" in seg_sql
    assert "Unknown" in seg_sql
    assert "5000" in seg_sql
    assert "1000" in seg_sql
    assert "lifetime_value_actual" in seg_sql


def test_dashboard_queries_present():
    sql = (ROOT / "src" / "dashboard" / "dashboard_queries.sql").read_text(encoding="utf-8")
    assert "Top 10" in sql or "top10" in sql.lower() or "LIMIT 10" in sql
    assert "revenue" in sql.lower()
    assert "segment" in sql.lower()
    assert "sales_by_product" in sql
    assert "customer_segmentation" in sql


def test_dashboard_guide_exists():
    guide = ROOT / "src" / "dashboard" / "DASHBOARD_GUIDE.md"
    assert guide.exists()
    text = guide.read_text(encoding="utf-8")
    assert "Top 10" in text
    assert "Visualization" in text


def test_config_has_no_windows_runtime_path():
    cfg = (ROOT / "config" / "pipeline_config.json").read_text(encoding="utf-8")
    assert "D:\\" not in cfg
    assert "D:/" not in cfg


def test_config_prefers_unity_catalog_volume_path():
    import json

    cfg = json.loads((ROOT / "config" / "pipeline_config.json").read_text(encoding="utf-8"))
    path = cfg["raw_data_path"]
    assert path.startswith("/Volumes/"), path
    assert path.rstrip("/").endswith("/raw_data"), path
    assert "/FileStore" not in path
    assert "/dbfs" not in path.lower()
    assert "unity_catalog_volume" in cfg
    vol = cfg["unity_catalog_volume"]
    assert vol["catalog"] and vol["schema"] and vol["volume"] and vol["subdir"]


def test_docs_do_not_recommend_filestore_or_dbfs():
    """Ensure key docs no longer present FileStore/DBFS as recommended defaults."""
    files = [
        ROOT / "config" / "pipeline_config.json",
        ROOT / "config" / "CONFIG_NOTES.md",
        ROOT / "database" / "setup-notes.md",
        ROOT / "README.md",
        ROOT / "design-notes.md",
    ]
    for path in files:
        text = path.read_text(encoding="utf-8")
        # Allow mentioning FileStore/DBFS only as explicitly disallowed alternatives
        for banned_default in (
            '"/FileStore',
            "e.g. `/FileStore",
            "or a Volume",
            "/FileStore/ecommerce/raw",
            "dbutils.widgets.text(\n    \"raw_data_path\",\n    \"/FileStore",
        ):
            assert banned_default not in text, f"{path} still contains banned default pattern: {banned_default}"
        # Default raw path examples must be Volumes when shown as the configured path
        if path.name == "pipeline_config.json":
            assert "/Volumes/" in text
            assert "/FileStore" not in text
            assert "/dbfs" not in text.lower()
