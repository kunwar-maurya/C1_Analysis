"""Bronze: ingest customers.csv into Delta."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python src/bronze/...` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.config import apply_runtime_overrides, fully_qualified_table, load_config, raw_file_path
from common.schemas import CUSTOMERS_SCHEMA
from common.spark_utils import ensure_schemas, get_spark, read_csv_with_schema, with_ingestion_metadata, write_delta


def ingest_customers(config=None, overrides=None, spark=None):
    config = apply_runtime_overrides(config or load_config(), overrides)
    spark = spark or get_spark("bronze-ingest-customers")

    ensure_schemas(
        spark,
        config["catalog"],
        [config["bronze_schema"], config["silver_schema"], config["gold_schema"]],
    )

    source = raw_file_path(config, "customers.csv")
    df = read_csv_with_schema(spark, source, CUSTOMERS_SCHEMA)
    run_id = (overrides or {}).get("pipeline_run_id")
    df = with_ingestion_metadata(df, source_file=source, pipeline_run_id=run_id)

    table = fully_qualified_table(config, "bronze", "customers")
    write_delta(df, table)

    count = df.count()
    print(f"Bronze customers written to {table}; rows={count}")
    return {"table": table, "rows": count, "source": source}


if __name__ == "__main__":
    ingest_customers()
