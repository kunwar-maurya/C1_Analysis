# AI Prompts — Silver Layer

## Prompt / instruction

Implement completeness, uniqueness, type, RI, business-logic checks; flag failures; metrics with pass %.

## What AI produced

- `src/silver/01`–`05_quality_*.py`
- `create_silver_tables.py`
- Local mirror `tests/dq_local.py` for offline detection proof

## Decisions accepted

- `dq_passed` / `dq_fail_flags` / `dq_fail_reasons`  
- Uniqueness flags all rows sharing a duplicated key  
- RI evaluated only for non-null FKs  

## Validation

- Local DQ detection of intentional issues: PASSED (pytest)  
- Spark Silver job: **NOT EXECUTED**
