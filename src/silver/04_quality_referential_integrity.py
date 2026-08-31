"""Silver referential integrity quality checks."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def flag_order_customer_fk(orders: DataFrame, customers: DataFrame) -> DataFrame:
    """RI_ORD_CUST: non-null customer_id must exist in customers."""
    valid = customers.select(F.col("customer_id").alias("_valid_customer_id")).distinct()
    joined = orders.join(
        valid,
        orders.customer_id == valid._valid_customer_id,
        how="left",
    )
    failed = F.col("customer_id").isNotNull() & F.col("_valid_customer_id").isNull()
    return (
        joined.withColumn(
            "_flag_RI_ORD_CUST",
            F.when(failed, F.lit("RI_ORD_CUST")).otherwise(F.lit(None)),
        )
        .withColumn(
            "_reason_RI_ORD_CUST",
            F.when(failed, F.lit("customer_id does not exist in customers")).otherwise(F.lit(None)),
        )
        .drop("_valid_customer_id")
    )


def flag_order_product_fk(orders: DataFrame, products: DataFrame) -> DataFrame:
    """RI_ORD_PROD: non-null product_id must exist in products."""
    valid = products.select(F.col("product_id").alias("_valid_product_id")).distinct()
    joined = orders.join(
        valid,
        orders.product_id == valid._valid_product_id,
        how="left",
    )
    failed = F.col("product_id").isNotNull() & F.col("_valid_product_id").isNull()
    return (
        joined.withColumn(
            "_flag_RI_ORD_PROD",
            F.when(failed, F.lit("RI_ORD_PROD")).otherwise(F.lit(None)),
        )
        .withColumn(
            "_reason_RI_ORD_PROD",
            F.when(failed, F.lit("product_id does not exist in products")).otherwise(F.lit(None)),
        )
        .drop("_valid_product_id")
    )
