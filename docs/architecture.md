# Architecture

## Goal

This MVP supports a simple local workflow:

research intake + uploaded files + notes -> extracted evidence -> gaps -> research questions -> hypotheses -> export

## Components

### Intake

`app.py` collects the research brief and stores it as a `ResearchProject`.

### Upload

Uploaded files are written to `data/uploads/` and tracked as `Source` records in SQLite.

### Ingestion

`src/ingestion.py` handles local parsing:

- PDF with PyMuPDF
- TXT with direct text reads
- CSV/XLSX with pandas summaries
- PNG/JPG with Pillow metadata

Processed summaries are written to `data/processed/` and stored as `ParsedContent`.

### Evidence Extraction

The MVP uses a conservative fallback extractor that:

- splits content into paragraphs
- labels likely evidence types using keywords
- attaches provenance to every evidence item
- avoids inventing unsupported facts

### Retrieval

`src/retrieval.py` builds a local TF-IDF index per project and supports evidence search from the UI.

### Gap Finding

`src/synthesis.py` creates gap findings from:

- explicit limitations
- low-confidence evidence
- variables that appear only once

### Hypothesis Generation

The same synthesis layer creates:

- research questions grounded in the intake and gap findings
- testable hypotheses with supporting and conflicting evidence links
- multiple distinct hypothesis lenses, including mechanistic, comparative, optimization, robustness, and translational
- proposed experiments, predicted outcomes, and falsification criteria
- synthetic simulation summaries for early planning support

### Brainstorming Studio

The multipage Streamlit setup adds a dedicated brainstorming page for early-stage ideation.

It provides:

- research area dropdowns
- topic suggestion menus
- question-framing lenses
- lighter-input idea generation
- optional live resource lookup from arXiv and Crossref
- synthetic scenario simulations to compare directions

### Ranking

`src/ranking.py` ranks hypotheses using:

- amount of supporting evidence
- confidence
- testability
- novelty alignment with user preference

### Export

`src/export.py` writes:

- JSON snapshots for structured reuse
- Markdown reports for easy reading and sharing

## Storage Model

SQLite stores JSON payloads for the main record types:

- `ResearchProject`
- `Source`
- `ParsedContent`
- `Evidence`
- `GapFinding`
- `ResearchQuestion`
- `Hypothesis`

This keeps the schema flexible for a first MVP while still using structured storage.

## Design Principles

- Local-first
- End-to-end without external services
- Friendly nontechnical workflow
- Clear provenance for uploaded evidence
- Simple code paths over heavy abstraction
