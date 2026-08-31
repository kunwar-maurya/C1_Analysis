# Pipeline Configuration Template

Copy `pipeline_config.json` and override for your workspace.

## Preferred storage: Unity Catalog Volumes

Raw CSVs must be read from a **Unity Catalog Volume** path:

```text
/Volumes/<catalog>/<schema>/<volume>/raw_data
```

Default placeholder in this repo:

```text
/Volumes/ecommerce/landing/raw_files/raw_data
```

If the Volume does not yet exist in your Databricks workspace, keep this placeholder (or edit `unity_catalog_volume` + `raw_data_path` to your real names). **Do not** replace it with `/FileStore`, `/dbfs`, DBFS mounts, Windows paths, or hard-coded cloud URIs.

## Key settings

| Key | Description | Example |
|-----|-------------|---------|
| `raw_data_path` | Unity Catalog Volume folder containing CSVs | `/Volumes/ecommerce/landing/raw_files/raw_data` |
| `unity_catalog_volume` | Placeholder metadata for catalog/schema/volume/subdir | see `pipeline_config.json` |
| `catalog` | Unity Catalog name for Delta tables | `ecommerce` |
| `bronze_schema` / `silver_schema` / `gold_schema` | Schema names | `bronze`, `silver`, `gold` |

## Job parameters / widgets

Recommended Databricks widgets:

- `raw_data_path`
- `catalog`
- `pipeline_run_id`

Environment variable override (optional): `PIPELINE_CONFIG_PATH`

## Local note

CSV generation writes to the repo `data/` directory (local only). Upload those files into the configured Unity Catalog Volume `raw_data_path` before Bronze ingest.
