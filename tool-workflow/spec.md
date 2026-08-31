# Implementation Specification

## 1. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | Generate customers (10,000), orders (100,000), products (500) CSV files with realistic values |
| FR-02 | Introduce exact intentional DQ issue counts (see FR-DQ) |
| FR-03 | Bronze: ingest CSVs to Delta with schemas + ingestion metadata |
| FR-04 | Silver: run completeness, uniqueness, type, referential integrity, business-logic checks |
| FR-05 | Silver: flag bad records; do not silently delete |
| FR-06 | Silver: produce quality metrics with pass percentage per rule |
| FR-07 | Gold: sales_by_product, revenue_by_customer, customer_segmentation, daily/weekly trends |
| FR-08 | Dashboard: Top 10 products, customer revenue distribution, segmentation SQL |
| FR-09 | Tests covering generation, Bronze, Silver, Gold, dashboard artifacts |
| FR-10 | Full documentation and requirement traceability |

### FR-DQ — Intentional Issues

| Issue | Expected Count |
|-------|----------------|
| NULL customer email | 50 |
| Duplicate customer_id records | 10 |
| NULL order customer_id | 100 |
| NULL order product_id | 200 |
| Orphan order customer_id | 50 |
| Orphan order product_id | 30 |
| Duplicate order_id records | 20 |

## 2. Non-Functional Requirements

- Databricks-compatible (PySpark / Spark SQL / Delta)
- Configurable storage paths (no Windows paths in runtime)
- No hard-coded credentials
- Deterministic generation via seed where useful
- Maintainable, modular code
- No silent data deletion
- Honest validation reporting

## 3. Data Contracts

### customers

| Column | Type | Notes |
|--------|------|-------|
| customer_id | INT | PK |
| customer_name | STRING | |
| email | STRING | nullable (intentional NULLs) |
| country | STRING | |
| signup_date | DATE | |
| customer_segment | STRING | Premium \| Standard \| Basic |
| lifetime_value | DECIMAL | source attribute |

### orders

| Column | Type | Notes |
|--------|------|-------|
| order_id | INT | PK |
| customer_id | INT | FK → customers (nullable / orphan intentional) |
| order_date | DATE | |
| product_id | INT | FK → products (nullable / orphan intentional) |
| quantity | INT | |
| unit_price | DECIMAL | |
| total_amount | DECIMAL | typically quantity × unit_price |
| order_status | STRING | Pending \| Completed \| Cancelled |
| payment_date | DATE | nullable |

### products

| Column | Type | Notes |
|--------|------|-------|
| product_id | INT | PK |
| product_name | STRING | |
| category | STRING | |
| price | DECIMAL | |
| cost | DECIMAL | |
| stock_quantity | INT | |
| reorder_level | INT | |

## 4. Layer Responsibilities

| Layer | Responsibility |
|-------|----------------|
| Bronze | Raw CSV → Delta; cast types; `_ingested_at`, `_source_file`; row counts |
| Silver | Quality rules; flags; metrics; cleaned-but-not-deleted curated tables |
| Gold | Business aggregations for analytics/dashboard |

## 5. Quality Rules

| Rule ID | Type | Description |
|---------|------|-------------|
| COMP_CUST_EMAIL | Completeness | email IS NOT NULL |
| COMP_ORD_CUST | Completeness | customer_id IS NOT NULL |
| COMP_ORD_PROD | Completeness | product_id IS NOT NULL |
| UNIQ_CUST_ID | Uniqueness | customer_id unique |
| UNIQ_ORD_ID | Uniqueness | order_id unique |
| TYPE_* | Type | Columns castable to contract types |
| RI_ORD_CUST | Referential | customer_id exists in customers (when not null) |
| RI_ORD_PROD | Referential | product_id exists in products (when not null) |
| BL_TOTAL_AMT | Business | total_amount ≈ quantity × unit_price (tolerance) |
| BL_STATUS | Business | order_status in allowed set |
| BL_SEGMENT | Business | customer_segment in allowed set |
| BL_PAYMENT | Business | if Completed → payment_date not null; if Cancelled → payment_date null or ≤ order_date + grace |

## 6. Gold Outputs

### sales_by_product
product_id, product_name, category, total_orders, total_revenue, avg_order_value

### revenue_by_customer
customer_id, customer_name, customer_segment, total_orders, total_revenue, avg_order_value, lifetime_value_actual

### customer_segmentation
segment_type, customer_count, avg_revenue, total_revenue

### daily_weekly_trends
Documented trend grain (daily and weekly revenue/orders)

### Calculation assumption (documented)
Only `order_status = 'Completed'` included in revenue and order-count metrics unless noted otherwise.

### Segmentation assumption (documented)
Based on `lifetime_value_actual`:
- High Value: ≥ 5000
- Medium Value: ≥ 1000 and < 5000
- Low Value: < 1000
- Unknown: no completed orders

## 7. Dashboard Requirements

Queries against Gold tables for Top 10 products, revenue distribution buckets, and segmentation.

## 8. Testing Requirements

See Section 12–13 of project requirements. Local pytest for generation and pure-Python/SQL artifact checks; Spark tests designed for Databricks or local Spark if present.

## 9. Acceptance Criteria

- [ ] Repo structure matches baseline (or documented deltas)
- [ ] CSVs generated with exact DQ issue counts
- [ ] Bronze/Silver/Gold code present and config-driven
- [ ] Quality flags + metrics implemented
- [ ] Dashboard SQL + guide present
- [ ] Tests present and executed where environment allows
- [ ] Traceability matrix complete
- [ ] README and docs complete
- [ ] No false Databricks execution claims

## 10. Assumptions

| ID | Assumption |
|----|------------|
| A-01 | Completed orders only for Gold revenue metrics |
| A-02 | Segmentation thresholds as above |
| A-03 | Duplicate customer/order rows: extra copies of existing IDs |
| A-04 | Orphan FKs use IDs outside valid ranges |
| A-05 | Paths configured via `config/pipeline_config.json` / env overrides |
| A-06 | Catalog `ecommerce`, schemas `bronze`/`silver`/`gold` (configurable) |
| A-07 | Raw CSVs land on a Unity Catalog Volume path (`/Volumes/.../raw_data`); placeholder allowed until Volume exists |

## 11. Constraints

- No Windows paths in Databricks runtime code
- Prefer Unity Catalog Volumes for raw CSV storage; do not default to `/FileStore`, `/dbfs`, or DBFS mounts
- No silent deletion of bad records
- No invented business requirements without documentation
- Prefer Databricks-native approaches; avoid unnecessary dependencies
