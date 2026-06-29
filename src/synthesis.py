from __future__ import annotations

from collections import Counter

from src.models import Evidence, GapFinding, Hypothesis, ResearchProject, ResearchQuestion


def generate_gaps_fallback(
    project: ResearchProject, evidence_list: list[Evidence]
) -> list[GapFinding]:
    gaps: list[GapFinding] = []
    limitations = [item for item in evidence_list if item.evidence_type == "limitation"]
    low_conf = [item for item in evidence_list if item.confidence < 0.4]
    variables = Counter(var for item in evidence_list for var in item.variables)

    if limitations:
        gaps.append(
            GapFinding(
                project_id=project.id,
                title="Limitations reported in current sources",
                description="Several uploaded sources explicitly mention limitations or uncertainty.",
                evidence_ids=[item.id for item in limitations[:5]],
                gap_type="limitation",
                importance_score=0.8,
                explanation="These limitations highlight where the current evidence base is incomplete.",
            )
        )

    if low_conf:
        gaps.append(
            GapFinding(
                project_id=project.id,
                title="Weakly supported observations",
                description="Some extracted evidence is low confidence and should be validated with stronger data.",
                evidence_ids=[item.id for item in low_conf[:5]],
                gap_type="weak_support",
                importance_score=0.7,
                explanation="Low-confidence items usually reflect sparse detail, ambiguous wording, or missing methods.",
            )
        )

    sparse_variables = [name for name, count in variables.items() if count == 1][:5]
    if sparse_variables:
        gaps.append(
            GapFinding(
                project_id=project.id,
                title="Variables explored only once",
                description=f"These variables appear only once across the current evidence: {', '.join(sparse_variables)}.",
                evidence_ids=[item.id for item in evidence_list[:5]],
                gap_type="unexplored_variable",
                importance_score=0.65,
                explanation="Single-mention variables may point to promising but underexplored directions.",
            )
        )

    if not gaps:
        gaps.append(
            GapFinding(
                project_id=project.id,
                title="Need for more direct evidence",
                description="The current project has little structured evidence, so new data collection is likely needed.",
                evidence_ids=[item.id for item in evidence_list[:3]],
                gap_type="needs_more_data",
                importance_score=0.6,
                explanation="The app could not identify strong recurring patterns in the uploaded material.",
            )
        )

    return gaps


def generate_questions_fallback(
    project: ResearchProject, gaps: list[GapFinding], evidence_list: list[Evidence]
) -> list[ResearchQuestion]:
    questions: list[ResearchQuestion] = []
    top_gap_ids = [gap.id for gap in gaps[:3]]
    evidence_terms = [var for item in evidence_list for var in item.variables][:5]
    term_text = ", ".join(evidence_terms) if evidence_terms else project.specific_topic

    prompts = [
        f"Which factors most strongly influence {project.specific_topic} under the current constraints?",
        f"What additional data would reduce uncertainty around {term_text} in this problem space?",
        f"How could a controlled experiment test the main limitation identified in the uploaded evidence?",
        f"What mechanism could explain the reported observations related to {project.research_problem}?",
        f"Which variable changes are most feasible to study next for {project.goal}?",
    ]

    for idx, prompt in enumerate(prompts, start=1):
        questions.append(
            ResearchQuestion(
                project_id=project.id,
                question=prompt,
                why_it_matters=f"This question helps move the project toward {project.goal.lower()}.",
                related_gap_ids=top_gap_ids,
                feasibility_score=max(0.3, 0.8 - idx * 0.08),
                novelty_score=0.45
                if project.novelty_level == "conservative"
                else 0.6
                if project.novelty_level == "balanced"
                else 0.78,
            )
        )

    return questions


def generate_hypotheses_fallback(
    project: ResearchProject,
    questions: list[ResearchQuestion],
    evidence_list: list[Evidence],
    gaps: list[GapFinding],
) -> list[Hypothesis]:
    support = [
        item
        for item in evidence_list
        if item.evidence_type in {"result", "claim", "dataset_summary"}
    ]
    conflict = [item for item in evidence_list if item.evidence_type == "limitation"]
    variable_text = (
        ", ".join(sorted({var for item in evidence_list for var in item.variables})[:3])
        or "key study variables"
    )
    gap_summary = gaps[0].title if gaps else "current evidence gaps"

    hypotheses: list[Hypothesis] = []
    for idx, question in enumerate(questions[:5], start=1):
        supporting_ids = [item.id for item in support[idx - 1 : idx + 1]] or [
            item.id for item in evidence_list[:2]
        ]
        conflicting_ids = [item.id for item in conflict[:1]]
        confidence = min(
            0.85, 0.3 + 0.1 * len(supporting_ids) - 0.08 * len(conflicting_ids)
        )
        novelty = question.novelty_score + (
            0.08 if project.novelty_level == "speculative" else 0.0
        )

        hypotheses.append(
            Hypothesis(
                project_id=project.id,
                title=f"Hypothesis {idx}: {project.specific_topic}",
                research_question=question.question,
                hypothesis=f"If {variable_text} are systematically adjusted, then outcomes related to {project.goal.lower()} will change in a measurable way.",
                rationale=f"This draft hypothesis is grounded in uploaded evidence and responds to the gap '{gap_summary}'.",
                supporting_evidence_ids=supporting_ids,
                conflicting_evidence_ids=conflicting_ids,
                proposed_experiment=(
                    "Run a small controlled comparison with a baseline condition, one adjusted variable set, "
                    "and clear outcome measurements."
                ),
                predicted_outcome=(
                    f"The adjusted condition will outperform the baseline on metrics relevant to {project.goal.lower()}."
                ),
                falsification_criteria=(
                    "Reject the hypothesis if the adjusted condition shows no meaningful improvement or if the effect reverses."
                ),
                novelty_score=min(0.95, novelty),
                testability_score=question.feasibility_score,
                confidence_score=max(0.2, confidence),
                human_review_status="draft",
            )
        )

    return hypotheses
