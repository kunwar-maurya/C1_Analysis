# Dashboard Guide

## Overview

Databricks SQL dashboard backed by Gold Delta tables in catalog `ecommerce`, schema `gold`.

Upload / run `src/dashboard/dashboard_queries.sql` in a Databricks SQL warehouse after Gold tables exist.

## Widgets

### 1. Top 10 Products by Revenue

| Item | Detail |
|------|--------|
| Query | `SELECT * FROM ecommerce.gold.dash_top10_products` (or inline ORDER BY LIMIT 10 on `sales_by_product`) |
| Purpose | Identify highest-revenue products |
| Visualization | Horizontal bar chart — X: `total_revenue`, Y: `product_name` |
| Measures | `total_revenue`, `total_orders`, `avg_order_value` |
| Dimensions | `product_name`, `category` |

### 2. Customer Revenue Distribution

| Item | Detail |
|------|--------|
| Query | `dash_customer_revenue_distribution` view / query in `dashboard_queries.sql` |
| Purpose | Understand concentration of spend across customers |
| Visualization | Bar chart — X: `revenue_bucket`, Y: `customer_count` |
| Measures | `customer_count`, `total_revenue`, `avg_revenue` |
| Dimensions | `revenue_bucket` |

### 3. Customer Segmentation

| Item | Detail |
|------|--------|
| Query | Select from `ecommerce.gold.customer_segmentation` |
| Purpose | Compare High / Medium / Low / Unknown segments |
| Visualization | Pie/donut on `customer_count`; secondary bar on `total_revenue` |
| Measures | `customer_count`, `avg_revenue`, `total_revenue` |
| Dimensions | `segment_type` |

### Optional: Daily Trend

Line chart of `total_revenue` over `period_start` where `period_type = 'day'`.

## Setup Steps

1. Complete Bronze → Silver → Gold pipeline.
2. Attach SQL warehouse to the workspace catalog.
3. Run `dashboard_queries.sql`.
4. Create a Databricks SQL Dashboard and add visualizations mapped to the queries above.

## Notes

- Segmentation uses **lifetime_value_actual** thresholds (see `design-notes.md`), not source `customer_segment`.
- Gold revenue includes only eligible **Completed** orders (documented assumption).
