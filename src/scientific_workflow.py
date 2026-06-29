from __future__ import annotations

from collections import Counter
from typing import Any

from src.models import Evidence, GapFinding, Hypothesis, ResearchProject
from src.research_catalog import branch_names, discipline_names, subfield_names


BROAD_DOMAIN_ALIASES = {
    "physics": "Physics",
    "biology": "Biology",
    "chemistry": "Chemistry",
    "engineering": "Engineering",
    "medicine": "Medicine and health",
    "health": "Medicine and health",
    "computer science": "Computer and information science",
    "ai": "Computer and information science",
    "climate": "Earth and environmental science",
    "environment": "Earth and environmental science",
    "math": "Mathematics",
    "mathematics": "Mathematics",
}


def clarify_domain(domain: str, subfield: str, goal: str) -> dict[str, Any]:
    normalized = _match_branch(domain)
    needs_clarification = not subfield.strip() or domain.strip().lower() in BROAD_DOMAIN_ALIASES
    if normalized:
        suggested_subfields = [
            f"{discipline}: {', '.join(subfield_names(normalized, discipline)[:3])}"
            for discipline in discipline_names(normalized)
        ]
    else:
        suggested_subfields = [
            f"{domain} mechanisms",
            f"{domain} measurement",
            f"{domain} modeling",
            f"{domain} intervention design",
        ]

    topic = subfield or domain or "the selected domain"
    return {
        "needs_clarification": needs_clarification,
        "suggested_subfields": suggested_subfields[:8],
        "feasible_research_directions": [
            f"Map the major variables and mechanisms in {topic}.",
            f"Compare competing methods or explanations in {topic}.",
            f"Identify under-tested conditions relevant to {goal or 'the research goal'}.",
            f"Design a small validation study with measurable outcomes.",
        ],
        "recommended_search_terms": [
            f"{topic} review",
            f"{topic} benchmark",
            f"{topic} experimental evidence",
            f"{topic} simulation study",
            f"{topic} limitations open questions",
        ],
        "possible_dataset_types": [
            "experimental measurements",
            "observational tables",
            "simulation outputs",
            "time-series records",
            "benchmark datasets",
        ],
        "clarifying_questions": [
            "Which subfield or mechanism matters most?",
            "What outcome or dependent variable should improve or change?",
            "Are you using papers, data, or both?",
            "What constraints limit validation?",
            "What would count as a useful negative result?",
        ],
    }


def plan_literature(domain: str, subfield: str, goal: str) -> dict[str, list[str]]:
    topic = subfield or domain
    return {
        "review_paper_search_terms": [
            f"{topic} systematic review",
            f"{topic} recent advances",
            f"{topic} open challenges",
        ],
        "recent_paper_search_terms": [
            f"{topic} 2024 2025 experimental",
            f"{topic} recent dataset",
            f"{topic} mechanism validation",
        ],
        "benchmark_terms": [
            f"{topic} benchmark",
            f"{topic} reproducibility",
            f"{topic} simulation comparison",
        ],
        "paper_types_to_collect": [
            "recent review or tutorial paper",
            "2-4 primary experimental or observational studies",
            "benchmark, dataset, or simulation paper",
            "paper that reports limitations or contradictory findings",
        ],
        "information_to_extract": [
            "main variables and entities",
            "methods and measurement conditions",
            "datasets, samples, or simulation setup",
            "key findings with evidence snippets",
            "limitations, contradictions, and open questions",
            f"claims directly relevant to {goal or 'the research goal'}",
        ],
    }


def generic_evidence_summary(
    project: ResearchProject, evidence_list: list[Evidence]
) -> dict[str, Any]:
    variables = sorted({variable for item in evidence_list for variable in item.variables})
    methods = [item.text for item in evidence_list if item.evidence_type == "method"][:5]
    limitations = [item.text for item in evidence_list if item.evidence_type == "limitation"][:5]
    findings = [
        {
            "claim": item.text,
            "variables_involved": item.variables,
            "relationship": "reported association or observation",
            "conditions": "; ".join(item.conditions),
            "evidence_snippet": item.text[:220],
            "confidence": _confidence_label(item.confidence),
        }
        for item in evidence_list
        if item.evidence_type in {"claim", "result", "dataset_summary", "observation"}
    ][:10]
    return {
        "paper_title": "Uploaded sources",
        "field": project.branch_of_science,
        "subfield": project.specific_topic,
        "entities": variables[:8],
        "variables": variables[:12],
        "methods": methods,
        "datasets_or_samples": [
            item.text for item in evidence_list if item.evidence_type == "dataset_summary"
        ][:5],
        "key_findings": findings,
        "limitations": limitations,
        "contradictions": detect_text_contradictions(evidence_list),
        "open_questions": [
            "Which findings replicate across independent sources?",
            "Which variables are missing from the uploaded evidence?",
            "Which proposed mechanism has enough support to test?",
        ],
    }


