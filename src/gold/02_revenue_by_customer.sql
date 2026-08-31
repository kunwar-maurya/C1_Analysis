-- GOLD 2: Revenue by Customer
-- lifetime_value_actual = SUM(total_amount) of eligible completed orders
-- Source customer_segment retained; lifetime_value_actual is computed

CREATE OR REPLACE TABLE ${catalog}.${gold_schema}.revenue_by_customer AS
WITH cust AS (
  SELECT customer_id, customer_name, customer_segment
  FROM (
    SELECT
      customer_id,
      customer_name,
      customer_segment,
      ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY customer_id) AS rn
    FROM ${catalog}.${silver_schema}.customers
  )
  WHERE rn = 1
),
eligible_orders AS (
  SELECT *
  FROM ${catalog}.${silver_schema}.orders
  WHERE order_status = 'Completed'
    AND customer_id IS NOT NULL
    AND product_id IS NOT NULL
    AND NOT array_contains(dq_fail_flags, 'RI_ORD_CUST')
    AND NOT array_contains(dq_fail_flags, 'RI_ORD_PROD')
    AND NOT array_contains(dq_fail_flags, 'COMP_ORD_CUST')
    AND NOT array_contains(dq_fail_flags, 'COMP_ORD_PROD')
)
SELECT
  c.customer_id,
  c.customer_name,
  c.customer_segment,
  COUNT(o.order_id) AS total_orders,
  CAST(COALESCE(SUM(o.total_amount), 0) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(
    CASE WHEN COUNT(o.order_id) = 0 THEN NULL
         ELSE SUM(o.total_amount) / COUNT(o.order_id)
    END AS DECIMAL(18, 2)
  ) AS avg_order_value,
  CAST(COALESCE(SUM(o.total_amount), 0) AS DECIMAL(18, 2)) AS lifetime_value_actual
FROM cust c
LEFT JOIN eligible_orders o
  ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_segment;
