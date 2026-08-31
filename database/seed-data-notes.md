# Seed Data Notes

Seed data is generated locally by:

```bash
python src/data_generation/generate_sample_data.py
```

Files land in `data/`:

- `customers.csv` (10,010 rows)
- `orders.csv` (100,020 rows)
- `products.csv` (500 rows)

Upload these CSVs to the Databricks **Unity Catalog Volume** path configured as `raw_data_path` in `config/pipeline_config.json` before Bronze ingestion.

Preferred pattern: `/Volumes/<catalog>/<schema>/<volume>/raw_data`  
Placeholder: `/Volumes/ecommerce/landing/raw_files/raw_data`

Do not treat local repo `data/` paths as Databricks runtime paths inside pipeline code. Do not use FileStore or DBFS as the landing location.
