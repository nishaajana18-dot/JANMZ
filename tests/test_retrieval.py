from src.models import Evidence
from src.retrieval import EvidenceIndex


def test_search_returns_ranked_results(tmp_path) -> None:
    index = EvidenceIndex("project-1")
    index.index_path = tmp_path / "project-1_tfidf.json"
    evidence = [
        Evidence(
            project_id="project-1",
            source_id="s1",
            evidence_type="result",
            text="Hydration monitoring improved alert timing.",
            provenance="demo 1",
        ),
        Evidence(
            project_id="project-1",
            source_id="s2",
            evidence_type="claim",
            text="Battery charging pattern changed over time.",
            provenance="demo 2",
        ),
    ]
    index.build(evidence)
    results = index.search("hydration alert", limit=1)
    assert len(results) == 1
    assert "Hydration" in results[0][0].text
