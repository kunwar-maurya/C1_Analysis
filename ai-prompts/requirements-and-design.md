# AI Prompts — Requirements and Design

## Prompt / instruction

Build the full Databricks Medallion e-commerce pipeline per the detailed project requirements; start with requirements/design and continue autonomously.

## What AI produced

- `requirements-analysis.md`, `design-notes.md`, `data-model.md`, `data-quality-strategy.md`
- `tool-workflow/project-context.md`, `spec.md`, `task-breakdown.md`
- Cursor rules under `.cursor/rules/`
- Ambiguity log with documented assumptions (Gold Completed-only; segmentation thresholds; duplicate semantics)

## Decisions accepted

- Completed-only eligible orders for Gold revenue  
- Revenue-based segmentation thresholds  
- Extra duplicate rows (not in-place mutation only)  
- Add `src/common/` and `config/` beyond baseline structure  

## Modified / rejected

- Rejected silent deletion of bad records  
- Rejected hard-coded Windows paths in runtime code  

## Validation

Planning files exist; terminology matches requirements sections 5–11, 15–20.
