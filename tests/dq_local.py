"""Local CSV-based DQ validators mirroring Silver rules (no Spark required).

Used by tests to prove intentional issues are detectable. Databricks Silver
implementation remains the source of truth for runtime.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def _blank(v) -> bool:
    return v is None or str(v).strip() == ""


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_intentional_issues(data_dir: Path) -> Dict[str, int]:
    customers = read_csv(data_dir / "customers.csv")
    orders = read_csv(data_dir / "orders.csv")
    products = read_csv(data_dir / "products.csv")

    valid_cust = set(range(1, 10001))
    valid_prod = set(range(1, 501))

    cust_counts = Counter(int(c["customer_id"]) for c in customers)
    order_counts = Counter(int(o["order_id"]) for o in orders)

    return {
        "customers_rows": len(customers),
        "orders_rows": len(orders),
        "products_rows": len(products),
        "null_emails": sum(1 for c in customers if _blank(c.get("email"))),
        "duplicate_customer_id_records": sum(v - 1 for v in cust_counts.values() if v > 1),
        "null_order_customer_id": sum(1 for o in orders if _blank(o.get("customer_id"))),
        "null_order_product_id": sum(1 for o in orders if _blank(o.get("product_id"))),
        "orphan_customer_id": sum(
            1
            for o in orders
            if not _blank(o.get("customer_id")) and int(o["customer_id"]) not in valid_cust
        ),
        "orphan_product_id": sum(
            1
            for o in orders
            if not _blank(o.get("product_id")) and int(o["product_id"]) not in valid_prod
        ),
        "duplicate_order_id_records": sum(v - 1 for v in order_counts.values() if v > 1),
        "uniq_cust_fail_rows": sum(1 for c in customers if cust_counts[int(c["customer_id"])] > 1),
        "uniq_ord_fail_rows": sum(1 for o in orders if order_counts[int(o["order_id"])] > 1),
    }


def compute_quality_metrics(data_dir: Path) -> List[Dict]:
    """Approximate Silver metrics from CSV for local validation."""
    customers = read_csv(data_dir / "customers.csv")
    orders = read_csv(data_dir / "orders.csv")
    products = read_csv(data_dir / "products.csv")
    cust_ids = {int(c["customer_id"]) for c in customers}
    prod_ids = {int(p["product_id"]) for p in products}
    cust_counts = Counter(int(c["customer_id"]) for c in customers)
    order_counts = Counter(int(o["order_id"]) for o in orders)

    def metric(rule_id, dataset, total, failed):
        passed = total - failed
        return {
            "rule_id": rule_id,
            "dataset": dataset,
            "total_records": total,
            "passed": passed,
            "failed": failed,
            "pass_percentage": round((passed / total) * 100.0, 4) if total else 0.0,
        }

    metrics = [
        metric("COMP_CUST_EMAIL", "customers", len(customers), sum(1 for c in customers if _blank(c.get("email")))),
        metric("UNIQ_CUST_ID", "customers", len(customers), sum(1 for c in customers if cust_counts[int(c["customer_id"])] > 1)),
        metric("COMP_ORD_CUST", "orders", len(orders), sum(1 for o in orders if _blank(o.get("customer_id")))),
        metric("COMP_ORD_PROD", "orders", len(orders), sum(1 for o in orders if _blank(o.get("product_id")))),
        metric("UNIQ_ORD_ID", "orders", len(orders), sum(1 for o in orders if order_counts[int(o["order_id"])] > 1)),
        metric(
            "RI_ORD_CUST",
            "orders",
            len(orders),
            sum(
                1
                for o in orders
                if not _blank(o.get("customer_id")) and int(o["customer_id"]) not in cust_ids
            ),
        ),
        metric(
            "RI_ORD_PROD",
            "orders",
            len(orders),
            sum(
                1
                for o in orders
                if not _blank(o.get("product_id")) and int(o["product_id"]) not in prod_ids
            ),
        ),
    ]
    return metrics


def gold_sales_by_product_from_csv(data_dir: Path) -> List[Dict]:
    """Local Gold-like aggregation for math tests (mirrors eligibility rules without dq flags)."""
    from decimal import Decimal, ROUND_HALF_UP

    orders = read_csv(data_dir / "orders.csv")
    products = read_csv(data_dir / "products.csv")
    prod = {}
    for p in products:
        pid = int(p["product_id"])
        if pid not in prod:
            prod[pid] = p

    valid_cust = {int(c["customer_id"]) for c in read_csv(data_dir / "customers.csv")}
    valid_prod = set(prod.keys())

    agg = defaultdict(lambda: {"total_orders": 0, "total_revenue": Decimal("0")})
    for o in orders:
        if o.get("order_status") != "Completed":
            continue
        if _blank(o.get("customer_id")) or _blank(o.get("product_id")):
            continue
        cid, pid = int(o["customer_id"]), int(o["product_id"])
        if cid not in valid_cust or pid not in valid_prod:
            continue
        agg[pid]["total_orders"] += 1
        agg[pid]["total_revenue"] += Decimal(o["total_amount"])

    rows = []
    for pid, vals in agg.items():
        p = prod[pid]
        if vals["total_orders"]:
            aov = (vals["total_revenue"] / Decimal(vals["total_orders"])).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            aov = None
        rows.append(
            {
                "product_id": pid,
                "product_name": p["product_name"],
                "category": p["category"],
                "total_orders": vals["total_orders"],
                "total_revenue": float(
                    vals["total_revenue"].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                ),
                "avg_order_value": float(aov) if aov is not None else None,
            }
        )
    return rows
