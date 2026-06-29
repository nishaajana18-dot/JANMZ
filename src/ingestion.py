from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
from PIL import Image

from src.config import settings
from src.models import Evidence, ParsedContent, Source

try:
    import fitz
except ImportError:  # pragma: no cover - depends on local environment
    fitz = None


def save_uploaded_file(project_id: str, uploaded_file) -> Path:
    safe_name = Path(uploaded_file.name).name
    target = settings.upload_dir / f"{project_id}_{safe_name}"
    target.write_bytes(uploaded_file.getbuffer())
    return target


def parse_source(project_id: str, source: Source) -> ParsedContent:
    raw_path = Path(source.raw_path)
    suffix = raw_path.suffix.lower()

    if suffix == ".pdf":
        text = extract_pdf_text(raw_path)
        metadata = {"pages": count_pdf_pages(raw_path)}
    elif suffix == ".txt":
        text = raw_path.read_text(encoding="utf-8", errors="ignore")
        metadata = {"characters": len(text)}
    elif suffix in {".csv", ".xlsx"}:
        text, metadata = summarize_tabular_file(raw_path)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        text, metadata = summarize_image(raw_path)
    else:
        text = "Unsupported file type for this MVP."
        metadata = {"supported": False}

    processed_path = settings.processed_dir / f"{source.id}.json"
    processed_payload = {"summary_text": text, "metadata": metadata}
    processed_path.write_text(json.dumps(processed_payload, indent=2), encoding="utf-8")

    return ParsedContent(
        project_id=project_id,
        source_id=source.id,
        summary_text=text,
        processed_path=str(processed_path),
        metadata=metadata,
    )


def extract_pdf_text(path: Path) -> str:
    if fitz is None:
        raise ImportError("PyMuPDF is required to ingest PDF files. Install it from requirements.txt.")
    with fitz.open(path) as document:
        pages = [page.get_text("text") for page in document]
    return "\n\n".join(page.strip() for page in pages if page.strip())


def count_pdf_pages(path: Path) -> int:
    if fitz is None:
        raise ImportError("PyMuPDF is required to ingest PDF files. Install it from requirements.txt.")
    with fitz.open(path) as document:
        return len(document)


def summarize_tabular_file(path: Path) -> tuple[str, dict]:
    df = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
    summary = {
        "rows": int(df.shape[0]),
        "columns": list(df.columns.astype(str)),
        "missing_values": df.isna().sum().to_dict(),
        "numeric_summary": df.describe(include="all").fillna("").to_dict(),
    }
    lines = [
        f"Dataset summary for {path.name}",
        f"Rows: {summary['rows']}",
        f"Columns: {', '.join(summary['columns']) or 'None'}",
        f"Missing values: {summary['missing_values']}",
        f"Descriptive statistics: {summary['numeric_summary']}",
    ]
    return "\n".join(lines), summary


def summarize_image(path: Path) -> tuple[str, dict]:
    with Image.open(path) as img:
        metadata = {"width": img.width, "height": img.height, "mode": img.mode}
    text = (
        f"Image metadata for {path.name}: {metadata}. "
        "Advanced image understanding is not enabled in this MVP."
    )
    return text, metadata


KEYWORD_MAP = {
    "limitation": ["limitation", "future work", "uncertain", "bias", "weakness"],
    "result": ["result", "improved", "increase", "decrease", "significant", "found"],
    "method": ["method", "protocol", "procedure", "measured", "assay"],
    "dataset_summary": ["dataset summary", "rows:", "columns:", "descriptive statistics"],
    "claim": ["suggest", "indicate", "show", "demonstrate", "hypothesis"],
}


def extract_evidence_fallback(project_id: str, source: Source, text: str) -> list[Evidence]:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]
    evidence_items: list[Evidence] = []

    for index, chunk in enumerate(chunks[:20], start=1):
        lower_chunk = chunk.lower()
        evidence_type = "observation"
        confidence = 0.35
        for candidate, keywords in KEYWORD_MAP.items():
            if any(keyword in lower_chunk for keyword in keywords):
                evidence_type = candidate
                confidence = 0.6 if candidate in {"result", "dataset_summary"} else 0.45
                break

        variables = sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9_-]{2,}\b", chunk)))[:5]
        conditions = sorted(
            set(
                re.findall(
                    r"\b(?:under|with|without|during|after|before)\s+[^.,;\n]{3,40}",
                    chunk,
                    re.I,
                )
            )
        )[:3]

        evidence_items.append(
            Evidence(
                project_id=project_id,
                source_id=source.id,
                evidence_type=evidence_type,
                text=chunk[:1200],
                variables=variables,
                conditions=conditions,
                confidence=confidence,
                provenance=f"{source.filename} paragraph {index}",
            )
        )

    if not evidence_items:
        evidence_items.append(
            Evidence(
                project_id=project_id,
                source_id=source.id,
                evidence_type="observation",
                text="No text could be extracted from this source.",
                confidence=0.1,
                provenance=f"{source.filename} extracted summary",
            )
        )

    return evidence_items
