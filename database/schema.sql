-- Logical schema reference for Medallion tables (Databricks / Unity Catalog)

CREATE CATALOG IF NOT EXISTS ecommerce;
CREATE SCHEMA IF NOT EXISTS ecommerce.bronze;
CREATE SCHEMA IF NOT EXISTS ecommerce.silver;
CREATE SCHEMA IF NOT EXISTS ecommerce.gold;

-- Bronze (created by PySpark writes; shown for documentation)
-- ecommerce.bronze.customers
-- ecommerce.bronze.orders
-- ecommerce.bronze.products
-- plus: _ingested_at, _source_file, _pipeline_run_id

-- Silver adds: dq_passed, dq_fail_flags, dq_fail_reasons
-- ecommerce.silver.quality_metrics(
--   rule_id, rule_name, dataset, total_records, passed, failed, pass_percentage
-- )

-- Gold
-- ecommerce.gold.sales_by_product
-- ecommerce.gold.revenue_by_customer
-- ecommerce.gold.customer_segmentation
-- ecommerce.gold.daily_weekly_trends
