from src.prompts import (
    MODEL_ROUTING,
    build_domain_clarification_prompt,
    build_hypothesis_generation_prompt,
)


def test_prompt_templates_are_hallucination_resistant() -> None:
    prompt = build_domain_clarification_prompt("physics", "find a testable idea")
    assert "Do not invent sources or evidence" in prompt
    assert "suggested_subfields" in prompt


def test_model_routing_has_reasoning_tasks() -> None:
    prompt = build_hypothesis_generation_prompt("domain", "gaps", "evidence")
    assert "falsifiable" in prompt
    assert MODEL_ROUTING["hypothesis_generation"]
