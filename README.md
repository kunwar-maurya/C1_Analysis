# Databricks Medallion E-Commerce Pipeline

End-to-end e-commerce data pipeline using **Medallion Architecture** on Databricks: CSV → Bronze → Silver → Gold → Databricks SQL Dashboard.

## Project Objective

Demonstrate data generation, raw ingestion, data quality validation (flagging — not silent deletion), transformation, aggregation, testing, debugging, documentation, and AI-assisted development.

## Architecture

```
customers.csv / orders.csv / products.csv
              ↓
     BRONZE (Delta + ingestion metadata)
              ↓
     SILVER (DQ flags + quality_metrics)
              ↓
     GOLD (sales / revenue / segmentation / trends)
              ↓
     Databricks SQL Dashboard
```

## Repository Structure

```
databricks-medallion-pipeline/
├── README.md
├── candidate-info.md
├── requirements-analysis.md
├── design-notes.md
├── data-model.md
├── data-quality-strategy.md
├── requirements-traceability.md
├── debugging-notes.md
├── reflection.md
├── final-ai-usage-summary.md
├── final-validation.md
├── config/
├── tool-workflow/
├── src/data_generation|bronze|silver|gold|dashboard|common/
├── data/
├── database/
├── tests/
└── ai-prompts/
```

**Structure additions (documented):** `src/common/`, `config/`, `requirements-traceability.md`, `final-validation.md` — support config-driven Databricks execution and §20 traceability.

## Datasets

| File | Rows | Notes |
|------|------|-------|
| customers.csv | 10,010 | 10,000 + 10 duplicate PK rows |
| orders.csv | 100,020 | 100,000 + 20 duplicate PK rows |
| products.csv | 500 | clean |

### Intentional DQ Issues

| Issue | Count |
|-------|-------|
| NULL customer email | 50 |
| Duplicate customer_id records | 10 |
| NULL order customer_id | 100 |
| NULL order product_id | 200 |
| Orphan customer_id | 50 |
| Orphan product_id | 30 |
| Duplicate order_id records | 20 |

## Local Setup

### Prerequisites

- Python 3.10+ (or [`uv`](https://github.com/astral-sh/uv))
- pytest (for tests)

### Generate sample data

```bash
uv run python src/data_generation/generate_sample_data.py --output-dir data --seed 42
```

### Run local tests

```bash
uv run --with pytest pytest tests/ -v
```

Local tests cover generation, CSV-mirrored Silver DQ detection, Gold math helpers, and SQL/artifact contracts.  
**They do not execute Databricks Spark jobs.**

## Databricks Setup

1. Create (or identify) a **Unity Catalog Volume** and upload `data/*.csv` to:  
   `/Volumes/<catalog>/<schema>/<volume>/raw_data`  
   Placeholder in this repo: `/Volumes/ecommerce/landing/raw_files/raw_data`  
   If the Volume is not provisioned yet, keep the placeholder — do **not** switch to FileStore/DBFS.
2. Set `raw_data_path` (and catalog/schemas) in `config/pipeline_config.json` or job widgets.  
   **Do not use** Windows paths (`D:\...`), `/FileStore`, `/dbfs`, DBFS mounts, or hard-coded cloud URIs in runtime config.
3. Attach this repo via Databricks Repos (or sync `src/` + `config/`).
4. Ensure cluster has Delta Lake / Unity Catalog access (including Volume read).

See `database/setup-notes.md` and `config/CONFIG_NOTES.md`.

## Execution Order (Databricks)

1. **Bronze:** `src/bronze/ingest_all.py`  
2. **Silver:** `src/silver/create_silver_tables.py`  
3. **Gold:** `src/gold/create_gold_tables.py`  
4. **Dashboard:** run `src/dashboard/dashboard_queries.sql` in SQL warehouse  

Example overrides:

```python
overrides = {
  "raw_data_path": "/Volumes/ecommerce/landing/raw_files/raw_data",
  "catalog": "ecommerce",
  "pipeline_run_id": "demo_001",
}
```

## Layer Summary

### Bronze
- Reads CSVs with explicit schemas
- Writes Delta tables with `_ingested_at`, `_source_file`, `_pipeline_run_id`
- Validates expected row counts

### Silver
- Completeness, uniqueness, type, referential integrity, business-logic checks
- Adds `dq_passed`, `dq_fail_flags`, `dq_fail_reasons`
- Writes `silver.quality_metrics` (pass %)
- **Never silently deletes bad records**

### Gold
- `sales_by_product`, `revenue_by_customer`, `customer_segmentation`, `daily_weekly_trends`
- Eligible orders: `order_status = 'Completed'` with valid non-null FKs (no RI/completeness FK failures)
- Segmentation on `lifetime_value_actual` thresholds (High ≥5000, Medium ≥1000, Low >0, else Unknown)

### Dashboard
- Top 10 products by revenue
- Customer revenue distribution
- Customer segmentation  
Details: `src/dashboard/DASHBOARD_GUIDE.md`

## Testing & Validation

| Scope | Status in this Cursor environment |
|-------|-----------------------------------|
| Data generation + exact DQ counts | **PASSED** |
| Local pytest (20 tests) | **PASSED** |
| Bronze/Silver/Gold Spark on Databricks | **NOT EXECUTED** (code provided) |

## Assumptions

See `requirements-analysis.md` and `design-notes.md`. Key assumptions:

- Gold revenue uses **Completed** eligible orders only
- Segmentation uses computed LTV thresholds (not source `customer_segment`)
- “N duplicate records” means N **extra** rows reusing existing PKs

## Known Limitations

- Databricks cluster execution was not performed from this development environment
- Local DQ metrics mirror Silver rules for key checks; business-logic Spark rules need Databricks run for live metrics
- Unity Catalog Volume (`raw_data_path`) is a **placeholder** until provisioned in the workspace
- Unity Catalog `CREATE CATALOG` / `CREATE VOLUME` requires appropriate privileges (adjust names to match your workspace)

## Documentation Index

| Doc | Purpose |
|-----|---------|
| tool-workflow/project-context.md | Persistent AI/project context |
| tool-workflow/spec.md | Implementation specification |
| tool-workflow/task-breakdown.md | Phased plan |
| data-quality-strategy.md | DQ framework |
| requirements-traceability.md | Requirement → artifact → test |
| final-validation.md | Acceptance audit |
| debugging-notes.md | Issues and fixes |
| ai-prompts/ | AI-assisted workflow history |
