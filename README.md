# General AI Co-Scientist

General AI Co-Scientist is a local, domain-agnostic Streamlit app for turning scientific domains, papers, datasets, and notes into structured evidence, knowledge gaps, ranked hypotheses, critique, validation plans, and reports.

The app is designed for nontechnical researchers and student demos. It runs end to end without an OpenAI API key by using local parsing, rule-based evidence extraction, dataset profiling, TF-IDF retrieval, deterministic gap detection, and cautious hypothesis generation.

## What The App Does

- Clarifies broad domains before hypothesis generation.
- Guides users through a cascading science tree from field to branch, subfield, topic, and possible question.
- Produces literature collection plans and extraction targets.
- Stores uploaded PDF, TXT, CSV, XLSX, PNG, and JPG files locally.
- Chunks long PDFs and stores extraction metadata.
- Profiles datasets without assuming a medical or single-domain schema.
- Recommends analyses such as correlation, regression, classification, clustering, dimensionality reduction, time-series analysis, simulation comparison, and ablation studies.
- Extracts evidence with provenance.
- Detects gaps across literature evidence, dataset variables, limitations, missing variables, and dataset patterns.
- Generates cautious, falsifiable hypothesis cards.
- Adds scientific critique, transparent ranking, and validation plans.
- Exports JSON and Markdown reports.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run The App

```bash
streamlit run app.py
```

The app opens as one tabbed workspace:

- `Project Workflow`
- `Brainstorming Studio`

## OpenAI API Key

The current app works without an API key. API keys are read from environment variables or Streamlit secrets, never from source code.

For local development, copy `.env.example` to `.env` and set `OPENAI_API_KEY`.

For Streamlit Cloud, set `OPENAI_API_KEY` in the app secrets panel. Do not commit `.streamlit/secrets.toml`.

## Pipeline

1. Landing page explains the scientific workflow.
2. Domain clarification suggests subfields, directions, search terms, dataset types, and clarifying questions.
3. Literature planning suggests paper types and information to extract.
4. Research intake creates a `ResearchProject`.
5. File uploads create `Source` records under `data/uploads/`.
6. Ingestion parses files and stores processed summaries under `data/processed/`.
7. Dataset profiling summarizes columns, missingness, variable types, targets, predictors, relationships, and recommended analyses.
8. Evidence extraction creates structured `Evidence` records with provenance.
9. Retrieval builds a local TF-IDF evidence index.
10. Gap detection compares evidence, dataset variables, limitations, and patterns.
11. Question generation produces research questions.
12. Hypothesis generation produces draft hypotheses.
13. Scientific critique checks assumptions, controls, confounders, feasibility, and alternative explanations.
14. Ranking scores hypotheses on scientific criteria.
15. Export writes JSON and Markdown reports.

## Tests

```bash
python -m pytest
```

## Current Limitations

- OpenAI-backed extraction and embeddings are scaffolded but not yet wired into the main flow.
- Image understanding is metadata-only.
- Evidence extraction is conservative and rule-based in fallback mode.
- Live resource lookup depends on internet availability and uses lightweight arXiv and Crossref queries.
- Synthetic simulations are planning support only, not empirical validation.
- Markdown export is implemented first; PDF export is a TODO.

## Future Improvements

- Add model-backed extraction, synthesis, and critique behind the existing prompt templates.
- Add PDF report export.
- Support multiple active projects.
- Add richer page-level PDF provenance.
- Add user-adjustable simulation assumptions and effect-size ranges.
