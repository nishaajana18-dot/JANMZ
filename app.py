from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.config import settings
from src.database import Database
from src.demo_data import build_demo_bundle
from src.export import export_json, export_markdown
from src.ingestion import extract_evidence_fallback, parse_source, save_uploaded_file
from src.models import (
    Evidence,
    GapFinding,
    Hypothesis,
    ParsedContent,
    ResearchProject,
    ResearchQuestion,
    Source,
)
from src.research_catalog import HYPOTHESIS_LENSES, QUESTION_LENSES, RESEARCH_AREAS
from src.ranking import rank_hypotheses
from src.retrieval import EvidenceIndex
from src.synthesis import (
    generate_gaps_fallback,
    generate_hypotheses_fallback,
    generate_questions_fallback,
)


settings.ensure_directories()
db = Database(settings.db_path)


def current_project() -> ResearchProject | None:
    projects = db.list_all(ResearchProject)
    return projects[0] if projects else None


def save_project(project: ResearchProject) -> None:
    db.upsert(project)


def load_demo_project() -> None:
    bundle = build_demo_bundle()
    project = bundle["project"]
    save_project(project)
    for key in ("sources", "evidence", "gaps", "questions", "hypotheses"):
        db.bulk_upsert(bundle[key])
    EvidenceIndex(project.id).build(bundle["evidence"])
    st.session_state["selected_hypothesis_id"] = bundle["hypotheses"][0].id


def project_records(project: ResearchProject) -> dict[str, list]:
    return {
        "sources": db.list_all(Source, project.id),
        "parsed_contents": db.list_all(ParsedContent, project.id),
        "evidence": db.list_all(Evidence, project.id),
        "gaps": db.list_all(GapFinding, project.id),
        "questions": db.list_all(ResearchQuestion, project.id),
        "hypotheses": db.list_all(Hypothesis, project.id),
    }


st.set_page_config(page_title="Research Hypothesis Builder", layout="wide")
st.title("Research Hypothesis Builder")
st.caption(
    "A local MVP that turns research intake, uploaded files, and notes into evidence, gaps, questions, and testable hypotheses."
)

with st.sidebar:
    st.subheader("Project Controls")
    st.page_link("app.py", label="Main Workflow")
    st.page_link("pages/1_Brainstorming_Studio.py", label="Brainstorming Studio")
    if st.button("Load Demo Project", use_container_width=True):
        load_demo_project()
        st.success("Loaded a synthetic demo project for exploration.")

    project = current_project()
    if project:
        st.info(f"Active project: {project.specific_topic}")
        if st.button("Clear Active Project Data", use_container_width=True):
            db.delete_project_data(project.id)
            st.rerun()
    else:
        st.warning("No active project yet. Start with the intake form or demo mode.")

st.header("Step 1: Research Intake")
with st.form("research_intake"):
    col1, col2 = st.columns(2)
    with col1:
        area_names = list(RESEARCH_AREAS.keys())
        selected_area = st.selectbox("Research area", area_names)
        branch = st.text_input("Branch of science", value=selected_area)
        topic_options = RESEARCH_AREAS[selected_area]
        suggested_topic = st.selectbox("Suggested topic menu", topic_options)
        topic = st.text_input("Specific topic", value=suggested_topic)
        problem = st.text_area("Research problem")
        goal = st.text_area("What do you want to discover or solve?")
    with col2:
        data = st.text_area("Available data")
        constraints = st.text_area("Constraints")
        novelty = st.selectbox(
            "Preferred novelty level",
            ["conservative", "balanced", "speculative"],
        )
        output_style = st.selectbox(
            "Preferred output style",
            ["concise", "detailed", "grant-style", "experimental-plan style"],
        )
    if st.form_submit_button("Save Research Project"):
        project = ResearchProject(
            branch_of_science=branch,
            specific_topic=topic,
            research_problem=problem,
            goal=goal,
            available_data=data,
            constraints=constraints,
            novelty_level=novelty,
            output_style=output_style,
        )
        save_project(project)
        st.success("Project intake saved.")
        st.rerun()

project = current_project()
if not project:
    st.stop()

records = project_records(project)

