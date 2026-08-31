# AI Prompts — Gold Layer

## Prompt / instruction

Create sales_by_product, revenue_by_customer, customer_segmentation, and trends; document calculations.

## What AI produced

- `src/gold/01`–`04_*.sql`
- `create_gold_tables.py` with `${catalog}` / schema substitution

## Decisions accepted

- Eligible = Completed + non-null valid FKs without RI/completeness FK flags  
- Segmentation thresholds 5000 / 1000 / >0 / Unknown  
- `lifetime_value_actual` = sum of eligible order amounts  

## Validation

- SQL column contracts + local AOV math: PASSED  
- Spark Gold execution: **NOT EXECUTED**
