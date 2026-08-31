# Databricks Workflow Guide — Medallion Pipeline

## Purpose

Orchestrate the **existing** Bronze → Silver → Gold pipeline as a single Databricks Job/Workflow with explicit task dependencies.

This Workflow **reuses** existing entry points. It does **not** duplicate business logic, data-quality rules, or Gold SQL.

Dashboard SQL (`src/dashboard/dashboard_queries.sql`) remains a separate Databricks SQL step (already executed successfully outside this Job).

## Existing entry points used

| Layer | Repository entry point | Function | Workflow task |
|-------|------------------------|----------|---------------|
| Bronze | `src/bronze/ingest_all.py` | `ingest_all()` | `bronze_ingest` via `workflows/tasks/run_bronze.py` |
| Silver | `src/silver/create_silver_tables.py` | `create_silver_tables()` | `silver_quality` via `workflows/tasks/run_silver.py` |
| Gold | `src/gold/create_gold_tables.py` | `create_gold_tables()` | `gold_aggregate` via `workflows/tasks/run_gold.py` |

Thin runners only parse job parameters and call those functions.

## Task graph / dependencies

```
bronze_ingest
      ↓ (depends_on)
silver_quality
      ↓ (depends_on)
gold_aggregate
```

- Silver runs **only after** Bronze succeeds.
- Gold runs **only after** Silver succeeds.

Definition: `workflows/medallion_pipeline_job.json`

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `raw_data_path` | `/Volumes/ecommerce/landing/raw_files/raw_data` | Unity Catalog Volume folder with CSVs |
| `catalog` | `ecommerce` | Unity Catalog name |
| `bronze_schema` | `bronze` | Bronze schema |
| `silver_schema` | `silver` | Silver schema |
| `gold_schema` | `gold` | Gold schema |
| `pipeline_run_id` | _(empty)_ | Optional Bronze ingestion run id |

All path/catalog values remain configuration-driven (job parameters override `config/pipeline_config.json`).

**Do not** set `raw_data_path` to `/FileStore`, `/dbfs`, DBFS mounts, Windows paths, or hard-coded cloud URIs.

## Expected outputs

After a successful Job run:

1. **Bronze tables** under `{catalog}.{bronze_schema}` (`customers`, `orders`, `products`) with ingestion metadata  
2. **Silver tables** under `{catalog}.{silver_schema}` including DQ flags + `quality_metrics`  
3. **Gold tables** under `{catalog}.{gold_schema}`: `sales_by_product`, `revenue_by_customer`, `customer_segmentation`, `daily_weekly_trends`

## How to run in Databricks

### Status of this artifact

The Workflow definition is provided in-repo. **It is not automatically deployed or executed from Cursor.** Deploy/run it in your Databricks workspace.

### Option A — Workflows UI

1. Ensure this repo is available in Databricks Repos (includes `src/`, `config/`, `workflows/`).
2. Confirm CSVs exist at `/Volumes/ecommerce/landing/raw_files/raw_data`.
3. **Workflows → Create Job**.
4. Add three **Python** tasks pointing at:
   - `workflows/tasks/run_bronze.py`
   - `workflows/tasks/run_silver.py`
   - `workflows/tasks/run_gold.py`  
   (full Workspace/Repos paths).
5. Set dependencies: Silver depends on Bronze; Gold depends on Silver.
6. Add job parameters from the table above.
7. Attach a cluster with Unity Catalog + Volume access.
8. **Run now**.

You may also paste/adapt `workflows/medallion_pipeline_job.json` (update `python_file` to absolute Workspace paths and attach a cluster).

### Option B — Databricks CLI / Jobs API

```bash
# Example only — adjust paths and auth for your workspace.
# This was NOT run from the Cursor development environment.
databricks jobs create --json-file workflows/medallion_pipeline_job.json
databricks jobs run-now --job-id <JOB_ID>
```

Update `python_file` entries to absolute `/Workspace/Repos/...` paths before create, and configure cluster settings.

### Option C — Asset Bundle (optional)

See `workflows/databricks.yml`. Requires setting workspace `host` and running `databricks bundle deploy` / `databricks bundle run` in an authenticated environment.

## Validation

Local (repo) validation of the dependency chain:

```bash
uv run --with pytest pytest tests/test_workflow.py -v
```

This validates the Job JSON task graph and parameter defaults. It does **not** deploy or run the Job in Databricks.

## Out of scope

- Delta Live Tables (DLT)
- Structured streaming
- Airflow / external orchestrators
- Changing Bronze/Silver/Gold/dashboard business logic
