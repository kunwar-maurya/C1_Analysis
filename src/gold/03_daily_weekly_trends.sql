-- GOLD: Daily and Weekly Trends
-- Assumption: only eligible Completed orders (same filter as other Gold tables)

CREATE OR REPLACE TABLE ${catalog}.${gold_schema}.daily_weekly_trends AS
WITH eligible_orders AS (
  SELECT
    order_date,
    total_amount
  FROM ${catalog}.${silver_schema}.orders
  WHERE order_status = 'Completed'
    AND customer_id IS NOT NULL
    AND product_id IS NOT NULL
    AND NOT array_contains(dq_fail_flags, 'RI_ORD_CUST')
    AND NOT array_contains(dq_fail_flags, 'RI_ORD_PROD')
    AND NOT array_contains(dq_fail_flags, 'COMP_ORD_CUST')
    AND NOT array_contains(dq_fail_flags, 'COMP_ORD_PROD')
),
daily AS (
  SELECT
    'day' AS period_type,
    order_date AS period_start,
    COUNT(*) AS total_orders,
    CAST(SUM(total_amount) AS DECIMAL(18, 2)) AS total_revenue
  FROM eligible_orders
  GROUP BY order_date
),
weekly AS (
  SELECT
    'week' AS period_type,
    date_trunc('WEEK', order_date)::date AS period_start,
    COUNT(*) AS total_orders,
    CAST(SUM(total_amount) AS DECIMAL(18, 2)) AS total_revenue
  FROM eligible_orders
  GROUP BY date_trunc('WEEK', order_date)::date
)
SELECT * FROM daily
UNION ALL
SELECT * FROM weekly;
