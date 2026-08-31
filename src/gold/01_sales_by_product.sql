-- GOLD 1: Sales by Product
-- Eligible orders: Completed + non-null FKs + no RI/completeness FK failures
-- total_orders = COUNT(*), total_revenue = SUM(total_amount),
-- avg_order_value = total_revenue / total_orders

CREATE OR REPLACE TABLE ${catalog}.${gold_schema}.sales_by_product AS
SELECT
  p.product_id,
  p.product_name,
  p.category,
  COUNT(*) AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(SUM(o.total_amount) / COUNT(*) AS DECIMAL(18, 2)) AS avg_order_value
FROM ${catalog}.${silver_schema}.orders o
INNER JOIN (
  SELECT product_id, product_name, category
  FROM (
    SELECT
      product_id,
      product_name,
      category,
      ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY product_id) AS rn
    FROM ${catalog}.${silver_schema}.products
  )
  WHERE rn = 1
) p
  ON o.product_id = p.product_id
WHERE o.order_status = 'Completed'
  AND o.customer_id IS NOT NULL
  AND o.product_id IS NOT NULL
  AND NOT array_contains(o.dq_fail_flags, 'RI_ORD_CUST')
  AND NOT array_contains(o.dq_fail_flags, 'RI_ORD_PROD')
  AND NOT array_contains(o.dq_fail_flags, 'COMP_ORD_CUST')
  AND NOT array_contains(o.dq_fail_flags, 'COMP_ORD_PROD')
GROUP BY p.product_id, p.product_name, p.category;
