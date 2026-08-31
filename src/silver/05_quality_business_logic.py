"""Silver business-logic quality checks."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


ALLOWED_SEGMENTS = ["Premium", "Standard", "Basic"]
ALLOWED_STATUSES = ["Pending", "Completed", "Cancelled"]


def flag_order_total_amount(orders: DataFrame, tolerance: float = 0.01) -> DataFrame:
    """BL_TOTAL_AMT: total_amount ≈ quantity * unit_price."""
    expected = F.col("quantity") * F.col("unit_price")
    failed = (F.abs(F.col("total_amount") - expected) > F.lit(tolerance)) | F.col("quantity").isNull()
    # Only fail when both sides present but mismatch; null quantity already type-failed
    mismatch = F.col("quantity").isNotNull() & F.col("unit_price").isNotNull() & F.col(
        "total_amount"
    ).isNotNull() & (F.abs(F.col("total_amount") - expected) > F.lit(tolerance))
    return orders.withColumn(
        "_flag_BL_TOTAL_AMT",
        F.when(mismatch, F.lit("BL_TOTAL_AMT")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_BL_TOTAL_AMT",
        F.when(mismatch, F.lit("total_amount does not equal quantity * unit_price")).otherwise(
            F.lit(None)
        ),
    )


def flag_order_status(orders: DataFrame) -> DataFrame:
    """BL_STATUS: order_status in allowed set."""
    failed = ~F.col("order_status").isin(ALLOWED_STATUSES) | F.col("order_status").isNull()
    return orders.withColumn(
        "_flag_BL_STATUS",
        F.when(failed, F.lit("BL_STATUS")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_BL_STATUS",
        F.when(failed, F.lit("order_status not in Pending|Completed|Cancelled")).otherwise(
            F.lit(None)
        ),
    )


def flag_customer_segment(customers: DataFrame) -> DataFrame:
    """BL_SEGMENT: customer_segment in allowed set."""
    failed = ~F.col("customer_segment").isin(ALLOWED_SEGMENTS) | F.col("customer_segment").isNull()
    return customers.withColumn(
        "_flag_BL_SEGMENT",
        F.when(failed, F.lit("BL_SEGMENT")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_BL_SEGMENT",
        F.when(failed, F.lit("customer_segment not in Premium|Standard|Basic")).otherwise(
            F.lit(None)
        ),
    )


def flag_payment_date_logic(orders: DataFrame) -> DataFrame:
    """BL_PAYMENT_DATE: Completed orders should have payment_date; Cancelled should not require it."""
    completed_missing = (F.col("order_status") == "Completed") & F.col("payment_date").isNull()
    pending_with_payment = (F.col("order_status") == "Pending") & F.col("payment_date").isNotNull()
    failed = completed_missing | pending_with_payment
    return orders.withColumn(
        "_flag_BL_PAYMENT_DATE",
        F.when(failed, F.lit("BL_PAYMENT_DATE")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_BL_PAYMENT_DATE",
        F.when(
            completed_missing,
            F.lit("Completed order missing payment_date"),
        )
        .when(pending_with_payment, F.lit("Pending order unexpectedly has payment_date"))
        .otherwise(F.lit(None)),
    )
