# Database / Databricks Setup Notes

## Prerequisites

- Databricks workspace with **Unity Catalog**
- A Unity Catalog **Volume** for raw CSV landing (preferred storage)
- Cluster or SQL warehouse with Delta Lake support
- Repo checked out via Databricks Repos **or** files uploaded to workspace

## Raw data path (Unity Catalog Volumes)

Preferred pattern:

```text
/Volumes/<catalog>/<schema>/<volume>/raw_data
```

Repository placeholder (configure to match your workspace):

```text
/Volumes/ecommerce/landing/raw_files/raw_data
```

Example Volume setup (adjust names as needed):

```sql
CREATE SCHEMA IF NOT EXISTS ecommerce.landing;
CREATE VOLUME IF NOT EXISTS ecommerce.landing.raw_files;
-- Then upload customers.csv, orders.csv, products.csv under:
-- /Volumes/ecommerce/landing/raw_files/raw_data/
```

If the Volume is not provisioned yet, keep the placeholder in `config/pipeline_config.json` and create it before running Bronze. **Do not** use `/FileStore`, `/dbfs`, DBFS mounts, local Windows paths, or hard-coded cloud storage URIs as the recommended path.

## Steps

1. Generate CSVs locally (`src/data_generation/generate_sample_data.py`).
2. Create/configure the Unity Catalog Volume and upload CSVs to `raw_data_path`.
3. Update `config/pipeline_config.json` (or job widgets) for catalog/schemas/`raw_data_path`.
4. On a cluster with the repo available, run the pipeline scripts.

Recommended job task order:

1. `src/bronze/ingest_all.py`
2. `src/silver/create_silver_tables.py`
3. `src/gold/create_gold_tables.py`
4. Run `src/dashboard/dashboard_queries.sql` in SQL warehouse
5. Optional: `src/silver/validate_intentional_issues.py`

## Widget overrides

```python
dbutils.widgets.text(
    "raw_data_path",
    "/Volumes/ecommerce/landing/raw_files/raw_data",
)
dbutils.widgets.text("catalog", "ecommerce")
overrides = {
  "raw_data_path": dbutils.widgets.get("raw_data_path"),
  "catalog": dbutils.widgets.get("catalog"),
}
```

## Permissions

Grant the job principal:

- Privileges to create schemas/tables in the target catalog
- `READ VOLUME` (and upload/write as needed) on the raw landing Volume
