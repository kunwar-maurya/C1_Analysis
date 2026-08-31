"""Silver completeness quality checks."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def flag_customer_email_completeness(customers: DataFrame) -> DataFrame:
    """COMP_CUST_EMAIL: email must be non-null and non-blank."""
    failed = F.col("email").isNull() | (F.trim(F.col("email")) == "")
    return customers.withColumn(
        "_flag_COMP_CUST_EMAIL",
        F.when(failed, F.lit("COMP_CUST_EMAIL")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_COMP_CUST_EMAIL",
        F.when(failed, F.lit("email is null or blank")).otherwise(F.lit(None)),
    )


def flag_order_customer_id_completeness(orders: DataFrame) -> DataFrame:
    """COMP_ORD_CUST: customer_id must be present."""
    failed = F.col("customer_id").isNull()
    return orders.withColumn(
        "_flag_COMP_ORD_CUST",
        F.when(failed, F.lit("COMP_ORD_CUST")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_COMP_ORD_CUST",
        F.when(failed, F.lit("customer_id is null")).otherwise(F.lit(None)),
    )


def flag_order_product_id_completeness(orders: DataFrame) -> DataFrame:
    """COMP_ORD_PROD: product_id must be present."""
    failed = F.col("product_id").isNull()
    return orders.withColumn(
        "_flag_COMP_ORD_PROD",
        F.when(failed, F.lit("COMP_ORD_PROD")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_COMP_ORD_PROD",
        F.when(failed, F.lit("product_id is null")).otherwise(F.lit(None)),
    )
