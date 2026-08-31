# Reflection

## What went well

- Clear requirements enabled a structured Medallion design without inventing business rules.
- Exact DQ issue injection with automated post-generation validation prevented silent drift.
- Separating local CSV validation from Databricks Spark runtime kept honesty about what was actually executed.
- Config-driven paths avoided Windows path leakage into cluster code.

## Challenges

- Host Python was not on PATH; switched to `uv run` for generation and pytest.
- Floating-point AOV assertions required Decimal rounding.
- Duplicate-row ordering had to precede NULL injection to preserve exact issue counts.

## Design trade-offs

- Uniqueness failures flag **all** rows sharing a duplicated key (failure count ≥ 2× introduced duplicates).
- Gold filters to Completed + valid FKs so analytics stay trustworthy while Silver retains all bad rows.
- Segmentation is revenue-based (`lifetime_value_actual`), distinct from source `customer_segment`.

## AI-assisted development takeaways

- Planning artifacts first reduced rework.
- Validation-after-each-phase caught the float bug before final packaging.
- Documenting “NOT RUN on Databricks” is part of engineering integrity for this evaluation.
