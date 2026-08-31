# Cursor Rules / Instructions (Summary)

Canonical always-apply rules live in:

`.cursor/rules/databricks-medallion.mdc`

Additional focused rules:

- `.cursor/rules/python-pyspark.mdc`
- `.cursor/rules/documentation-honesty.mdc`

These enforce Databricks-first design, Unity Catalog Volume paths for raw data, configurable paths, no silent DQ deletion, validation before completion, and honest reporting of what was/wasn't executed.
