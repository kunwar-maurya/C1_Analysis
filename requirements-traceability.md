# Requirements Traceability Matrix

| Requirement | Implementation Artifact | Test / Validation | Evidence / Documentation |
|-------------|-------------------------|-------------------|--------------------------|
| FR-01 Generate customers/orders/products | `src/data_generation/generate_sample_data.py` | `tests/test_data_generation.py` | `data/*.csv`, DATA_GENERATION_NOTES.md |
| FR-02 Exact intentional DQ issues | issue injection in generator + `validate_generated()` | test_intentional_* | `data/quality_validation_report.json` |
| FR-03 Bronze ingest to Delta + metadata | `src/bronze/*`, `src/common/spark_utils.py` | `test_bronze_artifact_contracts` | design-notes.md; Databricks execution pending |
| FR-04 Silver quality dimensions | `src/silver/01`–`05_*.py` | `tests/test_data_quality.py` | data-quality-strategy.md |
| FR-05 Flag bad records (no silent delete) | `create_silver_tables.py` (`dq_*` columns) | `test_bad_records_are_flagged_not_removed`, `test_silver_modules_exist_and_flag_not_delete` | data-quality-strategy.md |
| FR-06 Quality metrics + pass % | `silver.quality_metrics` writer + local mirror | `test_pass_percentage_math` | quality_validation_report.json |
| FR-07 Gold datasets | `src/gold/*.sql`, `create_gold_tables.py` | `tests/test_gold_aggregations.py` | design-notes.md calculation rules |
| FR-08 Dashboard SQL | `src/dashboard/dashboard_queries.sql` | `test_dashboard_queries_present` | DASHBOARD_GUIDE.md |
| FR-09 Tests | `tests/*` | pytest 20 passed (local) | debugging-notes.md, final validation |
| FR-10 Documentation + traceability | README + planning docs + this matrix | Final validation checklist | reflection.md |
| Configurable paths / UC Volumes (no Windows/FileStore/DBFS defaults) | `config/pipeline_config.json`, `src/common/config.py` | `test_config_prefers_unity_catalog_volume_path`, `test_docs_do_not_recommend_filestore_or_dbfs` | CONFIG_NOTES.md, setup-notes.md |
| Databricks compatibility | PySpark Bronze/Silver/Gold | Code review; runtime NOT executed here | database/setup-notes.md |
| Cursor rules | `.cursor/rules/*.mdc` | File presence | tool-workflow/cursor-rules-or-instructions.md |
| AI workflow docs | `ai-prompts/*` | Content review | final-ai-usage-summary.md |
| Candidate info | `candidate-info.md` | Placeholders only | candidate-info.md |
