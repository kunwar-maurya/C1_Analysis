# Data Model

## Conceptual Relationships

```
customers (1) ──────── (many) orders (many) ──────── (1) products
```

## Primary Keys

| Table | PK |
|-------|-----|
| customers | customer_id |
| orders | order_id |
| products | product_id |

## Foreign Keys

| From | Column | To |
|------|--------|-----|
| orders | customer_id | customers.customer_id |
| orders | product_id | products.product_id |

Note: Generated data intentionally violates FK completeness/integrity for a controlled subset of orders.

## Grain

| Entity | Grain |
|--------|-------|
| customers | One row per customer (plus intentional duplicate PK rows in raw/Bronze/Silver) |
| orders | One row per order (plus intentional duplicate PK rows) |
| products | One row per product |
| gold.sales_by_product | One row per product |
| gold.revenue_by_customer | One row per distinct customer_id that appears in customers (deduped for aggregation) |
| gold.customer_segmentation | One row per segment_type |
| gold.daily_weekly_trends | One row per period_type + period_start |

## Important Business Fields

- `order_status`: Pending | Completed | Cancelled
- `customer_segment`: Premium | Standard | Basic (source attribute)
- `lifetime_value`: source marketing/CRM attribute (not Gold actual)
- `lifetime_value_actual`: computed from completed eligible orders
- `total_amount`: order line total (single product per order in this model)

## Layer Responsibilities

| Layer | Tables | Responsibility |
|-------|--------|----------------|
| Bronze | bronze.customers, bronze.orders, bronze.products | Raw typed ingest + metadata |
| Silver | silver.customers, silver.orders, silver.products, silver.quality_metrics | Curated + DQ flags/metrics |
| Gold | gold.sales_by_product, gold.revenue_by_customer, gold.customer_segmentation, gold.daily_weekly_trends | Analytics |

## Order Model Note

Each order references a single `product_id` (order-line grain = order grain). Quantity and unit_price determine `total_amount`.
