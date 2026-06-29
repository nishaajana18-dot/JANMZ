from src.research_catalog import branch_names, questions_for_branch, topics_for_branch


def test_branch_dependent_options_are_scoped() -> None:
    branches = branch_names()
    assert "Biomedical and health sciences" in branches
    assert "Data, AI, and computation" in branches

    biomedical_topics = topics_for_branch("Biomedical and health sciences")
    data_topics = topics_for_branch("Data, AI, and computation")
    assert "Diagnostics and biomarkers" in biomedical_topics
    assert "Human-AI collaboration" not in biomedical_topics
    assert "Human-AI collaboration" in data_topics


def test_branch_questions_are_scoped() -> None:
    questions = questions_for_branch("Physical sciences and engineering")
    assert questions
    assert all("patient" not in question.lower() for question in questions)
