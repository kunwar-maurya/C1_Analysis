# AI Prompts — Testing

## Prompt / instruction

Create meaningful tests for generation, Bronze contracts, Silver DQ detection, Gold aggregations, dashboard artifacts; run and fix failures.

## What AI produced

- `tests/test_data_generation.py`
- `tests/test_data_quality.py`
- `tests/test_gold_aggregations.py`
- `tests/dq_local.py`

## Validation

Command: `uv run --with pytest pytest tests/ -v`  
Result: **20 passed** (after Decimal fix for AOV)
