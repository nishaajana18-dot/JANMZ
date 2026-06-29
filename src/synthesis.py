from __future__ import annotations

from collections import Counter

from src.research_catalog import HYPOTHESIS_LENSES, QUESTION_LENSES
from src.simulations import run_scenario_simulation
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
        f"{QUESTION_LENSES['Mechanism']} In this case, how might it explain {project.research_problem.lower()}?",
        f"{QUESTION_LENSES['Comparison']} Specifically, what should be compared to improve {project.goal.lower()}?",
        f"{QUESTION_LENSES['Optimization']} Focus on {term_text}.",
        f"{QUESTION_LENSES['Robustness']} Especially under these constraints: {project.constraints}.",
        f"{QUESTION_LENSES['Translation']} For {project.specific_topic}, what would that look like?",
        f"What additional data would reduce uncertainty around {term_text} in this problem space?",
    ]

    for idx, prompt in enumerate(prompts[:6], start=1):
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
    for idx, lens in enumerate(HYPOTHESIS_LENSES, start=1):
        question = questions[(idx - 1) % len(questions)] if questions else None
        supporting_ids = [item.id for item in support[idx - 1 : idx + 2]] or [
            item.id for item in evidence_list[:2]
        ]
        conflicting_ids = [item.id for item in conflict[:1]]
        confidence = min(
            0.85, 0.3 + 0.1 * len(supporting_ids) - 0.08 * len(conflicting_ids)
        )
        question_novelty = question.novelty_score if question else 0.6
        question_feasibility = question.feasibility_score if question else 0.55
        novelty = question_novelty + (
            0.08 if project.novelty_level == "speculative" else 0.0
        )
        simulation = run_scenario_simulation(
            label=lens["label"],
            baseline_mean=1.0,
            effect_mean=0.12 + (0.04 * idx),
            noise=max(0.08, 0.22 - (0.02 * idx)),
        )

        hypothesis_text = _build_hypothesis_text(
            lens["type"],
            project.goal.lower(),
            project.specific_topic,
            variable_text,
        )
        experiment_text = _build_experiment_text(
            lens["type"], project.specific_topic, project.constraints
        )
        rationale_text = (
            f"This {lens['label'].lower()} hypothesis is grounded in uploaded evidence and responds to the gap "
            f"'{gap_summary}'. It uses the current project goal and available variables to define a distinct test angle."
        )
        predicted_outcome = _build_predicted_outcome(
            lens["type"], project.goal.lower()
        )
        falsification = _build_falsification_text(lens["type"])
        assumptions = [
            f"The available evidence is relevant to {project.specific_topic}.",
            f"The variables {variable_text} can be measured consistently.",
            "The proposed comparison can be executed with the stated constraints.",
        ]

        hypotheses.append(
            Hypothesis(
                project_id=project.id,
                title=f"{lens['label']} Hypothesis for {project.specific_topic}",
                hypothesis_type=lens["type"],
                research_question=question.question if question else project.research_problem,
                hypothesis=hypothesis_text,
                rationale=rationale_text,
                supporting_evidence_ids=supporting_ids,
                conflicting_evidence_ids=conflicting_ids,
                proposed_experiment=experiment_text,
                predicted_outcome=predicted_outcome,
                falsification_criteria=falsification,
                novelty_score=min(0.95, novelty),
                testability_score=question_feasibility,
                confidence_score=max(0.2, confidence),
                assumptions=assumptions,
                simulation_summary=simulation.summary,
                human_review_status="draft",
            )
        )

    return hypotheses


