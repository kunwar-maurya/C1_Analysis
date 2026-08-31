# Data Generation Notes

## Purpose

Create realistic local CSV inputs for the Databricks Bronze layer, including exact intentional data-quality issues.

## How to run

```bash
python src/data_generation/generate_sample_data.py
# or
python src/data_generation/generate_sample_data.py --output-dir data --seed 42
```

## Outputs

| File | Rows | Notes |
|------|------|-------|
| data/customers.csv | 10,010 | 10,000 base + 10 duplicate PK rows |
| data/orders.csv | 100,020 | 100,000 base + 20 duplicate PK rows |
| data/products.csv | 500 | clean |

## Intentional issues (exact)

| Issue | Count |
|-------|-------|
| NULL / blank customer email | 50 |
| Extra duplicate customer_id rows | 10 |
| NULL / blank order customer_id | 100 |
| NULL / blank order product_id | 200 |
| Orphan order customer_id | 50 |
| Orphan order product_id | 30 |
| Extra duplicate order_id rows | 20 |

Blank CSV fields represent NULL for Spark ingestion.

## Duplicate semantics (assumption AMB-03 / AMB-04)

"N duplicate X_id records" means N **additional rows** that reuse existing primary keys. Base unique IDs remain 1..N for the clean population.

## Determinism

Seed default = 42.

## Validation

`validate_generated()` runs automatically after issue injection and raises if counts differ from expected.