st.header("Step 2: Upload Files")
uploads = st.file_uploader(
    "Add supporting files",
    type=["pdf", "txt", "csv", "xlsx", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
)
if uploads and st.button("Store Uploaded Files"):
    for uploaded_file in uploads:
        saved_path = save_uploaded_file(project.id, uploaded_file)
        source = Source(
            project_id=project.id,
            filename=uploaded_file.name,
            file_type=Path(uploaded_file.name).suffix.lower().lstrip("."),
            raw_path=str(saved_path),
            processed_status="uploaded",
        )
        db.upsert(source)
    st.success("Files stored in the local uploads folder.")
    st.rerun()

if records["sources"]:
    st.dataframe(
        [
            {
                "filename": source.filename,
                "type": source.file_type,
                "status": source.processed_status,
                "uploaded": source.upload_time.isoformat(timespec="seconds"),
            }
            for source in records["sources"]
        ],
        use_container_width=True,
    )

st.header("Step 3-5: Ingest, Extract Evidence, and Index")
if st.button("Ingest Files"):
    sources = db.list_all(Source, project.id)
    all_evidence: list[Evidence] = []
    for source in sources:
        if source.raw_path.startswith("demo://"):
            continue
        parsed = parse_source(project.id, source)
        db.upsert(parsed)
        evidence = extract_evidence_fallback(project.id, source, parsed.summary_text)
        all_evidence.extend(evidence)
        db.bulk_upsert(evidence)
        db.upsert(source.model_copy(update={"processed_status": "processed"}))

    EvidenceIndex(project.id).build(db.list_all(Evidence, project.id))
    st.success(f"Ingestion complete. Extracted {len(all_evidence)} evidence items.")
    st.rerun()

records = project_records(project)

if records["parsed_contents"]:
    with st.expander("Parsed file summaries"):
        for item in records["parsed_contents"]:
            st.markdown(f"**Source ID:** {item.source_id}")
            st.write(item.summary_text[:1000])

if records["evidence"]:
    st.subheader("Step 4: Extracted Evidence")
    for item in records["evidence"]:
        with st.expander(f"{item.evidence_type.title()} | {item.provenance}"):
            st.write(item.text)
            st.caption(
                f"Variables: {', '.join(item.variables) or 'None'} | "
                f"Conditions: {', '.join(item.conditions) or 'None'} | "
                f"Confidence: {item.confidence:.2f}"
            )

    st.subheader("Step 5: Search Evidence")
    search_query = st.text_input("Search extracted evidence")
    if search_query:
        results = EvidenceIndex(project.id).search(search_query)
        if results:
            for evidence, score in results:
                st.write(f"**{evidence.evidence_type.title()}** ({score:.2f})")
                st.write(evidence.text)
                st.caption(evidence.provenance)
        else:
            st.info("No indexed evidence matched the current search.")

st.header("Step 6: Identify Gaps")
if st.button("Find Gaps"):
    gaps = generate_gaps_fallback(project, records["evidence"])
    db.bulk_upsert(gaps)
    st.success(f"Created {len(gaps)} gap findings.")
    st.rerun()

if records["gaps"]:
    st.dataframe(
        [
            {
                "title": gap.title,
                "type": gap.gap_type,
                "importance": gap.importance_score,
                "evidence_links": len(gap.evidence_ids),
            }
            for gap in records["gaps"]
        ],
        use_container_width=True,
    )

st.header("Step 7: Generate Research Questions")
if st.button("Generate Research Questions"):
    questions = generate_questions_fallback(project, records["gaps"], records["evidence"])
    db.bulk_upsert(questions)
    st.success(f"Created {len(questions)} research questions.")
    st.rerun()

if records["questions"]:
    with st.expander("Question lenses used"):
        for label, description in QUESTION_LENSES.items():
            st.markdown(f"- **{label}:** {description}")
    for question in records["questions"]:
        st.markdown(f"- **{question.question}**")
        st.caption(
            f"Why it matters: {question.why_it_matters} | "
            f"Feasibility: {question.feasibility_score:.2f} | "
            f"Novelty: {question.novelty_score:.2f}"
        )

st.header("Step 8-9: Generate and Rank Hypotheses")
if st.button("Generate Hypotheses"):
    hypotheses = generate_hypotheses_fallback(
        project,
        records["questions"],
        records["evidence"],
        records["gaps"],
    )
    ranked = rank_hypotheses(project, hypotheses)
    db.bulk_upsert(ranked)
    st.success(f"Created and ranked {len(ranked)} hypotheses.")
    st.rerun()

records = project_records(project)
if records["hypotheses"]:
    st.subheader("Ranked Hypotheses")
    cols = st.columns(2)
    for idx, hypothesis in enumerate(records["hypotheses"]):
        with cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {hypothesis.title}")
                st.write(hypothesis.hypothesis)
                st.caption(
                    f"Type {hypothesis.hypothesis_type} | "
                    f"Confidence {hypothesis.confidence_score:.2f} | "
                    f"Novelty {hypothesis.novelty_score:.2f} | "
                    f"Testability {hypothesis.testability_score:.2f} | "
                    f"Evidence links {len(hypothesis.supporting_evidence_ids)} | "
                    f"Rank {hypothesis.rank_score:.2f}"
                )
                if st.button("View Details", key=f"view_{hypothesis.id}"):
                    st.session_state["selected_hypothesis_id"] = hypothesis.id

st.header("Step 10: Hypothesis Detail View")
selected_id = st.session_state.get("selected_hypothesis_id")
selected = db.get(Hypothesis, selected_id) if selected_id else None
evidence_lookup = {item.id: item for item in records["evidence"]}
if selected:
    st.subheader(selected.title)
    st.caption(f"Hypothesis type: {selected.hypothesis_type}")
    st.write(selected.hypothesis)
    st.write(f"**Rationale:** {selected.rationale}")
    st.write(f"**Proposed experiment:** {selected.proposed_experiment}")
    st.write(f"**Predicted outcome:** {selected.predicted_outcome}")
    st.write(f"**Falsification criteria:** {selected.falsification_criteria}")
    if selected.assumptions:
        st.write("**Assumptions**")
        for assumption in selected.assumptions:
            st.markdown(f"- {assumption}")
    if selected.simulation_summary:
        st.write("**Synthetic simulation note:**")
        st.caption(selected.simulation_summary)
    st.write("**Supporting evidence**")
    for evidence_id in selected.supporting_evidence_ids:
        evidence = evidence_lookup.get(evidence_id)
        if evidence:
            st.markdown(f"- {evidence.text}")
            st.caption(evidence.provenance)
    if selected.conflicting_evidence_ids:
        st.write("**Conflicting evidence**")
        for evidence_id in selected.conflicting_evidence_ids:
            evidence = evidence_lookup.get(evidence_id)
            if evidence:
                st.markdown(f"- {evidence.text}")
                st.caption(evidence.provenance)

    updated_notes = st.text_area(
        "Human notes",
        value=selected.human_notes,
        key=f"notes_{selected.id}",
    )
    updated_status = st.selectbox(
        "Review status",
        ["draft", "accepted", "rejected", "needs_revision"],
        index=["draft", "accepted", "rejected", "needs_revision"].index(
            selected.human_review_status
        ),
    )
    if st.button("Save Review Notes"):
        db.upsert(
            selected.model_copy(
                update={
                    "human_notes": updated_notes,
                    "human_review_status": updated_status,
                }
            )
        )
        st.success("Hypothesis review details updated.")
        st.rerun()
else:
    st.info("Select a hypothesis card to inspect its evidence and review details.")

st.header("Step 11: Export")
export_dir = settings.processed_dir
json_path = export_dir / f"{project.id}_report.json"
md_path = export_dir / f"{project.id}_report.md"
export_json(
    json_path,
    project,
    records["sources"],
    records["evidence"],
    records["gaps"],
    records["questions"],
    records["hypotheses"],
)
export_markdown(
    md_path,
    project,
    records["sources"],
    records["evidence"],
    records["gaps"],
    records["questions"],
    records["hypotheses"],
)

col_json, col_md = st.columns(2)
with col_json:
    st.download_button(
        "Download JSON Export",
        data=json_path.read_text(encoding="utf-8"),
        file_name=json_path.name,
        mime="application/json",
    )
with col_md:
    st.download_button(
        "Download Markdown Report",
        data=md_path.read_text(encoding="utf-8"),
        file_name=md_path.name,
        mime="text/markdown",
    )

st.header("Step 12: Demo Mode Notice")
st.caption(
    "Demo mode creates synthetic project records so you can explore the workflow without uploading real research material."
)
