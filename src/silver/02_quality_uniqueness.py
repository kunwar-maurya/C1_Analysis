"""Silver uniqueness quality checks."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def flag_customer_id_uniqueness(customers: DataFrame) -> DataFrame:
    """UNIQ_CUST_ID: customer_id must be unique. All rows sharing a duplicated key fail."""
    w = Window.partitionBy("customer_id")
    with_counts = customers.withColumn("_cust_id_cnt", F.count("*").over(w))
    failed = F.col("_cust_id_cnt") > 1
    return (
        with_counts.withColumn(
            "_flag_UNIQ_CUST_ID",
            F.when(failed, F.lit("UNIQ_CUST_ID")).otherwise(F.lit(None)),
        )
        .withColumn(
            "_reason_UNIQ_CUST_ID",
            F.when(failed, F.lit("customer_id is not unique")).otherwise(F.lit(None)),
        )
        .drop("_cust_id_cnt")
    )


def flag_order_id_uniqueness(orders: DataFrame) -> DataFrame:
    """UNIQ_ORD_ID: order_id must be unique. All rows sharing a duplicated key fail."""
    w = Window.partitionBy("order_id")
    with_counts = orders.withColumn("_ord_id_cnt", F.count("*").over(w))
    failed = F.col("_ord_id_cnt") > 1
    return (
        with_counts.withColumn(
            "_flag_UNIQ_ORD_ID",
            F.when(failed, F.lit("UNIQ_ORD_ID")).otherwise(F.lit(None)),
        )
        .withColumn(
            "_reason_UNIQ_ORD_ID",
            F.when(failed, F.lit("order_id is not unique")).otherwise(F.lit(None)),
        )
        .drop("_ord_id_cnt")
    )
