# Research Hypothesis Builder

Research Hypothesis Builder is a simple local MVP for turning research intake, uploaded files, and notes into structured evidence, gap findings, research questions, and ranked testable hypotheses.

The app is designed for nontechnical researchers and runs end to end even if no OpenAI API key is available. In fallback mode it uses local parsing, keyword-based evidence extraction, gap generation heuristics, and TF-IDF search over extracted evidence.

## What the app does

- Collects a research intake brief.
- Stores uploaded PDF, TXT, CSV, XLSX, PNG, and JPG files locally.
- Ingests files into extracted text or dataset summaries.
- Converts parsed content into evidence records with provenance.
- Lets you search evidence through a local index.
- Identifies evidence gaps.
- Generates research questions and testable hypotheses.
- Produces more diverse hypothesis types such as mechanistic, comparative, optimization, robustness, and translational ideas.
- Includes a Brainstorming Studio tab for early-stage idea exploration with lighter input needs.
- Uses a cascading field selector that narrows from broad science field to branch, subfield, topic, and possible question.
- Optionally pulls live inspiration links from arXiv and Crossref when internet access is available.
- Adds clearly labeled synthetic simulation notes to help compare early research directions.
- Ranks hypotheses and supports human review notes.
- Exports the full project as JSON or Markdown.
- Includes a synthetic demo mode for immediate testing.

## Installation

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell use:

```powershell
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

## Run the app

```bash
streamlit run app.py
```

The app opens as one tabbed workspace:

- `Project Workflow`
- `Brainstorming Studio`

## Add an OpenAI API key

1. Copy `.env.example` to `.env`.
2. Add your `OPENAI_API_KEY`.

The current MVP is built to run without an API key. If you add one later, the codebase is structured so model-based extraction and embeddings can be layered in without changing the UI flow.

## How to use demo mode

- Open the app.
- Click `Load Demo Project` in the sidebar.
- Explore synthetic evidence, gaps, questions, and hypotheses.

The demo data is intentionally synthetic and clearly separated from uploaded material.

## Pipeline overview

1. Research intake creates a `ResearchProject`.
2. File uploads create `Source` records and store files under `data/uploads/`.
3. Ingestion parses each file and writes processed summaries under `data/processed/`.
4. Evidence extraction creates structured `Evidence` records with provenance.
5. Retrieval builds a local TF-IDF evidence index.
6. Gap finding turns limitations and sparse evidence into `GapFinding` records.
7. Question generation produces `ResearchQuestion` records.
8. Hypothesis generation produces draft `Hypothesis` records.
9. Brainstorming Studio can generate lighter-weight research ideas before file-heavy intake in the same app.
10. Ranking orders hypotheses for review.
11. Export writes JSON and Markdown reports.

## Run tests

```bash
pytest
```

## Current limitations

- OpenAI-backed extraction and embeddings are not yet wired into the MVP flow.
- Image understanding is metadata-only for now.
- Evidence extraction is intentionally conservative and rule-based in fallback mode.
- The app uses a single active project workflow to keep the first version simple.
- Live resource lookup depends on internet availability and currently uses lightweight arXiv and Crossref queries rather than a full literature review pipeline.
- Synthetic simulations are for planning support only and are not substitutes for empirical validation.

## Future improvements

- Add OpenAI structured extraction and embeddings when an API key is present.
- Support multiple active projects in the UI.
- Add richer provenance display by page number or sheet name.
- Improve hypothesis editing and comparison workflows.
- Add stronger contradiction detection and experiment templates.
- Add user controls for simulation assumptions and effect-size ranges.
