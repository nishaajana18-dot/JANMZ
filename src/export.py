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
    domain_clarification: dict | None = None,
    literature_plan: dict | None = None,
    dataset_profiles: list[dict] | None = None,
    structured_gaps: list[dict] | None = None,
    critique: list[dict] | None = None,
    ranking: list[dict] | None = None,
    validation_plan: list[dict] | None = None,
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
        f"- Project mode: {project.project_mode}",
        f"- User level: {project.user_level}",
        f"- Time constraint: {project.time_constraint}",
        f"- Novelty preference: {project.novelty_level}",
        f"- Output style: {project.output_style}",
        "",
    ]
    if domain_clarification:
        lines.extend(["## Domain Clarification"])
        for key, value in domain_clarification.items():
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        lines.append("")
    if literature_plan:
        lines.extend(["## Literature Search Plan"])
        for key, value in literature_plan.items():
            lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        lines.append("")
    lines.append("## Uploaded Sources")
    lines.extend(
        f"- {source.filename} ({source.file_type}) [{source.processed_status}]"
        for source in sources
    )
    if dataset_profiles:
        lines.extend(["", "## Dataset Profile"])
        for index, profile in enumerate(dataset_profiles, start=1):
            lines.append(
                f"- Dataset {index}: {profile['shape']['rows']} rows x {profile['shape']['columns']} columns; "
                f"type {profile['inferred_dataset_type']}; recommended analyses: {', '.join(profile['recommended_analyses'])}"
            )
    lines.extend(["", "## Evidence Summary"])
    lines.extend(
        f"- [{item.evidence_type}] {item.text[:160]} (Provenance: {item.provenance})"
        for item in evidence
    )
    lines.extend(["", "## Gap Findings"])
    lines.extend(f"- {gap.title}: {gap.description}" for gap in gaps)
    if structured_gaps:
        lines.extend(["", "## Knowledge Gap Table"])
        for gap in structured_gaps:
            lines.append(
                f"- {gap['Gap']}: {gap['Why it matters']} Direction: {gap['Possible hypothesis direction']}"
            )
    lines.extend(["", "## Research Questions"])
    lines.extend(f"- {question.question}" for question in questions)
    lines.extend(["", "## Ranked Hypotheses"])
    lines.extend(
        f"- {hypothesis.title} [{hypothesis.hypothesis_type}]: {hypothesis.hypothesis} "
        f"(confidence {hypothesis.confidence_score:.2f}, novelty {hypothesis.novelty_score:.2f}, testability {hypothesis.testability_score:.2f}; "
        f"variables: {', '.join(hypothesis.variables_involved) or 'needs review'})"
        for hypothesis in hypotheses
    )
    if ranking:
        lines.extend(["", "## Ranking Scores"])
        for row in ranking:
            lines.append(f"- {row['Hypothesis']}: total {row['Total']}")
    if critique:
        lines.extend(["", "## Scientific Critique"])
        for row in critique:
            lines.append(
                f"- {row['Hypothesis']}: {row['Causality overclaims']} Suggested improvement: {row['Suggested improvements']}"
            )
    if validation_plan:
        lines.extend(["", "## Validation Plan"])
        for row in validation_plan:
            lines.append(f"- {row['Hypothesis']}: {row['Validation test']}")
    lines.extend(["", "## Proposed Experiments"])
    lines.extend(
        f"- {hypothesis.title}: {hypothesis.proposed_experiment}"
        for hypothesis in hypotheses
    )
    lines.extend(["", "## Simulation Notes"])
    lines.extend(
        f"- {hypothesis.title}: {hypothesis.simulation_summary or 'No simulation summary available.'}"
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
