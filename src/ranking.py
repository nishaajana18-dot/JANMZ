from __future__ import annotations

from src.models import Hypothesis, ResearchProject


NOVELTY_TARGET = {
    "conservative": 0.3,
    "balanced": 0.6,
    "speculative": 0.85,
}


def rank_hypotheses(
    project: ResearchProject, hypotheses: list[Hypothesis]
) -> list[Hypothesis]:
    target = NOVELTY_TARGET[project.novelty_level]
    ranked: list[Hypothesis] = []
    for hypothesis in hypotheses:
        evidence_support = min(1.0, len(hypothesis.supporting_evidence_ids) / 4)
        feasibility = hypothesis.testability_score
        novelty_alignment = 1 - abs(hypothesis.novelty_score - target)
        score = (
            0.35 * evidence_support
            + 0.25 * hypothesis.confidence_score
            + 0.2 * hypothesis.testability_score
            + 0.1 * feasibility
            + 0.1 * novelty_alignment
        )
        ranked.append(hypothesis.model_copy(update={"rank_score": round(score, 3)}))

    return sorted(ranked, key=lambda item: item.rank_score, reverse=True)
