from __future__ import annotations

from pathlib import Path

import pandas as pd
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
from src.ranking import rank_hypotheses
from src.research_catalog import (
    HYPOTHESIS_LENSES,
    QUESTION_LENSES,
    branch_names,
    discipline_names,
    path_label,
    questions_for_path,
    subfield_names,
    topics_for_path,
)
from src.resources import fetch_research_resources
from src.retrieval import EvidenceIndex
from src.prompts import MODEL_ROUTING
from src.scientific_workflow import (
    build_validation_plan,
    clarify_domain,
    critique_hypotheses,
    detect_knowledge_gaps,
    generic_evidence_summary,
    plan_literature,
    score_hypotheses,
)
from src.synthesis import (
    brainstorm_ideas,
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


def dataset_profiles(records: dict[str, list]) -> list[dict]:
    profiles = []
    for parsed in records["parsed_contents"]:
        if parsed.metadata.get("shape"):
            profiles.append(parsed.metadata)
    return profiles


def render_landing() -> None:
    st.title("General AI Co-Scientist")
    st.caption(
        "A domain-agnostic assistant for turning scientific papers and datasets into testable hypotheses."
    )
    steps = [
        "Clarify domain",
        "Collect papers/data",
        "Extract evidence",
        "Analyze dataset",
        "Find gaps",
        "Generate hypotheses",
        "Critique and rank",
        "Export report",
    ]
    cols = st.columns(4)
    for index, step in enumerate(steps, start=1):
        with cols[(index - 1) % 4]:
            st.metric(f"Step {index}", step)

    with st.expander("Model routing and token efficiency"):
        st.write(
            "The app is structured to use cheaper models for clarification, planning, formatting, ranking, and reports, while reserving stronger reasoning models for gaps, hypotheses, and critique."
        )
        st.dataframe(
            [{"Task": key, "Model": value} for key, value in MODEL_ROUTING.items()],
            use_container_width=True,
        )


def science_tree_selector(prefix: str) -> tuple[str, str, str, str, str]:
    branches = branch_names()
    branch = st.selectbox("Field of science", branches, key=f"{prefix}_branch")

    disciplines = discipline_names(branch)
    discipline = st.selectbox(
        "Branch within field",
        disciplines,
        key=f"{prefix}_{branch}_discipline",
    )

    subfields = subfield_names(branch, discipline)
    subfield = st.selectbox(
        "More specific area",
        subfields,
        key=f"{prefix}_{branch}_{discipline}_subfield",
    )

    topics = topics_for_path(branch, discipline, subfield)
    questions = questions_for_path(branch, discipline, subfield)
    topic = st.selectbox(
        "Specific topic",
        topics,
        key=f"{prefix}_{branch}_{discipline}_{subfield}_topic",
    )
    question = st.selectbox(
        "Possible question to answer",
        questions,
        key=f"{prefix}_{branch}_{discipline}_{subfield}_question",
    )
    st.caption(path_label(branch, discipline, subfield))
    return branch, discipline, subfield, topic, question


def render_project_workflow() -> None:
    st.header("Research Intake")
    col1, col2 = st.columns(2)
    with col1:
        branch, discipline, subfield, suggested_topic, suggested_problem = (
            science_tree_selector("intake")
        )
        broad_domain = st.text_input(
            "Broad scientific domain",
            value=branch,
            help="Examples: physics, biology, chemistry, engineering, climate science.",
        )
        optional_subfield = st.text_input(
            "Optional subfield",
            value=f"{discipline} / {subfield}",
        )
        topic = st.text_input(
            "Edit or narrow the specific topic",
            value=suggested_topic,
            key=f"intake_topic_{branch}_{discipline}_{subfield}_{suggested_topic}",
        )
        problem = st.text_area(
            "Research problem",
            value=suggested_problem,
            key=f"intake_problem_{branch}_{discipline}_{subfield}_{suggested_problem}",
        )
        goal = st.text_area("What do you want to discover or solve?")
    with col2:
        project_mode = st.selectbox(
            "Project mode",
            ["Literature only", "Dataset only", "Literature + dataset"],
            index=2,
        )
        user_level = st.selectbox(
            "User level",
            ["Beginner", "Undergraduate", "Graduate", "Researcher"],
            index=2,
        )
        time_constraint = st.selectbox(
            "Time constraint",
            ["Few hours", "One day", "One week", "Longer project"],
            index=2,
        )
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

    clarification = clarify_domain(broad_domain, optional_subfield, goal)
    literature_plan = plan_literature(broad_domain, optional_subfield, goal)
    with st.expander("Domain clarification", expanded=clarification["needs_clarification"]):
        if clarification["needs_clarification"]:
            st.warning(
                "This domain is still broad. Review the suggested subfields and answer the clarifying questions before generating hypotheses."
            )
        st.write("Suggested subfields")
        st.write(clarification["suggested_subfields"])
        st.write("Feasible research directions")
        st.write(clarification["feasible_research_directions"])
        st.write("Recommended search terms")
        st.write(clarification["recommended_search_terms"])
        st.write("Possible dataset types")
        st.write(clarification["possible_dataset_types"])
        st.write("Questions to answer before continuing")
        st.write(clarification["clarifying_questions"])

    with st.expander("Literature review plan"):
        for label, values in literature_plan.items():
            st.markdown(f"**{label.replace('_', ' ').title()}**")
            st.write(values)

    if st.button("Save Research Project", type="primary"):
        if not broad_domain.strip() or not goal.strip():
            st.error("Please enter at least a broad scientific domain and research goal before saving.")
            return
        project = ResearchProject(
            branch_of_science=f"{broad_domain} ({path_label(branch, discipline, subfield)})",
            specific_topic=topic,
            research_problem=problem,
            goal=goal,
            available_data=data,
            constraints=constraints,
            project_mode=project_mode,
            user_level=user_level,
            time_constraint=time_constraint,
            novelty_level=novelty,
            output_style=output_style,
        )
        save_project(project)
        st.success("Project intake saved.")
        st.rerun()

    project = current_project()
    if not project:
        st.info("Save a project or load demo data to continue through upload, evidence, and hypothesis generation.")
        return

    records = project_records(project)

    st.header("Upload Files")
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

    st.header("Ingest, Extract Evidence, and Index")
    if st.button("Ingest Files"):
        sources = db.list_all(Source, project.id)
        all_evidence: list[Evidence] = []
        with st.spinner("Parsing files, extracting evidence, and rebuilding the local index..."):
            for source in sources:
                if source.raw_path.startswith("demo://"):
                    continue
                try:
                    parsed = parse_source(project.id, source)
                    db.upsert(parsed)
                    evidence = extract_evidence_fallback(
                        project.id, source, parsed.summary_text
                    )
                    all_evidence.extend(evidence)
                    db.bulk_upsert(evidence)
                    db.upsert(source.model_copy(update={"processed_status": "processed"}))
                except Exception as exc:
                    db.upsert(source.model_copy(update={"processed_status": "failed"}))
                    st.error(f"Could not ingest {source.filename}: {exc}")

            EvidenceIndex(project.id).build(db.list_all(Evidence, project.id))
        st.success(f"Ingestion complete. Extracted {len(all_evidence)} evidence items.")
        st.rerun()

    records = project_records(project)

    if records["parsed_contents"]:
        with st.expander("Parsed file summaries"):
            for item in records["parsed_contents"]:
                st.markdown(f"**Source ID:** {item.source_id}")
                st.write(item.summary_text[:1000])

    profiles = dataset_profiles(records)
    if profiles:
        st.subheader("Dataset Profiles")
        for index, profile in enumerate(profiles, start=1):
            with st.expander(f"Dataset {index}: {profile['shape']['rows']} rows x {profile['shape']['columns']} columns"):
                st.write(f"Inferred type: {profile['inferred_dataset_type']}")
                st.write(f"Candidate targets: {', '.join(profile['candidate_target_columns']) or 'None'}")
                st.write(f"Candidate predictors: {', '.join(profile['candidate_predictor_columns']) or 'None'}")
                st.write(f"Recommended analyses: {', '.join(profile['recommended_analyses'])}")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "Column": column,
                                "Type": profile["dtypes"].get(column, ""),
                                "Missing": profile["missing_values"].get(column, 0),
                            }
                            for column in profile["columns"]
                        ]
                    ),
                    use_container_width=True,
                )
                if profile["simple_relationships"]:
                    st.write("Strongest simple relationships")
                    st.dataframe(profile["simple_relationships"], use_container_width=True)

    if records["evidence"]:
        st.subheader("Extracted Evidence")
        for item in records["evidence"]:
            with st.expander(f"{item.evidence_type.title()} | {item.provenance}"):
                st.write(item.text)
                st.caption(
                    f"Variables: {', '.join(item.variables) or 'None'} | "
                    f"Conditions: {', '.join(item.conditions) or 'None'} | "
                    f"Confidence: {item.confidence:.2f}"
                )

        st.subheader("Search Evidence")
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

        with st.expander("Generic Evidence Schema Summary"):
            summary = generic_evidence_summary(project, records["evidence"])
            st.json(summary)

    st.header("Identify Gaps")
    if st.button("Find Gaps"):
        with st.spinner("Comparing evidence, dataset variables, limitations, and missing information..."):
            gaps = generate_gaps_fallback(project, records["evidence"])
            db.bulk_upsert(gaps)
        st.success(f"Created {len(gaps)} gap findings.")
        st.rerun()

    structured_gaps = detect_knowledge_gaps(project, records["evidence"], profiles)
    if structured_gaps:
        st.subheader("Knowledge Gap Table")
        st.dataframe(structured_gaps, use_container_width=True)

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

    st.header("Generate Research Questions")
    if st.button("Generate Research Questions"):
        questions = generate_questions_fallback(
            project, records["gaps"], records["evidence"]
        )
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

    st.header("Generate and Rank Hypotheses")
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

        st.subheader("Scientific Ranking Table")
        ranking_rows = score_hypotheses(records["hypotheses"], profiles)
        st.dataframe(ranking_rows, use_container_width=True)

        st.subheader("Scientific Critique")
        critique_rows = critique_hypotheses(records["hypotheses"], profiles)
        st.dataframe(critique_rows, use_container_width=True)

        st.subheader("Validation Plan")
        validation_rows = build_validation_plan(records["hypotheses"])
        st.dataframe(validation_rows, use_container_width=True)

    render_hypothesis_detail(project, records)
    render_export(project, records)


