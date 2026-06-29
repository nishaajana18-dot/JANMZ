from pathlib import Path

from src.export import export_markdown
from src.models import Evidence, GapFinding, Hypothesis, ResearchProject, ResearchQuestion, Source
from src.ranking import rank_hypotheses
from src.synthesis import generate_gaps_fallback


def demo_project() -> ResearchProject:
    return ResearchProject(
        branch_of_science="Biology",
        specific_topic="Root growth",
        research_problem="Growth slows under drought",
        goal="improve resilience",
        available_data="lab notes",
        constraints="short timeline",
    )


def test_generate_gaps_from_limitations() -> None:
    project = demo_project()
    evidence = [
        Evidence(
            project_id=project.id,
            source_id="s1",
            evidence_type="limitation",
            text="A limitation is the small sample size.",
            provenance="notes p1",
        )
    ]
    gaps = generate_gaps_fallback(project, evidence)
    assert any(gap.gap_type == "limitation" for gap in gaps)


def test_hypothesis_ranking_prefers_supported_items() -> None:
    project = demo_project()
    hypotheses = [
        Hypothesis(
            project_id=project.id,
            title="A",
            research_question="Q1",
            hypothesis="H1",
            rationale="R1",
            supporting_evidence_ids=["e1", "e2", "e3"],
            conflicting_evidence_ids=[],
            proposed_experiment="E1",
            predicted_outcome="O1",
            falsification_criteria="F1",
            novelty_score=0.6,
            testability_score=0.8,
            confidence_score=0.75,
        ),
        Hypothesis(
            project_id=project.id,
            title="B",
            research_question="Q2",
            hypothesis="H2",
            rationale="R2",
            supporting_evidence_ids=["e1"],
            conflicting_evidence_ids=[],
            proposed_experiment="E2",
            predicted_outcome="O2",
            falsification_criteria="F2",
            novelty_score=0.6,
            testability_score=0.5,
            confidence_score=0.4,
        ),
    ]
    ranked = rank_hypotheses(project, hypotheses)
    assert ranked[0].title == "A"


def test_markdown_export_contains_sections(tmp_path: Path) -> None:
    project = demo_project()
    output = tmp_path / "report.md"
    export_markdown(
        output,
        project,
        [
            Source(
                project_id=project.id,
                filename="demo.txt",
                file_type="txt",
                raw_path="demo.txt",
            )
        ],
        [
            Evidence(
                project_id=project.id,
                source_id="s1",
                evidence_type="claim",
                text="Claim",
                provenance="p1",
            )
        ],
        [
            GapFinding(
                project_id=project.id,
                title="Gap",
                description="Desc",
                evidence_ids=[],
                gap_type="needs_more_data",
                explanation="Why",
            )
        ],
        [
            ResearchQuestion(
                project_id=project.id,
                question="Question?",
                why_it_matters="Why",
            )
        ],
        [
            Hypothesis(
                project_id=project.id,
                title="Hyp",
                research_question="Question?",
                hypothesis="Hypothesis text",
                rationale="Because",
                proposed_experiment="Experiment",
                predicted_outcome="Outcome",
                falsification_criteria="False if not observed",
            )
        ],
    )
    text = output.read_text(encoding="utf-8")
    assert "## Ranked Hypotheses" in text
