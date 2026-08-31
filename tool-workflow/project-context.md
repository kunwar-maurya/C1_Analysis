# Project Context — Databricks Medallion E-Commerce Pipeline

## Project Objective

Build an end-to-end e-commerce data pipeline on Databricks using Medallion Architecture (Bronze → Silver → Gold) with intentional data-quality issues, quality flagging (not silent deletion), Gold analytical datasets, Databricks SQL dashboard queries, tests, and full documentation.

## Business Context

An e-commerce retailer needs reliable sales and customer analytics. Raw CSV extracts (customers, orders, products) are ingested into Databricks, validated, and aggregated into Gold datasets that power SQL dashboards for product performance, customer revenue, and segmentation.

## Technical Stack

| Layer | Technology |
|-------|------------|
| Runtime | Databricks (Jobs / Notebooks / Repos) |
| Language | Python 3.x |
| Processing | PySpark, Spark SQL |
| Storage | Delta Lake |
| Analytics | Databricks SQL |
| Local | Python scripts for sample CSV generation & pytest |

**Constraint:** Core pipeline transformations use PySpark/Spark SQL — not Pandas-only processing.

## Architecture

```
CSV (customers, orders, products)
        ↓
   BRONZE (raw Delta + ingestion metadata)
        ↓
   SILVER (typed Delta + quality flags / metrics)
        ↓
   GOLD (sales_by_product, revenue_by_customer, customer_segmentation, trends)
        ↓
   Databricks SQL Dashboard
```

## Datasets

| Dataset | File | Rows | PK |
|---------|------|------|-----|
| Customers | customers.csv | 10,000 | customer_id |
| Orders | orders.csv | 100,000 | order_id |
| Products | products.csv | 500 | product_id |

Relationships: `customers` 1—∞ `orders` ∞—1 `products`

## Intentional Data-Quality Issues

**Customers:** 50 NULL emails; 10 duplicate `customer_id` records  
**Orders:** 100 NULL `customer_id`; 200 NULL `product_id`; 50 orphan `customer_id`; 30 orphan `product_id`; 20 duplicate `order_id`

Silver must **detect and flag** these — never silently delete.

## Layer Expectations

- **Bronze:** Raw ingest, schemas, ingestion timestamp/source metadata, row-count validation; no business transforms.
- **Silver:** Completeness, uniqueness, type, referential integrity, business-logic checks; flag failures; quality metrics with pass %.
- **Gold:** Sales by product; revenue by customer; customer segmentation; daily/weekly trends; documented calculation rules.

## Dashboard Requirements

1. Top 10 products by revenue  
2. Customer revenue distribution  
3. Customer segmentation  

## Testing Expectations

Validate generation (counts + DQ issues), Bronze (schema/rows/metadata), Silver (checks + flags), Gold (columns + math), dashboard SQL structure. Run what is possible locally; document what requires Databricks.

## Databricks Compatibility

- Configurable paths (no hard-coded `D:\...` in runtime code)
- **Preferred raw storage:** Unity Catalog Volumes  
  `/Volumes/<catalog>/<schema>/<volume>/raw_data`
- Do **not** recommend `/FileStore`, `/dbfs`, or DBFS mounts for raw CSV landing
- Catalog/schema/table names via config
- Suitable for Databricks Repos / Jobs
- No cloud storage SDKs unless required

## Repository Conventions

- Project root: `D:\databricks-medallion-pipeline` (local repo only)
- Config-driven paths in `config/`
- Shared helpers in `src/common/`
- Document assumptions in design/docs, not silently in code
- Update `debugging-notes.md` for failures and fixes
- Record AI-assisted work honestly in `ai-prompts/`

## Important Decisions

1. **Gold order inclusion:** Only `order_status = 'Completed'` counts toward revenue/order metrics (documented assumption).
2. **Segmentation:** Based on `lifetime_value_actual` (sum of completed order revenue) with documented thresholds.
3. **Duplicate PKs:** All rows kept in Bronze/Silver; uniqueness failures flagged on duplicate keys.
4. **Quality framework:** Per-record flag columns + centralized `silver_quality_metrics` table.
5. **Local vs Databricks:** Generation & pytest run locally; Bronze/Silver/Gold Spark code designed for Databricks (local Spark optional if available).
6. **Raw landing storage:** Unity Catalog Volumes (config placeholder if Volume not yet created); not FileStore/DBFS.