def brainstorm_ideas(
    branch_of_science: str,
    specific_topic: str,
    goal: str,
    constraints: str,
    lens_names: list[str],
    available_inputs: str,
) -> list[dict[str, object]]:
    ideas: list[dict[str, object]] = []
    topic_key = specific_topic or branch_of_science
    for idx, lens_name in enumerate(lens_names, start=1):
        lens = next(
            (item for item in HYPOTHESIS_LENSES if item["label"] == lens_name),
            HYPOTHESIS_LENSES[(idx - 1) % len(HYPOTHESIS_LENSES)],
        )
        simulation = run_scenario_simulation(
            label=lens["label"],
            baseline_mean=1.0,
            effect_mean=0.1 + (idx * 0.03),
            noise=0.15,
            trials=200,
        )
        question = {
            "Mechanistic": f"What mechanism might drive variation in {topic_key}?",
            "Comparative": f"Which intervention or condition is most promising for {topic_key}?",
            "Optimization": f"What parameter range is most likely to improve {goal.lower()}?",
            "Robustness": f"Does the expected effect hold under {constraints.lower() or 'realistic operating constraints'}?",
            "Translational": f"What is the smallest credible pilot for {topic_key}?",
        }.get(lens["label"], f"What is a strong next question for {topic_key}?")
        ideas.append(
            {
                "title": f"{lens['label']} idea for {topic_key}",
                "question": question,
                "hypothesis_type": lens["type"],
                "concept": _build_hypothesis_text(
                    lens["type"],
                    goal.lower() if goal else "the target outcome",
                    topic_key,
                    "priority variables",
                ),
                "experiment": _build_experiment_text(
                    lens["type"], topic_key, constraints or "limited resources"
                ),
                "simulation_summary": simulation.summary,
                "simulation_table": simulation.table,
                "data_needed": f"Useful starting inputs: {available_inputs or 'notes, a small dataset, or expert assumptions'}",
            }
        )
    return ideas


def _build_hypothesis_text(
    hypothesis_type: str, goal: str, topic: str, variable_text: str
) -> str:
    templates = {
        "mechanistic": f"If changes in {variable_text} are causally linked to {topic}, then a measurable shift should appear in outcomes tied to {goal}.",
        "comparative": f"If two candidate strategies for {topic} are tested side by side, the stronger strategy should produce better outcomes for {goal}.",
        "optimization": f"If {variable_text} are tuned within a more favorable range, performance related to {goal} should improve beyond baseline.",
        "robustness": f"If the main effect in {topic} is genuine, it should remain detectable even when conditions become more constrained or variable.",
        "translational": f"If the current evidence is strong enough to act on, a small applied pilot in {topic} should show an early positive signal for {goal}.",
    }
    return templates.get(
        hypothesis_type,
        f"If {variable_text} are adjusted in {topic}, outcomes related to {goal} will change in a measurable way.",
    )


def _build_experiment_text(hypothesis_type: str, topic: str, constraints: str) -> str:
    templates = {
        "mechanistic": f"Use a controlled experiment that isolates one suspected driver in {topic} while holding the remaining conditions constant. Account for constraints such as {constraints}.",
        "comparative": f"Compare a baseline and an alternative strategy for {topic} using matched cohorts, shared measurements, and a pre-declared evaluation window.",
        "optimization": f"Run a parameter sweep or staged pilot for {topic} across low, medium, and high settings, then estimate which range performs best.",
        "robustness": f"Repeat the main measurement for {topic} across at least two realistic constraint settings and compare effect stability.",
        "translational": f"Launch a small pilot for {topic} with a practical workflow, minimal instrumentation, and one decisive success metric.",
    }
    return templates.get(
        hypothesis_type,
        f"Run a small controlled comparison for {topic} with clear measurements and realistic constraints: {constraints}.",
    )


def _build_predicted_outcome(hypothesis_type: str, goal: str) -> str:
    templates = {
        "mechanistic": f"The manipulated driver will show a directional relationship with the outcome used to judge {goal}.",
        "comparative": f"One condition will outperform the comparator on the main metric relevant to {goal}.",
        "optimization": f"A middle or intentionally tuned range will outperform the untuned baseline for {goal}.",
        "robustness": f"The effect will persist with only modest attenuation under harder conditions tied to {goal}.",
        "translational": f"A small pilot will show a credible early signal that the idea can improve {goal}.",
    }
    return templates.get(
        hypothesis_type,
        f"The adjusted condition will outperform the baseline on metrics relevant to {goal}.",
    )


def _build_falsification_text(hypothesis_type: str) -> str:
    templates = {
        "mechanistic": "Reject if manipulating the proposed driver does not change the measured outcome in the predicted direction.",
        "comparative": "Reject if the alternative condition fails to outperform the comparator on the primary outcome.",
        "optimization": "Reject if tuning the parameter range does not produce a reproducible improvement over baseline.",
        "robustness": "Reject if the observed effect disappears once realistic constraints are introduced.",
        "translational": "Reject if the pilot cannot show an early positive signal on the pre-specified practical metric.",
    }
    return templates.get(
        hypothesis_type,
        "Reject if the adjusted condition shows no meaningful improvement or if the effect reverses.",
    )
