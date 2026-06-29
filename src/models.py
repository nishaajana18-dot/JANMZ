from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id() -> str:
    return str(uuid4())


class ResearchProject(BaseModel):
    id: str = Field(default_factory=new_id)
    branch_of_science: str
    specific_topic: str
    research_problem: str
    goal: str
    available_data: str
    constraints: str
    novelty_level: Literal["conservative", "balanced", "speculative"] = "balanced"
    output_style: Literal[
        "concise", "detailed", "grant-style", "experimental-plan style"
    ] = "concise"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Source(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    filename: str
    file_type: str
    upload_time: datetime = Field(default_factory=datetime.utcnow)
    raw_path: str
    processed_status: Literal["uploaded", "processed", "failed"] = "uploaded"


class ParsedContent(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    source_id: str
    summary_text: str
    processed_path: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Evidence(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    source_id: str
    evidence_type: Literal[
        "claim", "method", "result", "limitation", "dataset_summary", "observation"
    ]
    text: str
    variables: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    confidence: float = 0.3
    provenance: str


class GapFinding(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    title: str
    description: str
    evidence_ids: list[str] = Field(default_factory=list)
    gap_type: Literal[
        "unanswered_question",
        "weak_support",
        "contradiction",
        "missing_control",
        "unexplored_variable",
        "limitation",
        "needs_more_data",
    ]
    importance_score: float = 0.5
    explanation: str


class ResearchQuestion(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    question: str
    why_it_matters: str
    related_gap_ids: list[str] = Field(default_factory=list)
    feasibility_score: float = 0.5
    novelty_score: float = 0.5


class Hypothesis(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    title: str
    hypothesis_type: str = "general"
    research_question: str
    hypothesis: str
    rationale: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    conflicting_evidence_ids: list[str] = Field(default_factory=list)
    proposed_experiment: str
    predicted_outcome: str
    falsification_criteria: str
    novelty_score: float = 0.5
    testability_score: float = 0.5
    confidence_score: float = 0.3
    assumptions: list[str] = Field(default_factory=list)
    simulation_summary: str = ""
    human_review_status: Literal[
        "draft", "accepted", "rejected", "needs_revision"
    ] = "draft"
    human_notes: str = ""
    rank_score: float = 0.0
