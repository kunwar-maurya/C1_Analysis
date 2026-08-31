# Requirements Analysis

## Source of Truth

Project requirements provided in the initial specification (Sections 1–34). No invented business requirements.

## Ambiguities Identified

| ID | Ambiguity | Decision | Documented In |
|----|-----------|----------|---------------|
| AMB-01 | Whether cancelled/pending orders count in Gold revenue | Include only `Completed` orders | design-notes.md, data-model.md |
| AMB-02 | How customer segmentation is calculated | Thresholds on `lifetime_value_actual` (High/Medium/Low/Unknown) | design-notes.md, Gold SQL comments |
| AMB-03 | Meaning of "10 duplicate customer_id records" | 10 extra rows that reuse existing IDs (total customers.csv rows = 10,010) | DATA_GENERATION_NOTES.md |
| AMB-04 | Meaning of "20 duplicate order_id records" | 20 extra rows reusing existing order_ids (total orders.csv rows = 100,020) | DATA_GENERATION_NOTES.md |
| AMB-05 | Gold file `03_daily_weekly_trends.sql` required in structure but not listed in Gold 1–3 | Include as additional Gold trend dataset | design-notes.md |
| AMB-06 | Local Spark availability for full Bronze/Silver/Gold execution | Provide Databricks-ready code; run generation + pytest locally; document Databricks-required steps | README, final validation |
| AMB-07 | Exact business rule for `total_amount` vs quantity×unit_price | Expect equality within 0.01; flag mismatches | data-quality-strategy.md |
| AMB-08 | `lifetime_value` on customers vs computed `lifetime_value_actual` | Keep source LTV as attribute; Gold computes actual from completed orders | data-model.md |
| AMB-09 | Preferred Databricks landing storage when not specified as FileStore vs Volumes | Unity Catalog Volumes (`/Volumes/<catalog>/<schema>/<volume>/raw_data`); placeholder if Volume not yet created — never default to FileStore/DBFS | design-notes.md, config/, setup-notes |

## Requirement Themes

1. Medallion pipeline on Databricks
2. Exact intentional DQ issues + detection
3. Flag, don't delete
4. Configurable paths
5. Dashboard SQL
6. Tests + honest validation
7. AI-assisted workflow documentation
8. Full docs + traceability

## Out of Scope (Explicit)

- External cloud object storage SDKs
- Inventing additional dashboards beyond minimum + useful trends
- Claiming Databricks success without execution
