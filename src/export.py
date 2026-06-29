from __future__ import annotations

import json
from pathlib import Path

from src.models import (
    Evidence,
    GapFinding,
    Hypothesis,
    ResearchProject,
    ResearchQuestion,
    Source,
)


def export_json(
    path: Path,
    project: ResearchProject,
    sources: list[Source],
    evidence: list[Evidence],
    gaps: list[GapFinding],
    questions: list[ResearchQuestion],
    hypotheses: list[Hypothesis],
) -> Path:
    payload = {
        "project": project.model_dump(mode="json"),
        "sources": [item.model_dump(mode="json") for item in sources],
        "evidence": [item.model_dump(mode="json") for item in evidence],
        "gaps": [item.model_dump(mode="json") for item in gaps],
        "questions": [item.model_dump(mode="json") for item in questions],
        "hypotheses": [item.model_dump(mode="json") for item in hypotheses],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def export_markdown(
    path: Path,
    project: ResearchProject,
    sources: list[Source],
    evidence: list[Evidence],
    gaps: list[GapFinding],
    questions: list[ResearchQuestion],
    hypotheses: list[Hypothesis],
) -> Path:
    lines = [
        f"# Research Hypothesis Builder Report: {project.specific_topic}",
        "",
        "## Project Intake Summary",
        f"- Branch of science: {project.branch_of_science}",
        f"- Topic: {project.specific_topic}",
        f"- Research problem: {project.research_problem}",
        f"- Goal: {project.goal}",
        f"- Available data: {project.available_data}",
        f"- Constraints: {project.constraints}",
        f"- Novelty preference: {project.novelty_level}",
        f"- Output style: {project.output_style}",
        "",
        "## Uploaded Sources",
    ]
    lines.extend(
        f"- {source.filename} ({source.file_type}) [{source.processed_status}]"
        for source in sources
    )
    lines.extend(["", "## Evidence Summary"])
    lines.extend(
        f"- [{item.evidence_type}] {item.text[:160]} (Provenance: {item.provenance})"
        for item in evidence
    )
    lines.extend(["", "## Gap Findings"])
    lines.extend(f"- {gap.title}: {gap.description}" for gap in gaps)
    lines.extend(["", "## Research Questions"])
    lines.extend(f"- {question.question}" for question in questions)
    lines.extend(["", "## Ranked Hypotheses"])
    lines.extend(
        f"- {hypothesis.title}: {hypothesis.hypothesis} "
        f"(confidence {hypothesis.confidence_score:.2f}, novelty {hypothesis.novelty_score:.2f}, testability {hypothesis.testability_score:.2f})"
        for hypothesis in hypotheses
    )
    lines.extend(["", "## Proposed Experiments"])
    lines.extend(
        f"- {hypothesis.title}: {hypothesis.proposed_experiment}"
        for hypothesis in hypotheses
    )
    lines.extend(["", "## Limitations"])
    limitations = [item for item in evidence if item.evidence_type == "limitation"]
    if limitations:
        lines.extend(f"- {item.text[:180]}" for item in limitations)
    else:
        lines.append("- No explicit limitations were extracted from the current evidence.")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
