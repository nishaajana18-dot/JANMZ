from __future__ import annotations

from src.models import (
    Evidence,
    GapFinding,
    Hypothesis,
    ResearchProject,
    ResearchQuestion,
    Source,
)


def build_demo_bundle() -> dict[str, list | ResearchProject]:
    project = ResearchProject(
        branch_of_science="Biomedical engineering",
        specific_topic="Wearable hydration monitoring",
        research_problem="Field teams struggle to detect early dehydration before performance drops.",
        goal="identify practical signals for earlier dehydration detection",
        available_data="Synthetic wearable summaries, field notes, and mock pilot results",
        constraints="Low-cost sensors, small pilot sample, outdoor conditions",
        novelty_level="balanced",
        output_style="experimental-plan style",
    )

    sources = [
        Source(
            project_id=project.id,
            filename="demo_field_notes.txt",
            file_type="txt",
            raw_path="demo://field_notes",
            processed_status="processed",
        ),
        Source(
            project_id=project.id,
            filename="demo_pilot_results.csv",
            file_type="csv",
            raw_path="demo://pilot_results",
            processed_status="processed",
        ),
    ]

    evidence = [
        Evidence(
            project_id=project.id,
            source_id=sources[0].id,
            evidence_type="claim",
            text="Participants often reported fatigue 20 to 30 minutes before the strongest hydration warning appeared.",
            variables=["fatigue", "hydration warning", "time lag"],
            confidence=0.55,
            provenance="demo_field_notes.txt paragraph 1",
        ),
        Evidence(
            project_id=project.id,
            source_id=sources[1].id,
            evidence_type="result",
            text="A combined temperature and heart-rate trend flagged potential dehydration earlier than either signal alone in the mock pilot.",
            variables=["temperature", "heart rate", "combined trend"],
            confidence=0.72,
            provenance="demo_pilot_results.csv summary",
        ),
        Evidence(
            project_id=project.id,
            source_id=sources[1].id,
            evidence_type="limitation",
            text="The pilot included few participants and did not control for caffeine intake or acclimation.",
            variables=["participant count", "caffeine intake", "acclimation"],
            confidence=0.6,
            provenance="demo_pilot_results.csv summary",
        ),
    ]

    gaps = [
        GapFinding(
            project_id=project.id,
            title="Missing control for confounders",
            description="The mock pilot did not control for caffeine intake or heat acclimation.",
            evidence_ids=[evidence[2].id],
            gap_type="missing_control",
            importance_score=0.84,
            explanation="Without these controls, the signal may not generalize across field settings.",
        )
    ]

    questions = [
        ResearchQuestion(
            project_id=project.id,
            question="Does combining skin temperature and heart-rate drift improve early dehydration detection compared with single-sensor alerts?",
            why_it_matters="A better early warning could help prevent performance decline in field settings.",
            related_gap_ids=[gaps[0].id],
            feasibility_score=0.79,
            novelty_score=0.63,
        )
    ]

    hypotheses = [
        Hypothesis(
            project_id=project.id,
            title="Combined wearable trend improves early detection",
            hypothesis_type="comparative",
            research_question=questions[0].question,
            hypothesis="If skin temperature and heart-rate drift are modeled together, dehydration risk can be detected earlier than with single-sensor thresholds.",
            rationale="The synthetic pilot suggests the combined trend was more sensitive than isolated alerts.",
            supporting_evidence_ids=[evidence[0].id, evidence[1].id],
            conflicting_evidence_ids=[evidence[2].id],
            proposed_experiment="Run a crossover field study comparing combined-signal alerts against single-sensor baselines.",
            predicted_outcome="The combined model will trigger earlier while maintaining acceptable false-positive rates.",
            falsification_criteria="Reject if the combined model does not outperform both single-sensor baselines on lead time and accuracy.",
            novelty_score=0.63,
            testability_score=0.79,
            confidence_score=0.58,
            assumptions=[
                "The synthetic signals reflect real-world hydration trends.",
                "Lead time can be measured consistently across devices.",
            ],
            simulation_summary="Synthetic simulation only: the combined-signal scenario outperformed the baseline in most sampled runs.",
            human_review_status="draft",
            rank_score=0.71,
        )
    ]

    return {
        "project": project,
        "sources": sources,
        "evidence": evidence,
        "gaps": gaps,
        "questions": questions,
        "hypotheses": hypotheses,
    }
