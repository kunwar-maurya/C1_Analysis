# Task Breakdown

## Phase 1: Requirements & Architecture

**Objective:** Capture requirements, architecture, data model, quality strategy, Cursor rules.

**Tasks:**
- Analyze requirements; document ambiguities/assumptions
- Write project-context, spec, design notes, data model, DQ strategy
- Create Cursor rules
- Create requirements traceability matrix skeleton

**Outputs:** Planning markdown files, `.cursor/rules/`, structure dirs

**Validation:** All required planning files exist; terminology matches requirements

**Dependencies:** None

---

## Phase 2: Data Generation

**Objective:** Produce CSVs with exact intentional DQ issues.

**Tasks:**
- Implement `generate_sample_data.py`
- Write generation notes
- Auto-validate issue counts post-generation

**Outputs:** `data/*.csv`, generation notes, generation validation report

**Validation:** Row counts + exact DQ counts match FR-DQ

**Dependencies:** Phase 1

---

## Phase 3: Bronze

**Objective:** Raw CSV → Delta with metadata.

**Tasks:**
- Common config/helpers
- Per-entity ingest scripts + `ingest_all.py`
- Schema SQL / setup notes
- Bronze validation utilities

**Outputs:** `src/bronze/*`, `database/*`, config

**Validation:** Schemas, row counts, metadata fields (code + local dry-run where possible)

**Dependencies:** Phase 2

---

## Phase 4: Silver

**Objective:** Quality framework with flags and metrics.

**Tasks:**
- Completeness, uniqueness, type, RI, business-logic modules
- `create_silver_tables.py`
- Quality metrics aggregation

**Outputs:** `src/silver/*`, quality strategy alignment

**Validation:** Detect intentional issues; flags present; pass % calculated

**Dependencies:** Phase 3

---

## Phase 5: Gold

**Objective:** Analytical aggregations.

**Tasks:**
- SQL for sales by product, revenue by customer, trends, segmentation
- `create_gold_tables.py`
- Document calculation rules

**Outputs:** `src/gold/*`

**Validation:** Columns present; sample math checks in tests

**Dependencies:** Phase 4

---

## Phase 6: Dashboard

**Objective:** Databricks SQL dashboard queries + guide.

**Tasks:**
- `dashboard_queries.sql`
- `DASHBOARD_GUIDE.md`

**Outputs:** Dashboard artifacts

**Validation:** SQL parses / references Gold tables; guide complete

**Dependencies:** Phase 5

---

## Phase 7: Testing

**Objective:** Meaningful automated tests.

**Tasks:**
- test_data_generation, test_data_quality, test_gold_aggregations
- Run tests locally where possible

**Outputs:** `tests/*`, test results documented

**Validation:** Tests executed; failures fixed or documented

**Dependencies:** Phases 2–6

---

## Phase 8: Debugging & Refinement

**Objective:** Fix failures; document root causes.

**Tasks:**
- Capture errors; fix; re-validate
- Update `debugging-notes.md`

**Outputs:** Fixes + debugging notes

**Validation:** Previously failing checks pass or gaps documented

**Dependencies:** Phase 7

---

## Phase 9: Documentation

**Objective:** Complete engineer-facing docs and AI prompt history.

**Tasks:**
- README, reflection, final-ai-usage-summary, candidate-info
- ai-prompts/* for actual work
- Complete traceability matrix

**Outputs:** Documentation suite

**Validation:** Docs cover setup, execution, assumptions, limitations

**Dependencies:** Phases 1–8

---

## Phase 10: Final Validation

**Objective:** Requirement audit.

**Tasks:**
- End-to-end checklist: Expected vs Actual vs Status vs Evidence
- Identify remaining gaps

**Outputs:** Final validation section (README and/or dedicated file)

**Validation:** Honest status; no false completion claims

**Dependencies:** All prior phases