def detect_knowledge_gaps(
    project: ResearchProject,
    evidence_list: list[Evidence],
    dataset_profiles: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    variable_counts = Counter(variable for item in evidence_list for variable in item.variables)
    literature_variables = set(variable_counts)
    dataset_variables = {
        column
        for profile in dataset_profiles
        for column in profile.get("columns", [])
    }
    gaps: list[dict[str, Any]] = []

    for item in evidence_list:
        if item.evidence_type == "limitation":
            gaps.append(
                {
                    "Gap": "Reported limitation needs validation",
                    "Evidence": item.text[:180],
                    "Missing information": "Independent test, stronger sample, or missing control",
                    "Why it matters": "Limitations mark places where a hypothesis may fail or become more precise.",
                    "Possible hypothesis direction": f"Test whether the limitation changes outcomes for {project.specific_topic}.",
                    "Confidence": "medium",
                }
            )

    missing_in_dataset = sorted(literature_variables - dataset_variables)[:5]
    if missing_in_dataset and dataset_profiles:
        gaps.append(
            {
                "Gap": "Literature variables missing from dataset",
                "Evidence": ", ".join(missing_in_dataset),
                "Missing information": "Dataset columns or derived features for these variables",
                "Why it matters": "A hypothesis cannot be tested directly if core variables are absent.",
                "Possible hypothesis direction": "Add or derive missing variables before validation.",
                "Confidence": "high",
            }
        )

    for profile in dataset_profiles:
        relationships = profile.get("simple_relationships", [])
        if relationships:
            top = relationships[0]
            gaps.append(
                {
                    "Gap": "Dataset pattern needs mechanistic explanation",
                    "Evidence": f"{top['variables']} relationship strength {top['strength']}",
                    "Missing information": "Causal mechanism, controls, and replication",
                    "Why it matters": "A strong pattern can inspire a testable hypothesis but does not prove causality.",
                    "Possible hypothesis direction": "Test whether the relationship persists after controls or perturbation.",
                    "Confidence": "medium",
                }
            )

    if not gaps:
        gaps.append(
            {
                "Gap": "Insufficient evidence for specific hypothesis generation",
                "Evidence": "Few uploaded evidence records or dataset patterns are available.",
                "Missing information": "More papers, data, variables, or constraints",
                "Why it matters": "Broad domains need narrowing before useful hypotheses are generated.",
                "Possible hypothesis direction": "Use domain clarification and literature planning first.",
                "Confidence": "high",
            }
        )
    return gaps[:8]


def critique_hypotheses(
    hypotheses: list[Hypothesis], dataset_profiles: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    has_dataset = bool(dataset_profiles)
    critiques = []
    for hypothesis in hypotheses:
        critiques.append(
            {
                "Hypothesis": hypothesis.title,
                "Unsupported assumptions": "; ".join(hypothesis.assumptions[:2])
                or "Assumptions should be made explicit before validation.",
                "Causality overclaims": "Treat the hypothesis as a testable possibility, not a proven causal claim.",
                "Missing controls": "Add baseline, negative control, and at least one robustness condition.",
                "Confounders": "Measurement bias, sample selection, hidden covariates, and domain-specific constraints.",
                "Data limitations": "Dataset support is available." if has_dataset else "No uploaded dataset has been profiled yet.",
                "Novelty concerns": "Check whether the hypothesis restates a known conclusion from one source.",
                "Feasibility issues": "Confirm the variables can be measured with available time and tools.",
                "Alternative explanations": "A correlated variable or unmeasured mechanism may explain the same pattern.",
                "Suggested improvements": "Narrow variables, define controls, and pre-register falsification criteria.",
            }
        )
    return critiques


def score_hypotheses(
    hypotheses: list[Hypothesis], dataset_profiles: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    has_dataset = bool(dataset_profiles)
    rows = []
    for hypothesis in hypotheses:
        support_count = len(hypothesis.supporting_evidence_ids)
        rows.append(
            {
                "Hypothesis": hypothesis.title,
                "Novelty": _score(hypothesis.novelty_score),
                "Plausibility": _score(hypothesis.confidence_score),
                "Testability": _score(hypothesis.testability_score),
                "Feasibility": _score(hypothesis.testability_score * 0.9 + 0.1),
                "Data availability": 4 if has_dataset else max(1, min(3, support_count + 1)),
                "Scientific impact": 4 if hypothesis.hypothesis_type in {"mechanistic", "translational"} else 3,
                "Risk of confounding": 2 if hypothesis.conflicting_evidence_ids else 3,
            }
        )
    for row in rows:
        row["Total"] = sum(value for key, value in row.items() if key != "Hypothesis")
    return sorted(rows, key=lambda item: item["Total"], reverse=True)


def build_validation_plan(hypotheses: list[Hypothesis]) -> list[dict[str, str]]:
    return [
        {
            "Hypothesis": hypothesis.title,
            "Validation test": hypothesis.proposed_experiment,
            "Primary outcome": hypothesis.predicted_outcome,
            "Falsification": hypothesis.falsification_criteria,
            "Controls": "Baseline condition, negative control, and sensitivity check",
        }
        for hypothesis in hypotheses
    ]


def _match_branch(domain: str) -> str | None:
    normalized = domain.strip().lower()
    if normalized in BROAD_DOMAIN_ALIASES:
        return BROAD_DOMAIN_ALIASES[normalized]
    for branch in branch_names():
        if branch.lower() == normalized:
            return branch
    return None


def _confidence_label(confidence: float) -> str:
    if confidence >= 0.7:
        return "high"
    if confidence >= 0.45:
        return "medium"
    return "low"


def _score(value: float) -> int:
    return max(1, min(5, round(value * 5)))


def detect_text_contradictions(evidence_list: list[Evidence]) -> list[str]:
    positive = [item.text for item in evidence_list if "increase" in item.text.lower()]
    negative = [item.text for item in evidence_list if "decrease" in item.text.lower()]
    if positive and negative:
        return [
            "Some uploaded evidence uses both increase and decrease language; inspect whether these refer to the same variables and conditions."
        ]
    return []
