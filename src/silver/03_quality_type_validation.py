"""Silver type validation quality checks.

Bronze already applies schemas. These checks flag nulls that indicate
unparseable values for required typed fields, and invalid domain values.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def flag_customer_types(customers: DataFrame) -> DataFrame:
    failed = (
        F.col("customer_id").isNull()
        | F.col("customer_name").isNull()
        | F.col("country").isNull()
        | F.col("signup_date").isNull()
        | F.col("customer_segment").isNull()
        | F.col("lifetime_value").isNull()
    )
    return customers.withColumn(
        "_flag_TYPE_CUST",
        F.when(failed, F.lit("TYPE_CUST")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_TYPE_CUST",
        F.when(failed, F.lit("one or more required customer typed fields are null")).otherwise(
            F.lit(None)
        ),
    )


def flag_order_types(orders: DataFrame) -> DataFrame:
    # customer_id / product_id nulls are completeness issues; type check focuses on other fields
    failed = (
        F.col("order_id").isNull()
        | F.col("order_date").isNull()
        | F.col("quantity").isNull()
        | F.col("unit_price").isNull()
        | F.col("total_amount").isNull()
        | F.col("order_status").isNull()
    )
    return orders.withColumn(
        "_flag_TYPE_ORD",
        F.when(failed, F.lit("TYPE_ORD")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_TYPE_ORD",
        F.when(failed, F.lit("one or more required order typed fields are null")).otherwise(
            F.lit(None)
        ),
    )


def flag_product_types(products: DataFrame) -> DataFrame:
    failed = (
        F.col("product_id").isNull()
        | F.col("product_name").isNull()
        | F.col("category").isNull()
        | F.col("price").isNull()
        | F.col("cost").isNull()
        | F.col("stock_quantity").isNull()
        | F.col("reorder_level").isNull()
    )
    return products.withColumn(
        "_flag_TYPE_PROD",
        F.when(failed, F.lit("TYPE_PROD")).otherwise(F.lit(None)),
    ).withColumn(
        "_reason_TYPE_PROD",
        F.when(failed, F.lit("one or more required product typed fields are null")).otherwise(
            F.lit(None)
        ),
    )
