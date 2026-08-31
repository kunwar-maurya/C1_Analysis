"""Create Silver tables with quality flags and quality_metrics."""

from __future__ import annotations

import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Iterable, List, Tuple

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
except NameError:
    # __file__ not available in Databricks REPL, use current directory
    sys.path.insert(0, str(Path.cwd().parent))

from common.config import apply_runtime_overrides, fully_qualified_table, load_config
from common.spark_utils import get_spark, write_delta


def _load_silver_modules():
    try:
        d = Path(__file__).resolve().parent
    except NameError:
        # __file__ not available in Databricks REPL, use current directory
        d = Path.cwd()
    return {
        "completeness": SourceFileLoader("q_comp", str(d / "01_quality_completeness.py")).load_module(),
        "uniqueness": SourceFileLoader("q_uniq", str(d / "02_quality_uniqueness.py")).load_module(),
        "types": SourceFileLoader("q_type", str(d / "03_quality_type_validation.py")).load_module(),
        "ri": SourceFileLoader("q_ri", str(d / "04_quality_referential_integrity.py")).load_module(),
        "biz": SourceFileLoader("q_biz", str(d / "05_quality_business_logic.py")).load_module(),
    }


def _finalize_flags(df: DataFrame, flag_cols: Iterable[str], reason_cols: Iterable[str]) -> DataFrame:
    return (
        df.withColumn(
            "dq_fail_flags",
            F.expr(
                "filter(array({}), x -> x is not null)".format(
                    ", ".join([f"`{c}`" for c in flag_cols])
                )
            ),
        )
        .withColumn(
            "dq_fail_reasons",
            F.concat_ws(
                "; ",
                F.expr(
                    "filter(array({}), x -> x is not null)".format(
                        ", ".join([f"`{c}`" for c in reason_cols])
                    )
                ),
            ),
        )
        .withColumn("dq_passed", F.size(F.col("dq_fail_flags")) == 0)
        .drop(*list(flag_cols), *list(reason_cols))
    )


def _metric_row(spark, rule_id: str, rule_name: str, dataset: str, df: DataFrame, fail_expr):
    total = df.count()
    failed = df.filter(fail_expr).count()
    passed = total - failed
    pct = round((passed / total) * 100.0, 4) if total else 0.0
    return spark.createDataFrame(
        [(rule_id, rule_name, dataset, total, passed, failed, pct)],
        "rule_id string, rule_name string, dataset string, total_records long, passed long, failed long, pass_percentage double",
    )


def build_silver_customers(bronze_customers: DataFrame, mods, spark) -> Tuple[DataFrame, DataFrame]:
    df = bronze_customers
    df = mods["completeness"].flag_customer_email_completeness(df)
    df = mods["uniqueness"].flag_customer_id_uniqueness(df)
    df = mods["types"].flag_customer_types(df)
    df = mods["biz"].flag_customer_segment(df)

    flag_cols = [
        "_flag_COMP_CUST_EMAIL",
        "_flag_UNIQ_CUST_ID",
        "_flag_TYPE_CUST",
        "_flag_BL_SEGMENT",
    ]
    reason_cols = [
        "_reason_COMP_CUST_EMAIL",
        "_reason_UNIQ_CUST_ID",
        "_reason_TYPE_CUST",
        "_reason_BL_SEGMENT",
    ]

    # Capture metrics before dropping flag cols
    metrics = [
        _metric_row(
            spark,
            "COMP_CUST_EMAIL",
            "Customer email completeness",
            "customers",
            df,
            F.col("_flag_COMP_CUST_EMAIL").isNotNull(),
        ),
        _metric_row(
            spark,
            "UNIQ_CUST_ID",
            "Customer ID uniqueness",
            "customers",
            df,
            F.col("_flag_UNIQ_CUST_ID").isNotNull(),
        ),
        _metric_row(
            spark,
            "TYPE_CUST",
            "Customer type validation",
            "customers",
            df,
            F.col("_flag_TYPE_CUST").isNotNull(),
        ),
        _metric_row(
            spark,
            "BL_SEGMENT",
            "Customer segment domain",
            "customers",
            df,
            F.col("_flag_BL_SEGMENT").isNotNull(),
        ),
    ]
    silver = _finalize_flags(df, flag_cols, reason_cols)
    from functools import reduce

    metrics_df = reduce(lambda a, b: a.unionByName(b), metrics)
    return silver, metrics_df


def build_silver_products(bronze_products: DataFrame, mods, spark) -> Tuple[DataFrame, DataFrame]:
    df = mods["types"].flag_product_types(bronze_products)
    flag_cols = ["_flag_TYPE_PROD"]
    reason_cols = ["_reason_TYPE_PROD"]
    metrics = _metric_row(
        spark,
        "TYPE_PROD",
        "Product type validation",
        "products",
        df,
        F.col("_flag_TYPE_PROD").isNotNull(),
    )
    silver = _finalize_flags(df, flag_cols, reason_cols)
    return silver, metrics


