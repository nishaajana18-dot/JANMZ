# Architecture

## Goal

This app supports a domain-agnostic scientific workflow:

domain clarification + papers/data + evidence extraction + dataset profiling -> gaps -> hypotheses -> critique -> validation plan -> report

## Main App

`app.py` is a single Streamlit application with two tabs:

- `Project Workflow`
- `Brainstorming Studio`

The first screen presents the app as `General AI Co-Scientist` and shows the workflow steps.

## Intake And Domain Clarification

`src/research_catalog.py` provides a broad science tree. Users select:

- broad field
- branch within field
- more specific area
- topic
- possible question

`src/scientific_workflow.py` adds domain clarification, feasible directions, search terms, possible dataset types, and clarifying questions.

## Literature Planning

`src/scientific_workflow.py` creates review paper search terms, recent paper terms, benchmark terms, paper types to collect, and information to extract.

## Upload And Ingestion

Uploaded files are written to `data/uploads/` and tracked as `Source` records in SQLite.

`src/ingestion.py` handles:

- PDF text extraction with PyMuPDF
- TXT reads
- CSV/XLSX dataset summaries
- PNG/JPG metadata
- PDF text chunking and local chunk summaries

Processed summaries are stored in `data/processed/` and SQLite as `ParsedContent`.

## Dataset Profiling

`src/dataset_profiler.py` profiles tabular data with:

- shape and columns
- missingness
- numeric and categorical columns
- candidate targets
- candidate predictors
- simple numeric relationships
- recommended analyses
- inferred dataset type

## Evidence

`src/ingestion.py` creates fallback evidence records from uploaded text. `src/scientific_workflow.py` can also summarize evidence into a generic schema with entities, variables, methods, datasets or samples, key findings, limitations, contradictions, and open questions.

## Gap Detection

`src/synthesis.py` creates fallback stored `GapFinding` records.

`src/scientific_workflow.py` creates a richer knowledge gap table by comparing:

- literature findings
- dataset variables
- dataset patterns
- contradictions
- missing variables
- limitations
- under-tested mechanisms

## Hypotheses

`src/synthesis.py` generates diverse hypothesis cards across mechanistic, comparative, optimization, robustness, and translational lenses.

Each hypothesis includes:

- statement
- variables
- literature support
- dataset support note
- assumptions
- possible confounders
- validation test
- predicted outcome
- falsification criteria
- novelty, testability, and confidence scores

## Critique, Ranking, And Validation

`src/scientific_workflow.py` adds:

- skeptical scientific critique
- transparent 1-5 ranking criteria
- validation plans for each hypothesis

## Prompt Templates And Model Routing

`src/prompts.py` defines prompt builders for future model-backed calls:

- domain clarification
- literature planning
- evidence extraction
- dataset analysis
- gap detection
- hypothesis generation
- scientific critique
- ranking
- report drafting

It also centralizes model routing so cheaper models can handle planning/formatting while stronger reasoning models handle gaps, hypotheses, and critique.

## Export

`src/export.py` writes:

- JSON snapshots
- Markdown reports with project inputs, clarification, literature plan, dataset profile, evidence, gaps, hypotheses, critique, validation plan, limitations, and next steps

PDF export is left as a future enhancement.
