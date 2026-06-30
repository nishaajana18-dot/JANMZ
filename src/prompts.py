from __future__ import annotations

from src.config import settings


def get_model_routing():
    """Get model routing configuration dynamically."""
    cheap = getattr(settings, 'cheap_model', 'gpt-4o-mini')
    reasoning = getattr(settings, 'reasoning_model', 'gpt-4o')
    return {
        "domain_clarification": cheap,
        "literature_planning": cheap,
        "evidence_extraction": cheap,
        "dataset_analysis": cheap,
        "gap_detection": reasoning,
        "hypothesis_generation": reasoning,
        "scientific_critique": reasoning,
        "ranking": cheap,
        "report": cheap,
    }


MODEL_ROUTING = get_model_routing()


def build_domain_clarification_prompt(domain: str, goal: str) -> str:
    return _base_prompt(
        "Clarify the scientific domain before hypothesis generation.",
        f"Domain: {domain}\nResearch goal: {goal}",
        "Return JSON with suggested_subfields, feasible_directions, search_terms, dataset_types, clarifying_questions.",
    )


def build_literature_planning_prompt(domain: str, subfield: str, goal: str) -> str:
    return _base_prompt(
        "Create a literature review collection plan.",
        f"Domain: {domain}\nSubfield: {subfield}\nResearch goal: {goal}",
        "Return JSON with review_search_terms, recent_search_terms, benchmark_terms, paper_types_to_collect, extraction_targets.",
    )


def build_evidence_extraction_prompt(text: str) -> str:
    return _base_prompt(
        "Extract only evidence explicitly present in the supplied text.",
        text[:6000],
        "Return JSON matching the generic evidence schema. Do not invent citations, methods, or findings.",
    )


def build_dataset_analysis_prompt(profile_summary: str) -> str:
    return _base_prompt(
        "Analyze a dataset profile in a domain-agnostic way.",
        profile_summary,
        "Return JSON with candidate_targets, candidate_predictors, relationships, recommended_analyses, limitations.",
    )


def build_gap_detection_prompt(
    evidence_summary: str, dataset_summary: str, goal: str
) -> str:
    return _base_prompt(
        "Detect scientific knowledge gaps before proposing hypotheses.",
        f"Goal: {goal}\nEvidence:\n{evidence_summary}\nDataset:\n{dataset_summary}",
        "Return JSON rows with gap, evidence, missing_information, why_it_matters, possible_hypothesis_direction, confidence.",
    )


def build_hypothesis_generation_prompt(
    domain_summary: str, gaps: str, evidence_summary: str
) -> str:
    return _base_prompt(
        "Generate cautious, falsifiable, evidence-backed scientific hypotheses.",
        f"Domain:\n{domain_summary}\nGaps:\n{gaps}\nEvidence:\n{evidence_summary}",
        "Return 5-8 JSON cards with statement, variables, mechanism, support, assumptions, confounders, falsification, validation_test, feasibility, novelty.",
    )


def build_scientific_critique_prompt(hypotheses: str) -> str:
    return _base_prompt(
        "Act as a skeptical scientific reviewer.",
        hypotheses,
        "Return JSON critique for each hypothesis covering unsupported assumptions, causality overclaims, missing controls, confounders, data limitations, novelty concerns, feasibility issues, alternatives, improvements.",
    )


def build_ranking_prompt(hypotheses: str) -> str:
    return _base_prompt(
        "Rank hypotheses using transparent scientific criteria.",
        hypotheses,
        "Return JSON scores from 1-5 for novelty, plausibility, testability, feasibility, data_availability, scientific_impact, risk_of_confounding.",
    )


def build_report_prompt(project_summary: str) -> str:
    return _base_prompt(
        "Draft a Markdown scientific planning report.",
        project_summary,
        "Include inputs, clarification, literature plan, dataset profile, evidence, gaps, hypotheses, critique, validation plan, limitations, next steps.",
    )


def _base_prompt(task: str, context: str, output_contract: str) -> str:
    return (
        "You are a domain-agnostic scientific co-scientist. Use cautious language. "
        "Do not claim generated hypotheses are true. Do not invent sources or evidence. "
        "Ask for clarification if the domain is too broad.\n\n"
        f"Task: {task}\n\n"
        f"Context:\n{context}\n\n"
        f"Output requirements:\n{output_contract}"
    )
