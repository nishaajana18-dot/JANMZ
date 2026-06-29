from __future__ import annotations

import streamlit as st

from src.research_catalog import (
    HYPOTHESIS_LENSES,
    QUESTION_LENSES,
    branch_names,
    questions_for_branch,
    topics_for_branch,
)
from src.resources import fetch_research_resources
from src.synthesis import brainstorm_ideas


st.set_page_config(page_title="Brainstorming Studio", layout="wide")
st.title("Brainstorming Studio")
st.caption(
    "Use this page to explore research directions before you have many files. It combines guided prompts, optional internet resources, and clearly labeled synthetic simulations."
)

with st.sidebar:
    st.page_link("app.py", label="Main Workflow")
    st.page_link("pages/1_Brainstorming_Studio.py", label="Brainstorming Studio")

selected_area = st.selectbox("Branch of science", branch_names())
topic_options = topics_for_branch(selected_area)
question_options = questions_for_branch(selected_area)

with st.form("brainstorm_form"):
    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox("Topic within this branch", topic_options)
        selected_question = st.selectbox(
            "Possible question within this branch",
            question_options,
        )
        custom_topic = st.text_input("Optional narrower topic")
        goal = st.text_area("What do you want to discover or improve?", value=selected_question)
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
        include_resources = st.checkbox("Try internet resources for inspiration", value=True)
    submitted = st.form_submit_button("Generate Brainstorming Ideas")

final_topic = custom_topic.strip() or topic

st.subheader("Question prompt")
st.info(QUESTION_LENSES[selected_question_lens])

if submitted:
    ideas = brainstorm_ideas(
        branch_of_science=selected_area,
        specific_topic=final_topic,
        goal=goal or "the target outcome",
        constraints=constraints or "resource limits",
        lens_names=preferred_lenses or [item["label"] for item in HYPOTHESIS_LENSES[:3]],
        available_inputs=available_inputs,
    )

    st.subheader("Brainstormed ideas")
    for idea in ideas:
        with st.container(border=True):
            st.markdown(f"### {idea['title']}")
            st.write(f"**Question:** {idea['question']}")
            st.write(f"**Draft concept:** {idea['concept']}")
            st.write(f"**Suggested experiment or simulation:** {idea['experiment']}")
            st.caption(idea["data_needed"])
            st.caption(idea["simulation_summary"])
            st.dataframe(idea["simulation_table"], use_container_width=True)

    st.subheader("Resource leads")
    if include_resources:
        resources = fetch_research_resources(final_topic, selected_area)
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

st.subheader("How to use this page")
st.markdown(
    "- Start with a broad area and a possible question area.\n"
    "- Pick two or three idea styles to keep the options meaningfully different.\n"
    "- Treat the simulation output as synthetic planning support, not as empirical evidence.\n"
    "- Move the strongest idea into the main workflow once you have better notes, files, or pilot data."
)
