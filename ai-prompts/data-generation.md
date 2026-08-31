# AI Prompts — Data Generation

## Prompt / instruction

Implement generation for 10k/100k/500 rows with exact intentional DQ issues and auto-validation.

## What AI produced

- `src/data_generation/generate_sample_data.py`
- `DATA_GENERATION_NOTES.md`
- Generated `data/*.csv`

## Decisions accepted

- Seed = 42  
- Blank CSV fields for NULLs  
- Duplicates created before NULL/orphan injection  

## Modified

- Reordered issue injection after initial design risk (DBG-002)

## Validation

```
customers_rows: 10010
orders_rows: 100020
products_rows: 500
null_emails: 50
duplicate_customer_id_records: 10
null_order_customer_id: 100
null_order_product_id: 200
orphan_customer_id: 50
orphan_product_id: 30
duplicate_order_id_records: 20
```

Result: **PASSED**
