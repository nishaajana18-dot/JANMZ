from src.research_catalog import (
    branch_names,
    discipline_names,
    questions_for_branch,
    questions_for_path,
    subfield_names,
    topics_for_branch,
    topics_for_path,
)


def test_science_tree_narrows_physics_options() -> None:
    branches = branch_names()
    assert "Physics" in branches
    assert "Medicine and health" in branches

    physics_disciplines = discipline_names("Physics")
    assert "Biophysics" in physics_disciplines
    assert "Mechanics" in physics_disciplines
    assert "Quantum physics" in physics_disciplines
    assert "Clinical science" not in physics_disciplines

    quantum_subfields = subfield_names("Physics", "Quantum physics")
    assert "Quantum information" in quantum_subfields
    assert "Medical physics" not in quantum_subfields


def test_topics_and_questions_are_specific_to_tree_path() -> None:
    quantum_topics = topics_for_path("Physics", "Quantum physics", "Quantum information")
    quantum_questions = questions_for_path(
        "Physics", "Quantum physics", "Quantum information"
    )
    assert "Qubit error mitigation" in quantum_topics
    assert any("noise source" in question for question in quantum_questions)

    medical_topics = topics_for_branch("Medicine and health")
    assert "Early detection biomarkers" in medical_topics
    assert "Qubit error mitigation" not in medical_topics


def test_branch_level_helpers_flatten_only_that_branch() -> None:
    physics_topics = topics_for_branch("Physics")
    physics_questions = questions_for_branch("Physics")
    assert "Protein folding dynamics" in physics_topics
    assert "Qubit error mitigation" in physics_topics
    assert "Early detection biomarkers" not in physics_topics
    assert all("clinical change" not in question.lower() for question in physics_questions)
