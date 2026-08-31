# AI Prompts — Bronze Layer

## Prompt / instruction

Implement Bronze CSV → Delta with schemas, ingestion metadata, row-count validation; config-driven paths.

## What AI produced

- `src/bronze/01_ingest_customers.py`, `02_ingest_orders.py`, `03_ingest_products.py`, `ingest_all.py`
- `src/common/schemas.py`, `spark_utils.py`, `config.py`
- `config/pipeline_config.json`

## Decisions accepted

- Explicit StructType schemas  
- Metadata: `_ingested_at`, `_source_file`, `_pipeline_run_id`  
- Expected rows include duplicate extras (10010 / 100020 / 500)
- Raw CSV path via Unity Catalog Volume config (`/Volumes/.../raw_data`), not FileStore/DBFS

## Validation

- Local: artifact/contract tests PASSED  
- Databricks Spark ingest: **NOT EXECUTED**
- Storage-path compatibility correction: Volumes preferred (see debugging-notes DBG-005)
