from src.synthesis import brainstorm_ideas, generate_hypotheses_fallback
from src.models import Evidence, GapFinding, ResearchProject, ResearchQuestion


def demo_project() -> ResearchProject:
    return ResearchProject(
        branch_of_science="Data, AI, and computation",
        specific_topic="Human-AI collaboration",
        research_problem="Teams struggle to know when to trust model suggestions.",
        goal="improve decision quality",
        available_data="notes and a pilot dashboard",
        constraints="limited time and mixed user expertise",
    )


def test_brainstorm_ideas_returns_distinct_lenses() -> None:
    ideas = brainstorm_ideas(
        branch_of_science="Data, AI, and computation",
        specific_topic="Human-AI collaboration",
        goal="improve decision quality",
        constraints="limited time",
        lens_names=["Mechanistic", "Comparative", "Optimization"],
        available_inputs="notes",
    )
    assert len(ideas) == 3
    assert len({idea["hypothesis_type"] for idea in ideas}) == 3


def test_generate_hypotheses_are_diverse() -> None:
    project = demo_project()
    evidence = [
        Evidence(
            project_id=project.id,
            source_id="s1",
            evidence_type="result",
            text="Users made fewer errors when explanations were paired with confidence cues.",
            variables=["explanations", "confidence cues", "errors"],
            provenance="pilot paragraph 1",
        ),
        Evidence(
            project_id=project.id,
            source_id="s2",
            evidence_type="limitation",
            text="The sample size was small and only covered one workflow.",
            variables=["sample size", "workflow"],
            provenance="pilot paragraph 2",
        ),
    ]
    gaps = [
        GapFinding(
            project_id=project.id,
            title="Limited workflow coverage",
            description="Only one workflow was tested.",
            evidence_ids=[evidence[1].id],
            gap_type="limitation",
            explanation="Need more settings.",
        )
    ]
    questions = [
        ResearchQuestion(
            project_id=project.id,
            question="How do confidence cues affect trust calibration?",
            why_it_matters="Better calibration may reduce errors.",
        )
    ]
    hypotheses = generate_hypotheses_fallback(project, questions, evidence, gaps)
    assert len(hypotheses) >= 5
    assert len({item.hypothesis_type for item in hypotheses}) >= 5
    assert all(item.simulation_summary for item in hypotheses)