def build_silver_orders(
    bronze_orders: DataFrame,
    silver_customers: DataFrame,
    silver_products: DataFrame,
    mods,
    spark,
    amount_tolerance: float,
) -> Tuple[DataFrame, DataFrame]:
    df = bronze_orders
    df = mods["completeness"].flag_order_customer_id_completeness(df)
    df = mods["completeness"].flag_order_product_id_completeness(df)
    df = mods["uniqueness"].flag_order_id_uniqueness(df)
    df = mods["types"].flag_order_types(df)
    # RI against distinct valid IDs from bronze/silver customers & products
    # Use all customer_id/product_id values present (including dups) as reference set
    df = mods["ri"].flag_order_customer_fk(df, silver_customers.select("customer_id"))
    df = mods["ri"].flag_order_product_fk(df, silver_products.select("product_id"))
    df = mods["biz"].flag_order_total_amount(df, tolerance=amount_tolerance)
    df = mods["biz"].flag_order_status(df)
    df = mods["biz"].flag_payment_date_logic(df)

    flag_cols = [
        "_flag_COMP_ORD_CUST",
        "_flag_COMP_ORD_PROD",
        "_flag_UNIQ_ORD_ID",
        "_flag_TYPE_ORD",
        "_flag_RI_ORD_CUST",
        "_flag_RI_ORD_PROD",
        "_flag_BL_TOTAL_AMT",
        "_flag_BL_STATUS",
        "_flag_BL_PAYMENT_DATE",
    ]
    reason_cols = [
        "_reason_COMP_ORD_CUST",
        "_reason_COMP_ORD_PROD",
        "_reason_UNIQ_ORD_ID",
        "_reason_TYPE_ORD",
        "_reason_RI_ORD_CUST",
        "_reason_RI_ORD_PROD",
        "_reason_BL_TOTAL_AMT",
        "_reason_BL_STATUS",
        "_reason_BL_PAYMENT_DATE",
    ]

    metric_specs = [
        ("COMP_ORD_CUST", "Order customer_id completeness", "_flag_COMP_ORD_CUST"),
        ("COMP_ORD_PROD", "Order product_id completeness", "_flag_COMP_ORD_PROD"),
        ("UNIQ_ORD_ID", "Order ID uniqueness", "_flag_UNIQ_ORD_ID"),
        ("TYPE_ORD", "Order type validation", "_flag_TYPE_ORD"),
        ("RI_ORD_CUST", "Order customer referential integrity", "_flag_RI_ORD_CUST"),
        ("RI_ORD_PROD", "Order product referential integrity", "_flag_RI_ORD_PROD"),
        ("BL_TOTAL_AMT", "Order total_amount business rule", "_flag_BL_TOTAL_AMT"),
        ("BL_STATUS", "Order status domain", "_flag_BL_STATUS"),
        ("BL_PAYMENT_DATE", "Payment date business rule", "_flag_BL_PAYMENT_DATE"),
    ]
    from functools import reduce

    metrics = [
        _metric_row(spark, rid, name, "orders", df, F.col(col).isNotNull())
        for rid, name, col in metric_specs
    ]
    metrics_df = reduce(lambda a, b: a.unionByName(b), metrics)
    silver = _finalize_flags(df, flag_cols, reason_cols)
    return silver, metrics_df


def create_silver_tables(overrides=None):
    config = apply_runtime_overrides(load_config(), overrides)
    spark = get_spark("silver-quality")
    mods = _load_silver_modules()
    tolerance = float(config.get("quality", {}).get("amount_tolerance", 0.01))

    bronze_customers = spark.table(fully_qualified_table(config, "bronze", "customers"))
    bronze_orders = spark.table(fully_qualified_table(config, "bronze", "orders"))
    bronze_products = spark.table(fully_qualified_table(config, "bronze", "products"))

    silver_customers, m_cust = build_silver_customers(bronze_customers, mods, spark)
    silver_products, m_prod = build_silver_products(bronze_products, mods, spark)
    silver_orders, m_ord = build_silver_orders(
        bronze_orders, silver_customers, silver_products, mods, spark, tolerance
    )

    metrics = m_cust.unionByName(m_prod).unionByName(m_ord)

    write_delta(silver_customers, fully_qualified_table(config, "silver", "customers"))
    write_delta(silver_orders, fully_qualified_table(config, "silver", "orders"))
    write_delta(silver_products, fully_qualified_table(config, "silver", "products"))
    write_delta(metrics, fully_qualified_table(config, "silver", "quality_metrics"))

    print("Silver tables written.")
    metrics.show(50, truncate=False)
    return {
        "customers": fully_qualified_table(config, "silver", "customers"),
        "orders": fully_qualified_table(config, "silver", "orders"),
        "products": fully_qualified_table(config, "silver", "products"),
        "quality_metrics": fully_qualified_table(config, "silver", "quality_metrics"),
    }


if __name__ == "__main__":
    create_silver_tables()
