from src.models import Evidence, Hypothesis, ResearchProject
from src.scientific_workflow import (
    clarify_domain,
    critique_hypotheses,
    generic_evidence_summary,
    score_hypotheses,
)


def test_clarify_domain_flags_broad_input() -> None:
    result = clarify_domain("physics", "", "find a project")
    assert result["needs_clarification"] is True
    assert any("Quantum physics" in item for item in result["suggested_subfields"])


def test_generic_evidence_summary_uses_generic_schema() -> None:
    project = ResearchProject(
        branch_of_science="Physics",
        specific_topic="Quantum sensing",
        research_problem="Noise limits performance",
        goal="improve signal quality",
        available_data="papers",
        constraints="small pilot",
    )
    evidence = [
        Evidence(
            project_id=project.id,
            source_id="s1",
            evidence_type="result",
            text="Noise decreased signal stability under high temperature.",
            variables=["Noise", "Signal"],
            provenance="paper p1",
        )
    ]
    summary = generic_evidence_summary(project, evidence)
    assert "key_findings" in summary
    assert summary["field"] == "Physics"


def test_scoring_and_critique_return_rows() -> None:
    hypothesis = Hypothesis(
        project_id="p1",
        title="Test",
        research_question="Question?",
        hypothesis="If X changes, Y changes.",
        rationale="Because",
        proposed_experiment="Run a controlled comparison.",
        predicted_outcome="Y changes.",
        falsification_criteria="No change in Y.",
        supporting_evidence_ids=["e1"],
    )
    assert score_hypotheses([hypothesis], [])[0]["Total"] > 0
    assert critique_hypotheses([hypothesis], [])[0]["Hypothesis"] == "Test"