def render_hypothesis_detail(project: ResearchProject, records: dict[str, list]) -> None:
    st.header("Hypothesis Detail View")
    selected_id = st.session_state.get("selected_hypothesis_id")
    selected = db.get(Hypothesis, selected_id) if selected_id else None
    evidence_lookup = {item.id: item for item in records["evidence"]}
    if selected:
        st.subheader(selected.title)
        st.caption(f"Hypothesis type: {selected.hypothesis_type}")
        st.write(selected.hypothesis)
        st.write(f"**Rationale:** {selected.rationale}")
        st.write(f"**Variables involved:** {', '.join(selected.variables_involved) or 'Needs review'}")
        st.write(f"**Literature support:** {selected.literature_support or 'Needs review'}")
        st.write(f"**Dataset support:** {selected.dataset_support or 'No dataset support identified yet.'}")
        st.write(f"**Possible confounders:** {', '.join(selected.possible_confounders) or 'Needs review'}")
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


def render_export(project: ResearchProject, records: dict[str, list]) -> None:
    st.header("Export")
    export_dir = settings.processed_dir
    json_path = export_dir / f"{project.id}_report.json"
    md_path = export_dir / f"{project.id}_report.md"
    profiles = dataset_profiles(records)
    structured_gaps = detect_knowledge_gaps(project, records["evidence"], profiles)
    critique = critique_hypotheses(records["hypotheses"], profiles)
    ranking = score_hypotheses(records["hypotheses"], profiles)
    validation_plan = build_validation_plan(records["hypotheses"])
    clarification = clarify_domain(
        project.branch_of_science, project.specific_topic, project.goal
    )
    literature_plan = plan_literature(
        project.branch_of_science, project.specific_topic, project.goal
    )
    export_json(
        json_path,
        project,
        records["sources"],
        records["evidence"],
        records["gaps"],
        records["questions"],
        records["hypotheses"],
        domain_clarification=clarification,
        literature_plan=literature_plan,
        dataset_profiles=profiles,
        structured_gaps=structured_gaps,
        critique=critique,
        ranking=ranking,
        validation_plan=validation_plan,
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


def render_brainstorming_studio() -> None:
    st.header("Brainstorming Studio")
    col1, col2 = st.columns(2)
    with col1:
        branch, discipline, subfield, topic, selected_question = science_tree_selector(
            "brainstorm"
        )
        custom_topic = st.text_input("Optional narrower topic")
        goal = st.text_area(
            "What do you want to discover or improve?",
            value=selected_question,
            key=f"brainstorm_goal_{branch}_{discipline}_{subfield}_{selected_question}",
        )
        constraints = st.text_area("What constraints matter right now?")
    with col2:
        available_inputs = st.text_area(
            "What inputs do you already have?",
            value="A few notes, rough assumptions, or a small pilot dataset",
        )
        preferred_lenses = st.multiselect(
            "Idea styles to generate",
            [item["label"] for item in HYPOTHESIS_LENSES],
            default=[item["label"] for item in HYPOTHESIS_LENSES[:3]],
        )
        selected_question_lens = st.selectbox(
            "Question framing lens",
            list(QUESTION_LENSES.keys()),
        )
        include_resources = st.checkbox(
            "Try internet resources for inspiration",
            value=True,
        )

    final_topic = custom_topic.strip() or topic
    st.info(QUESTION_LENSES[selected_question_lens])

    if st.button("Generate Brainstorming Ideas", type="primary"):
        ideas = brainstorm_ideas(
            branch_of_science=path_label(branch, discipline, subfield),
            specific_topic=final_topic,
            goal=goal or "the target outcome",
            constraints=constraints or "resource limits",
            lens_names=preferred_lenses
            or [item["label"] for item in HYPOTHESIS_LENSES[:3]],
            available_inputs=available_inputs,
        )

        st.subheader("Brainstormed Ideas")
        for idea in ideas:
            with st.container(border=True):
                st.markdown(f"### {idea['title']}")
                st.write(f"**Question:** {idea['question']}")
                st.write(f"**Draft concept:** {idea['concept']}")
                st.write(f"**Suggested experiment or simulation:** {idea['experiment']}")
                st.caption(idea["data_needed"])
                st.caption(idea["simulation_summary"])
                st.dataframe(idea["simulation_table"], use_container_width=True)

        st.subheader("Resource Leads")
        if include_resources:
            resources = fetch_research_resources(final_topic, branch)
            if resources:
                for item in resources:
                    summary = item.get("summary") or "No summary available."
                    published = item.get("published") or "Unknown date"
                    st.markdown(
                        f"- **{item['source']}**: [{item['title']}]({item['url']})"
                    )
                    st.caption(f"{published} | {summary}")
            else:
                st.info(
                    "No live resources were returned right now. The page still works offline with guided brainstorming and synthetic simulations."
                )
        else:
            st.caption("Internet resource lookup was skipped for this run.")


st.set_page_config(page_title="General AI Co-Scientist", layout="wide")
render_landing()

with st.sidebar:
    st.subheader("Project Controls")
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
        st.warning("No active project yet. Start in the workflow tab or load demo data.")

workflow_tab, brainstorm_tab = st.tabs(["Project Workflow", "Brainstorming Studio"])
with workflow_tab:
    render_project_workflow()
with brainstorm_tab:
    render_brainstorming_studio()
