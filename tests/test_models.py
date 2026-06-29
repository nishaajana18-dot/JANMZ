from src.models import Evidence, ResearchProject


def test_project_defaults() -> None:
    project = ResearchProject(
        branch_of_science="Physics",
        specific_topic="Battery materials",
        research_problem="Capacity fade",
        goal="improve cycle life",
        available_data="pilot data",
        constraints="limited budget",
    )
    assert project.id
    assert project.novelty_level == "balanced"


def test_evidence_requires_provenance() -> None:
    evidence = Evidence(
        project_id="p1",
        source_id="s1",
        evidence_type="claim",
        text="A supported statement.",
        provenance="source paragraph 1",
    )
    assert evidence.provenance == "source paragraph 1"
