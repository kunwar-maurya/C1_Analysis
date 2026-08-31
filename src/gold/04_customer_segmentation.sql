-- GOLD 3: Customer Segmentation
-- Segmentation is based on lifetime_value_actual (completed eligible order revenue),
-- NOT on source customer_segment (Premium/Standard/Basic).
--
-- Thresholds (documented assumption):
--   High Value:   lifetime_value_actual >= 5000
--   Medium Value: lifetime_value_actual >= 1000 AND < 5000
--   Low Value:    lifetime_value_actual > 0 AND < 1000
--   Unknown:      lifetime_value_actual = 0 (no eligible completed orders)

CREATE OR REPLACE TABLE ${catalog}.${gold_schema}.customer_segmentation AS
WITH scored AS (
  SELECT
    customer_id,
    lifetime_value_actual,
    CASE
      WHEN lifetime_value_actual >= 5000 THEN 'High Value'
      WHEN lifetime_value_actual >= 1000 THEN 'Medium Value'
      WHEN lifetime_value_actual > 0 THEN 'Low Value'
      ELSE 'Unknown'
    END AS segment_type
  FROM ${catalog}.${gold_schema}.revenue_by_customer
)
SELECT
  segment_type,
  COUNT(*) AS customer_count,
  CAST(AVG(lifetime_value_actual) AS DECIMAL(18, 2)) AS avg_revenue,
  CAST(SUM(lifetime_value_actual) AS DECIMAL(18, 2)) AS total_revenue
FROM scored
GROUP BY segment_type
ORDER BY
  CASE segment_type
    WHEN 'High Value' THEN 1
    WHEN 'Medium Value' THEN 2
    WHEN 'Low Value' THEN 3
    ELSE 4
  END;
