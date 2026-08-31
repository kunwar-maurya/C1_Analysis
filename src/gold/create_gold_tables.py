"""Create Gold analytical tables by executing Gold SQL scripts.

Uses Spark SQL. Placeholder tokens ${catalog}, ${silver_schema}, ${gold_schema}
are substituted from pipeline config (Databricks-compatible; no Windows paths).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
except NameError:
    # __file__ not available in Databricks REPL, use current directory
    sys.path.insert(0, str(Path.cwd().parent))

from common.config import apply_runtime_overrides, load_config
from common.spark_utils import ensure_schemas, get_spark


SQL_FILES = [
    "01_sales_by_product.sql",
    "02_revenue_by_customer.sql",
    "03_daily_weekly_trends.sql",
    "04_customer_segmentation.sql",
]


def _render_sql(text: str, config: dict) -> str:
    replacements = {
        "${catalog}": config["catalog"],
        "${bronze_schema}": config["bronze_schema"],
        "${silver_schema}": config["silver_schema"],
        "${gold_schema}": config["gold_schema"],
    }
    out = text
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def create_gold_tables(overrides=None):
    config = apply_runtime_overrides(load_config(), overrides)
    spark = get_spark("gold-create")
    ensure_schemas(
        spark,
        config["catalog"],
        [config["bronze_schema"], config["silver_schema"], config["gold_schema"]],
    )

    try:
        gold_dir = Path(__file__).resolve().parent
    except NameError:
        # __file__ not available in Databricks REPL, use current directory
        gold_dir = Path.cwd()
    # Order matters: segmentation depends on revenue_by_customer
    for name in SQL_FILES:
        path = gold_dir / name
        sql = _render_sql(path.read_text(encoding="utf-8"), config)
        # Strip pure comment-only leading lines is unnecessary; Spark accepts comments
        print(f"Executing {name} ...")
        spark.sql(sql)

    print("Gold tables created:")
    for key in [
        "sales_by_product",
        "revenue_by_customer",
        "daily_weekly_trends",
        "customer_segmentation",
    ]:
        table = f"{config['catalog']}.{config['gold_schema']}.{config['tables'][key]}"
        count = spark.table(table).count()
        print(f"  {table}: {count} rows")

    return True


if __name__ == "__main__":
    create_gold_tables()
