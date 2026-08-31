"""
Generate realistic e-commerce sample CSVs with intentional data-quality issues.

Local development script. Outputs to repo `data/` by default.
Does not hard-code Databricks runtime paths.

Expected clean base rows:
  customers: 10,000
  orders:    100,000
  products:  500

Intentional issues (exact):
  customers: 50 NULL emails; 10 duplicate customer_id records
  orders:    100 NULL customer_id; 200 NULL product_id;
             50 orphan customer_id; 30 orphan product_id;
             20 duplicate order_id records

After adding duplicates, file row counts are:
  customers.csv: 10,010
  orders.csv:    100,020
  products.csv:  500
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


SEED = 42

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Aarav", "Ananya", "Wei", "Yuki", "Omar", "Fatima", "Carlos", "Sofia", "Hans", "Ingrid",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Patel", "Kim", "Chen", "Singh", "Khan", "Ali", "Rossi", "Mueller", "Silva", "Costa",
]

COUNTRIES = [
    "United States", "Canada", "United Kingdom", "Germany", "France", "India",
    "Australia", "Brazil", "Japan", "Mexico", "Spain", "Italy", "Netherlands",
    "Singapore", "United Arab Emirates",
]

SEGMENTS = ["Premium", "Standard", "Basic"]
ORDER_STATUSES = ["Pending", "Completed", "Cancelled"]

CATEGORIES = {
    "Electronics": ["Wireless Headphones", "USB-C Hub", "Bluetooth Speaker", "Smart Watch", "Laptop Stand"],
    "Home": ["Ceramic Mug Set", "Throw Pillow", "LED Desk Lamp", "Storage Bin", "Kitchen Towels"],
    "Apparel": ["Cotton T-Shirt", "Running Shorts", "Fleece Hoodie", "Baseball Cap", "Crew Socks"],
    "Sports": ["Yoga Mat", "Resistance Bands", "Water Bottle", "Jump Rope", "Dumbbell Pair"],
    "Beauty": ["Face Moisturizer", "Lip Balm Pack", "Shampoo Bottle", "Body Lotion", "Nail Kit"],
    "Grocery": ["Organic Coffee", "Granola Mix", "Olive Oil", "Herbal Tea", "Trail Mix"],
    "Toys": ["Building Blocks", "Puzzle Set", "Remote Car", "Board Game", "Plush Animal"],
    "Books": ["Paperback Novel", "Cookbook", "History Guide", "Kids Storybook", "Productivity Journal"],
}


def money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def random_date(rng: random.Random, start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, max(delta, 0)))


@dataclass
class GenerationResult:
    customers_path: Path
    orders_path: Path
    products_path: Path
    validation: Dict[str, int]


def generate_products(rng: random.Random, n: int = 500) -> List[Dict]:
    rows: List[Dict] = []
    cat_names = list(CATEGORIES.keys())
    for i in range(1, n + 1):
        category = cat_names[(i - 1) % len(cat_names)]
        base_name = CATEGORIES[category][(i - 1) % len(CATEGORIES[category])]
        price = money(rng.uniform(5.0, 799.99))
        cost = money(float(price) * rng.uniform(0.35, 0.75))
        stock = rng.randint(0, 5000)
        reorder = max(5, stock // 10)
        rows.append(
            {
                "product_id": i,
                "product_name": f"{base_name} {i:03d}",
                "category": category,
                "price": f"{price:.2f}",
                "cost": f"{cost:.2f}",
                "stock_quantity": stock,
                "reorder_level": reorder,
            }
        )
    return rows


def generate_customers(rng: random.Random, n: int = 10000) -> List[Dict]:
    rows: List[Dict] = []
    start = date(2018, 1, 1)
    end = date(2025, 12, 31)
    for i in range(1, n + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        segment = rng.choices(SEGMENTS, weights=[0.15, 0.55, 0.30])[0]
        ltv_base = {"Premium": (2000, 15000), "Standard": (200, 4000), "Basic": (0, 800)}[segment]
        rows.append(
            {
                "customer_id": i,
                "customer_name": f"{first} {last}",
                "email": f"{first.lower()}.{last.lower()}{i}@example.com",
                "country": rng.choice(COUNTRIES),
                "signup_date": random_date(rng, start, end).isoformat(),
                "customer_segment": segment,
                "lifetime_value": f"{money(rng.uniform(*ltv_base)):.2f}",
            }
        )
    return rows


def generate_orders(
    rng: random.Random,
    customers: Sequence[Dict],
    products: Sequence[Dict],
    n: int = 100000,
) -> List[Dict]:
    rows: List[Dict] = []
    product_by_id = {int(p["product_id"]): p for p in products}
    cust_ids = [int(c["customer_id"]) for c in customers]
    start = date(2023, 1, 1)
    end = date(2026, 8, 1)

    for i in range(1, n + 1):
        cust_id = rng.choice(cust_ids)
        prod_id = rng.randint(1, len(products))
        product = product_by_id[prod_id]
        qty = rng.randint(1, 5)
        unit_price = money(float(product["price"]) * rng.uniform(0.85, 1.05))
        total = money(float(unit_price) * qty)
        status = rng.choices(ORDER_STATUSES, weights=[0.12, 0.78, 0.10])[0]
        order_dt = random_date(rng, start, end)
        payment_date: Optional[str]
        if status == "Completed":
            payment_date = (order_dt + timedelta(days=rng.randint(0, 7))).isoformat()
        elif status == "Pending":
            payment_date = ""
        else:
            payment_date = ""

        rows.append(
            {
                "order_id": i,
                "customer_id": cust_id,
                "order_date": order_dt.isoformat(),
                "product_id": prod_id,
                "quantity": qty,
                "unit_price": f"{unit_price:.2f}",
                "total_amount": f"{total:.2f}",
                "order_status": status,
                "payment_date": payment_date,
            }
        )
    return rows


def introduce_customer_issues(rng: random.Random, customers: List[Dict]) -> None:
    # Duplicate first from clean rows so later NULL emails are not copied.
    for _ in range(10):
        src = rng.choice(customers[:10000])
        dup = dict(src)
        dup["customer_name"] = src["customer_name"] + " (DUP)"
        if dup["email"]:
            dup["email"] = "dup." + dup["email"]
        customers.append(dup)

    # 50 NULL emails among the original 10,000 only (exact count)
    idxs = rng.sample(range(10000), 50)
    for idx in idxs:
        customers[idx]["email"] = ""


def introduce_order_issues(
    rng: random.Random,
    orders: List[Dict],
    valid_customer_ids: Sequence[int],
    valid_product_ids: Sequence[int],
) -> None:
    # Duplicate first from clean base rows so issue injection stays exact.
    for _ in range(20):
        src = rng.choice(orders[:100000])
        dup = dict(src)
        dup["quantity"] = int(src["quantity"]) + 1
        unit = money(float(src["unit_price"]))
        dup["unit_price"] = f"{unit:.2f}"
        dup["total_amount"] = f"{money(float(unit) * int(dup['quantity'])):.2f}"
        orders.append(dup)

    # Apply DQ issues only to the original 100,000 rows (disjoint index sets).
    all_idxs = list(range(100000))
    rng.shuffle(all_idxs)

    null_cust_idxs = all_idxs[:100]
    null_prod_idxs = all_idxs[100:300]
    orphan_cust_idxs = all_idxs[300:350]
    orphan_prod_idxs = all_idxs[350:380]

    for idx in null_cust_idxs:
        orders[idx]["customer_id"] = ""

    for idx in null_prod_idxs:
        orders[idx]["product_id"] = ""

    max_cust = max(valid_customer_ids)
    max_prod = max(valid_product_ids)
    for i, idx in enumerate(orphan_cust_idxs):
        orders[idx]["customer_id"] = max_cust + 1000 + i

    for i, idx in enumerate(orphan_prod_idxs):
        orders[idx]["product_id"] = max_prod + 1000 + i


def write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = {k: ("" if row.get(k) is None else row.get(k)) for k in fieldnames}
            writer.writerow(out)


def _is_blank(value: object) -> bool:
    return value is None or str(value).strip() == ""


def validate_generated(
    customers: Sequence[Dict],
    orders: Sequence[Dict],
    products: Sequence[Dict],
) -> Dict[str, int]:
    cust_ids = [c["customer_id"] for c in customers]
    order_ids = [o["order_id"] for o in orders]
    valid_cust = set(range(1, 10001))
    valid_prod = set(range(1, 501))

    null_emails = sum(1 for c in customers if _is_blank(c.get("email")))
    # duplicate customer_id *records* beyond unique count
    from collections import Counter

    cust_counts = Counter(int(c["customer_id"]) for c in customers)
    dup_cust_records = sum(v - 1 for v in cust_counts.values() if v > 1)

    null_order_cust = sum(1 for o in orders if _is_blank(o.get("customer_id")))
    null_order_prod = sum(1 for o in orders if _is_blank(o.get("product_id")))

    orphan_cust = 0
    orphan_prod = 0
    for o in orders:
        if not _is_blank(o.get("customer_id")):
            cid = int(o["customer_id"])
            if cid not in valid_cust:
                orphan_cust += 1
        if not _is_blank(o.get("product_id")):
            pid = int(o["product_id"])
            if pid not in valid_prod:
                orphan_prod += 1

    order_counts = Counter(int(o["order_id"]) for o in orders)
    dup_order_records = sum(v - 1 for v in order_counts.values() if v > 1)

    result = {
        "customers_rows": len(customers),
        "orders_rows": len(orders),
        "products_rows": len(products),
        "null_emails": null_emails,
        "duplicate_customer_id_records": dup_cust_records,
        "null_order_customer_id": null_order_cust,
        "null_order_product_id": null_order_prod,
        "orphan_customer_id": orphan_cust,
        "orphan_product_id": orphan_prod,
        "duplicate_order_id_records": dup_order_records,
    }

    expected = {
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

    mismatches = {k: (result[k], expected[k]) for k in expected if result[k] != expected[k]}
    if mismatches:
        raise AssertionError(f"Generation validation failed: {mismatches}")
    return result


def generate_all(output_dir: Path, seed: int = SEED) -> GenerationResult:
    rng = random.Random(seed)
    products = generate_products(rng, 500)
    customers = generate_customers(rng, 10000)
    orders = generate_orders(rng, customers, products, 100000)

    introduce_customer_issues(rng, customers)
    introduce_order_issues(
        rng,
        orders,
        valid_customer_ids=list(range(1, 10001)),
        valid_product_ids=list(range(1, 501)),
    )

    validation = validate_generated(customers, orders, products)

    customers_path = output_dir / "customers.csv"
    orders_path = output_dir / "orders.csv"
    products_path = output_dir / "products.csv"

    write_csv(
        customers_path,
        [
            "customer_id",
            "customer_name",
            "email",
            "country",
            "signup_date",
            "customer_segment",
            "lifetime_value",
        ],
        customers,
    )
    write_csv(
        orders_path,
        [
            "order_id",
            "customer_id",
            "order_date",
            "product_id",
            "quantity",
            "unit_price",
            "total_amount",
            "order_status",
            "payment_date",
        ],
        orders,
    )
    write_csv(
        products_path,
        [
            "product_id",
            "product_name",
            "category",
            "price",
            "cost",
            "stock_quantity",
            "reorder_level",
        ],
        products,
    )

    return GenerationResult(customers_path, orders_path, products_path, validation)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate e-commerce sample CSVs")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for CSV files (default: <repo>/data)",
    )
    parser.add_argument("--seed", type=int, default=SEED)
    args, unknown = parser.parse_known_args(argv)

    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        try:
            repo = Path(__file__).resolve().parents[2]
            output_dir = repo / "data"
        except NameError:
            # __file__ not available in Databricks REPL, use current directory
            output_dir = Path("data")

    result = generate_all(output_dir, seed=args.seed)
    print("Generation complete.")
    print(f"  customers: {result.customers_path}")
    print(f"  orders:    {result.orders_path}")
    print(f"  products:  {result.products_path}")
    print("Validation:")
    for k, v in result.validation.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    main()
