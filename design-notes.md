# Design Notes

## Architecture Overview

Medallion Architecture on Databricks Delta Lake:

1. **Landing / files:** CSV under a configurable **Unity Catalog Volume** path
2. **Bronze:** Append/overwrite raw typed Delta tables with ingestion metadata
3. **Silver:** Same grain as Bronze entities plus quality flag columns and a metrics table
4. **Gold:** Aggregated business tables for analytics
5. **Serving:** Databricks SQL queries / dashboard

## Path Configuration

`config/pipeline_config.json` defines:

- `raw_data_path` — Unity Catalog Volume folder containing CSVs  
  Pattern: `/Volumes/<catalog>/<schema>/<volume>/raw_data`  
  Placeholder default: `/Volumes/ecommerce/landing/raw_files/raw_data`
- `unity_catalog_volume` — placeholder metadata (`catalog` / `schema` / `volume` / `subdir`) when the Volume is not yet provisioned
- `catalog`, `bronze_schema`, `silver_schema`, `gold_schema`
- table name prefixes

**Not recommended / not used as defaults:** `/FileStore`, `/dbfs`, DBFS mounts, Windows paths, or hard-coded cloud URIs.

Local generation writes to `./data/` relative to repo root. Databricks jobs set `raw_data_path` to the Volume location where CSVs were uploaded.

## Bronze Design

- Explicit StructType schemas
- `option("header", True)`, inferSchema=False with explicit casts
- Columns: `_ingested_at` (timestamp), `_source_file` (string), `_pipeline_run_id` (string)
- Mode: overwrite for demo reproducibility (documented); production could switch to append + merge

## Silver Quality Framework

Each Silver entity table includes:

- All Bronze business columns
- `dq_passed` (boolean) — true if all applicable rules pass
- `dq_fail_flags` (array<string>) — rule IDs that failed
- `dq_fail_reasons` (string) — human-readable summary

Additionally:

- `silver.quality_check_results` — optional detail grain (rule_id, record_key, status)
- `silver.quality_metrics` — Rule, Total Records, Passed, Failed, Pass Percentage

Bad records remain in Silver tables with flags.

## Gold Calculation Rules

**Eligible orders:** `order_status = 'Completed'` AND `dq_passed = true` for order-level RI/completeness where needed.

**Assumption A-GOLD-FILTER:** For revenue aggregations, use Silver orders where:
- `order_status = 'Completed'`
- `customer_id` and `product_id` are not null
- referential integrity flags pass for those FKs (`RI_ORD_CUST`, `RI_ORD_PROD` not in fail flags)

This avoids inflating revenue with orphan/null keys while retaining failed rows in Silver for DQ reporting.

**Metrics:**
- `total_orders` = count of eligible orders
- `total_revenue` = sum(`total_amount`) of eligible orders
- `avg_order_value` = `total_revenue / total_orders` (null-safe)
- `lifetime_value_actual` = customer's `total_revenue`

**Segmentation (`segment_type`):** based on `lifetime_value_actual`:
- High Value: ≥ 5000
- Medium Value: 1000–4999.99
- Low Value: > 0 and < 1000
- Unknown: 0 or no eligible orders

Note: This is **revenue-based segmentation**, distinct from source `customer_segment` (Premium/Standard/Basic).

## Trends Gold

`gold.daily_weekly_trends` provides:
- `period_type` (day|week)
- `period_start`
- `total_orders`
- `total_revenue`

## Error Handling

- Missing config → clear exception
- Missing source files → fail with path context
- Quality modules are additive and idempotent per run

## Structure Delta from Baseline

Added:
- `src/common/` — shared config/schema helpers (maintainability)
- `config/` — pipeline configuration templates
- `requirements-traceability.md` — required by §20

These support Databricks compatibility without changing required baseline paths.
