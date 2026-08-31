-- Databricks SQL Dashboard Queries
-- Consume Gold tables. Replace catalog/schema if needed.
-- Default: ecommerce.gold

-- =============================================================================
-- 1) Top 10 Products by Revenue
-- Purpose: Rank best-selling products by total_revenue
-- Visualization: Horizontal bar chart (product_name vs total_revenue)
-- Important fields: product_name, category, total_revenue, total_orders, avg_order_value
-- =============================================================================
CREATE OR REPLACE VIEW ecommerce.gold.dash_top10_products AS
SELECT
  product_id,
  product_name,
  category,
  total_orders,
  total_revenue,
  avg_order_value
FROM ecommerce.gold.sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;

-- Query for dashboard widget:
SELECT * FROM ecommerce.gold.dash_top10_products;


-- =============================================================================
-- 2) Customer Revenue Distribution
-- Purpose: Show how customers distribute across revenue buckets
-- Visualization: Histogram / bar chart of bucket vs customer_count
-- Important fields: revenue_bucket, customer_count, total_revenue
-- =============================================================================
CREATE OR REPLACE VIEW ecommerce.gold.dash_customer_revenue_distribution AS
SELECT
  CASE
    WHEN lifetime_value_actual >= 5000 THEN '5000+'
    WHEN lifetime_value_actual >= 1000 THEN '1000-4999'
    WHEN lifetime_value_actual >= 100 THEN '100-999'
    WHEN lifetime_value_actual > 0 THEN '0.01-99'
    ELSE '0'
  END AS revenue_bucket,
  COUNT(*) AS customer_count,
  CAST(SUM(lifetime_value_actual) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(AVG(lifetime_value_actual) AS DECIMAL(18, 2)) AS avg_revenue
FROM ecommerce.gold.revenue_by_customer
GROUP BY
  CASE
    WHEN lifetime_value_actual >= 5000 THEN '5000+'
    WHEN lifetime_value_actual >= 1000 THEN '1000-4999'
    WHEN lifetime_value_actual >= 100 THEN '100-999'
    WHEN lifetime_value_actual > 0 THEN '0.01-99'
    ELSE '0'
  END
ORDER BY
  CASE
    WHEN revenue_bucket = '0' THEN 1
    WHEN revenue_bucket = '0.01-99' THEN 2
    WHEN revenue_bucket = '100-999' THEN 3
    WHEN revenue_bucket = '1000-4999' THEN 4
    ELSE 5
  END;

SELECT * FROM ecommerce.gold.dash_customer_revenue_distribution;


-- =============================================================================
-- 3) Customer Segmentation
-- Purpose: Summarize High/Medium/Low/Unknown revenue segments
-- Visualization: Pie or donut (customer_count); optional bar for total_revenue
-- Important fields: segment_type, customer_count, avg_revenue, total_revenue
-- =============================================================================
SELECT
  segment_type,
  customer_count,
  avg_revenue,
  total_revenue
FROM ecommerce.gold.customer_segmentation
ORDER BY
  CASE segment_type
    WHEN 'High Value' THEN 1
    WHEN 'Medium Value' THEN 2
    WHEN 'Low Value' THEN 3
    ELSE 4
  END;


-- =============================================================================
-- Optional: Daily revenue trend (line chart)
-- =============================================================================
SELECT
  period_start,
  total_orders,
  total_revenue
FROM ecommerce.gold.daily_weekly_trends
WHERE period_type = 'day'
ORDER BY period_start;
