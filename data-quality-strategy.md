# Data Quality Strategy

## Principles

1. **Detect, don't hide** — intentional issues must surface in Silver.
2. **Flag, don't delete** — failed records remain queryable.
3. **Explain failures** — rule ID + reason on each record.
4. **Measure** — pass percentage per rule.
5. **Extensible** — new rules register into the same metrics pattern.

## Dimensions Covered

| Dimension | Rules |
|-----------|-------|
| Completeness | COMP_CUST_EMAIL, COMP_ORD_CUST, COMP_ORD_PROD |
| Uniqueness | UNIQ_CUST_ID, UNIQ_ORD_ID |
| Type validation | TYPE_CUST_*, TYPE_ORD_*, TYPE_PROD_* |
| Referential integrity | RI_ORD_CUST, RI_ORD_PROD |
| Business logic | BL_TOTAL_AMT, BL_STATUS, BL_SEGMENT, BL_PAYMENT_DATE |

## Record-Level Output

Silver entity tables include:

| Column | Meaning |
|--------|---------|
| dq_passed | All applicable rules passed |
| dq_fail_flags | Array of failed rule IDs |
| dq_fail_reasons | Semicolon-separated explanations |

## Metrics Output

`silver.quality_metrics`:

| Column | Description |
|--------|-------------|
| rule_id | Stable rule identifier |
| rule_name | Human-readable name |
| dataset | customers \| orders \| products |
| total_records | Denominator |
| passed | Count passed |
| failed | Count failed |
| pass_percentage | passed / total_records * 100 |

## Expected Detection (Post-Generation)

Given intentional issues, Silver should report approximately:

| Rule | Expected Failures (approx) |
|------|----------------------------|
| COMP_CUST_EMAIL | 50 |
| UNIQ_CUST_ID | 10 duplicate rows (+ originals share key; uniqueness failure marks all rows with duplicated IDs) |
| COMP_ORD_CUST | 100 |
| COMP_ORD_PROD | 200 |
| RI_ORD_CUST | ≥ 50 orphan non-null customer_ids (nulls counted under completeness, not RI) |
| RI_ORD_PROD | ≥ 30 orphan non-null product_ids |
| UNIQ_ORD_ID | duplicate order_id rows flagged |

**Uniqueness marking policy:** All rows whose key appears more than once are flagged (not only the "extra" copies). Document this so failure counts may exceed "10" / "20" duplicate *records introduced*.

## Process Flow

```
Bronze tables
    → apply rule modules (completeness → uniqueness → type → RI → business)
    → union fail flags per record
    → write Silver tables
    → aggregate quality_metrics
```

## Reporting Example

| Rule | Total | Passed | Failed | Pass % |
|------|-------|--------|--------|--------|
| COMP_CUST_EMAIL | 10010 | 9960 | 50 | 99.50 |

## Scalability

New rules: implement function returning (key, rule_id, passed, reason), register in `create_silver_tables.py` rule list, metrics auto-aggregate.
