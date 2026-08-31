"""Spark I/O helpers shared across Bronze/Silver/Gold."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType


def get_spark(app_name: str = "medallion-pipeline") -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def read_csv_with_schema(
    spark: SparkSession,
    path: str,
    schema: StructType,
) -> DataFrame:
    return (
        spark.read.format("csv")
        .option("header", True)
        .option("mode", "PERMISSIVE")
        .schema(schema)
        .load(path)
    )


def with_ingestion_metadata(
    df: DataFrame,
    source_file: str,
    pipeline_run_id: Optional[str] = None,
) -> DataFrame:
    run_id = pipeline_run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return (
        df.withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.lit(source_file))
        .withColumn("_pipeline_run_id", F.lit(run_id))
    )


def write_delta(
    df: DataFrame,
    table_name: str,
    mode: str = "overwrite",
) -> None:
    (
        df.write.format("delta")
        .mode(mode)
        .option("overwriteSchema", "true")
        .saveAsTable(table_name)
    )


def ensure_schemas(spark: SparkSession, catalog: str, schemas: list[str]) -> None:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
    for schema in schemas:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
