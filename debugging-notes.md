# Debugging Notes

## DBG-001 — Python launcher missing on PATH

**Problem:** `python` / `py` invoke Windows Store stubs; command failed with exit 9009.  
**Root cause:** No traditional Python on PATH; `uv` is available.  
**Fix:** Run generation and tests via `uv run --with pytest python ...`.  
**Validation:** Data generation completed with exact DQ counts; pytest executed.

## DBG-002 — Duplicate rows inflated intentional NULL counts (caught in design)

**Problem:** If duplicates are created *after* NULL/orphan injection by copying mutated rows, NULL/orphan counts exceed the required exact values.  
**Root cause:** Order of operations in issue injection.  
**Fix:** Create duplicate PK rows first from clean data; then apply NULL/orphan mutations only to the original base row index ranges.  
**Validation:** Post-generation `validate_generated()` asserts exact expected counts — passed.

## DBG-003 — Floating-point avg_order_value assertion

**Problem:** `test_avg_order_value_math` failed (`878.28 == 878.27`) due to binary float rounding.  
**Root cause:** Computing AOV with Python `float` / `round`.  
**Fix:** Use `Decimal` with `ROUND_HALF_UP` in local Gold helper and test.  
**Validation:** Re-run pytest (see latest results in final validation).

## DBG-005 — Prefer Unity Catalog Volumes over FileStore

**Problem:** Default/recommended raw path used `/FileStore/...`, which is not the preferred Databricks storage approach for this project.  
**Root cause:** Initial config/docs used FileStore as a convenient example.  
**Fix:** Set `raw_data_path` to `/Volumes/ecommerce/landing/raw_files/raw_data` (placeholder UC Volume pattern), document Volume setup, remove FileStore/DBFS as recommended defaults across docs/config/rules/tests.  
**Validation:** Repo-wide search for FileStore/DBFS defaults + pytest storage-path tests.
