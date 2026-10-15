import json
from typing import Any

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="AI Recruitment Screening Assistant",
    page_icon="👥",
    layout="wide",
)

API_URL = st.sidebar.text_input(
    "FastAPI URL",
    value="http://127.0.0.1:8000",
    help="Address of the running FastAPI backend.",
).strip().rstrip("/")

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.7rem; padding-bottom: 2.5rem; }
      div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.22);
        padding: 14px 16px; border-radius: 12px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("AI Recruitment Screening Assistant")
st.caption("AI-assisted CV screening — final decisions remain with HR.")

# ----------------------------- API helpers -----------------------------

def api_get(path: str) -> Any:
    response = requests.get(f"{API_URL}{path}", timeout=20)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict | None = None, timeout: int = 60) -> Any:
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


def api_put(path: str, payload: dict) -> Any:
    response = requests.put(f"{API_URL}{path}", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def show_api_error(error: Exception) -> None:
    if isinstance(error, requests.HTTPError) and error.response is not None:
        try:
            detail = error.response.json()
        except ValueError:
            detail = error.response.text
        st.error(f"API request failed ({error.response.status_code}): {detail}")
    elif isinstance(error, requests.RequestException):
        st.error(
            "Could not connect to FastAPI. Start the backend and check the API URL. "
            f"Details: {error}"
        )
    else:
        st.error(str(error))


def get_candidate_info(item: dict) -> dict:
    value = item.get("candidate", {})
    return value if isinstance(value, dict) else {}


def get_candidate_id(item: dict) -> str:
    candidate = get_candidate_info(item)
    return str(
        item.get("message_id")
        or item.get("id")
        or candidate.get("email")
        or ""
    )


def get_ranking(item: dict) -> dict:
    value = item.get("ranking", {})
    return value if isinstance(value, dict) else {}


def get_all_candidates() -> list[dict]:
    result = api_get("/candidates")
    if isinstance(result, dict):
        result = result.get("candidates", [])
    return result if isinstance(result, list) else []


def status_counts(candidates: list[dict]) -> tuple[int, int, int]:
    qualified = sum(
        bool(get_ranking(item).get("all_must_have_satisfied"))
        for item in candidates
    )
    review = len(candidates) - qualified
    return len(candidates), qualified, review


def extract_resume_text(uploaded_file) -> str:
    suffix = uploaded_file.name.lower().rsplit(".", 1)[-1]
    data = uploaded_file.getvalue()

    if suffix == "pdf":
        from io import BytesIO
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if suffix == "docx":
        from io import BytesIO
        from docx import Document

        document = Document(BytesIO(data))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraph for paragraph in paragraphs if paragraph.strip()).strip()

    if suffix == "txt":
        return data.decode("utf-8", errors="replace").strip()

    raise ValueError("Supported file types are PDF, DOCX, and TXT.")


def flatten_requirement_results(section_name: str, section: Any) -> list[dict]:
    if not isinstance(section, dict):
        return []
    results = section.get("results", [])
    if not isinstance(results, list):
        return []
    flattened = []
    for result in results:
        if not isinstance(result, dict):
            continue
        flattened.append({
            "Section": section_name,
            "Requirement": result.get("requirement", "—"),
            "Status": result.get("status", result.get("result", "—")),
            "Evidence": result.get("evidence") or result.get("reason") or "No evidence returned",
        })
    return flattened


def render_candidate_detail(item: dict) -> None:
    candidate = get_candidate_info(item)
    ranking = get_ranking(item)
    st.markdown("#### Candidate details")
    left, right = st.columns(2)
    with left:
        st.write("**Name:**", candidate.get("name") or "Not provided")
        st.write("**Email:**", candidate.get("email") or "Not provided")
        st.write("**Phone:**", candidate.get("phone") or "Not provided")
        st.write("**Resume file:**", item.get("resume_file") or "Not recorded")
    with right:
        st.write("**Score:**", ranking.get("score", item.get("semantic_similarity", {}).get("similarity_score", "Not available")))
        st.write("**Category:**", ranking.get("category", "Not ranked"))
        st.write("**Must-have criteria satisfied:**", ranking.get("all_must_have_satisfied", "Not evaluated"))

    st.markdown("#### Skills, education, experience, and certificates")
    comparison = item.get("comparison", {})
    rows = []
    for section in ("skills", "education", "experience", "certificates"):
        rows.extend(flatten_requirement_results(section.title(), comparison.get(section)))
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No detailed requirement-comparison results were returned for this candidate.")

    with st.expander("Extracted CV information"):
        st.json(candidate)
    with st.expander("Job requirements used for this result"):
        st.json(item.get("job_requirements", {}))
    with st.expander("Full screening record"):
        st.json(item)


# ----------------------------- Navigation -----------------------------

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Go to",
        ["Dashboard", "Create Job", "Candidates", "HR Decisions"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("AI output supports HR review; it does not make the hiring decision.")

# ----------------------------- Dashboard ------------------------------

if page == "Dashboard":
    st.subheader("Dashboard")
    try:
        candidates = get_all_candidates()
        total, qualified, review = status_counts(candidates)
        jobs = api_get("/jobs")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Candidates", total)
        c2.metric("Qualified", qualified)
        c3.metric("Needs HR review", review)
        c4.metric("Jobs in this session", len(jobs) if isinstance(jobs, list) else 0)
        st.success("FastAPI connection is working.")

        st.markdown("#### Recent candidate results")
        if candidates:
            rows = []
            for item in candidates[:10]:
                person = get_candidate_info(item)
                ranking = get_ranking(item)
                rows.append({
                    "Name": person.get("name") or "Not provided",
                    "Email": person.get("email") or "Not provided",
                    "Score": ranking.get("score", "Not ranked"),
                    "Category": ranking.get("category", "Not ranked"),
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No candidate results are available yet.")
    except (requests.RequestException, ValueError) as error:
        show_api_error(error)

# ----------------------------- Create Job -----------------------------

elif page == "Create Job":
    st.subheader("Create a job")
    st.write("Enter the role and its job description. The backend validates and stores the job.")

    with st.form("job_form", clear_on_submit=False):
        title = st.text_input("Job title", placeholder="Junior Data Analyst")
        description = st.text_area(
            "Job description",
            height=230,
            placeholder="Responsibilities, required skills, education, experience, and preferred qualifications...",
        )
        submitted = st.form_submit_button("Create job", type="primary")

    if submitted:
        if not title.strip() or len(description.strip()) < 20:
            st.warning("Enter a job title and a job description of at least 20 characters.")
        else:
            try:
                job = api_post(
                    "/jobs",
                    {"title": title.strip(), "description": description.strip()},
                    timeout=20,
                )
                st.session_state["active_job"] = job
                st.success("Job created in the backend.")
                st.json(job)
                st.info(
                    "Important: the current /jobs endpoint stores the title and description only. "
                    "Saving HR-edited must-have/preferred requirements needs a matching backend endpoint."
                )
            except (requests.RequestException, ValueError) as error:
                show_api_error(error)

    st.divider()
    st.markdown("#### Jobs currently returned by the API")
    try:
        jobs = api_get("/jobs")
        if jobs:
            st.dataframe(pd.DataFrame(jobs), use_container_width=True, hide_index=True)
        else:
            st.info("No jobs have been created yet.")
    except (requests.RequestException, ValueError) as error:
        show_api_error(error)

# ----------------------------- Candidates -----------------------------

elif page == "Candidates":
    st.subheader("Candidate screening and results")
    tab_saved, tab_upload, tab_rank = st.tabs(
        ["Saved candidates", "Screen one CV", "Refresh ranking"]
    )

    with tab_saved:
        if st.button("Load / refresh candidates", key="load_candidates", type="primary"):
            try:
                st.session_state["candidate_cache"] = get_all_candidates()
            except (requests.RequestException, ValueError) as error:
                show_api_error(error)

        candidates = st.session_state.get("candidate_cache")
        if candidates is None:
            try:
                candidates = get_all_candidates()
                st.session_state["candidate_cache"] = candidates
            except (requests.RequestException, ValueError) as error:
                candidates = []
                show_api_error(error)

        if candidates:
            table_rows = []
            for index, item in enumerate(candidates):
                person = get_candidate_info(item)
                ranking = get_ranking(item)
                table_rows.append({
                    "Index": index,
                    "Name": person.get("name") or "Not provided",
                    "Email": person.get("email") or "Not provided",
                    "Score": ranking.get("score", "Not ranked"),
                    "Category": ranking.get("category", "Not ranked"),
                    "Must-haves met": ranking.get("all_must_have_satisfied", "Not evaluated"),
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

            selected_index = st.selectbox(
                "Select a candidate to inspect",
                options=list(range(len(candidates))),
                format_func=lambda i: (
                    f"{i}: {get_candidate_info(candidates[i]).get('name') or 'Unknown'} "
                    f"— {get_candidate_info(candidates[i]).get('email') or 'no email'}"
                ),
            )
            render_candidate_detail(candidates[selected_index])

            with st.expander("View original resume file location"):
                resume_name = candidates[selected_index].get("resume_file")
                if resume_name:
                    st.write(f"Recorded filename: `{resume_name}`")
                    st.caption(
                        "The current API does not provide a download endpoint for the original CV, "
                        "so the UI cannot download it yet."
                    )
                else:
                    st.info("No resume filename is recorded for this candidate.")
        else:
            st.info("No saved candidates were found. You can test a single CV in the next tab.")

    with tab_upload:
        st.markdown("##### Test a CV against a job description")
        st.caption(
            "This sends the CV text to POST /screen. The current endpoint returns a result but does not save it to the ranked-candidates file."
        )
        uploaded = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])
        selected_job_description = ""
        try:
            jobs = api_get("/jobs")
        except (requests.RequestException, ValueError):
            jobs = []

        if jobs:
            labels = [
                f"{job.get('title', 'Untitled')} — {job.get('id', '')}"
                for job in jobs
            ]
            selected_label = st.selectbox("Use a saved job", labels, key="screen_saved_job")
            selected_job = jobs[labels.index(selected_label)]
            selected_job_description = selected_job.get("description", "")
            st.text_area(
                "Selected job description",
                value=selected_job_description,
                height=150,
                disabled=True,
            )
            use_manual_description = st.checkbox("Use a different job description instead")
        else:
            use_manual_description = True
            st.info("No saved jobs are available. Enter a job description below.")

        if use_manual_description:
            selected_job_description = st.text_area(
                "Job description for this screening",
                value=selected_job_description,
                height=180,
                key="manual_job_description",
            )

        if st.button("Screen uploaded CV", type="primary", key="screen_cv"):
            if uploaded is None:
                st.warning("Upload a PDF, DOCX, or TXT CV first.")
            elif len(selected_job_description.strip()) < 20:
                st.warning("Provide a job description of at least 20 characters.")
            else:
                try:
                    cv_text = extract_resume_text(uploaded)
                    if len(cv_text) < 50:
                        st.warning("Could not extract enough text from this CV. Check whether the PDF is scanned or empty.")
                    else:
                        with st.spinner("Screening the CV with the backend..."):
                            result = api_post(
                                "/screen",
                                {
                                    "cv_text": cv_text,
                                    "job_description": selected_job_description.strip(),
                                },
                                timeout=180,
                            )
                        st.session_state["single_screen_result"] = result
                        st.success("Screening response received.")
                except Exception as error:
                    show_api_error(error)

        single_result = st.session_state.get("single_screen_result")
        if single_result:
            st.markdown("##### Screening result")
            person = single_result.get("candidate", {})
            similarity = single_result.get("semantic_similarity", {})
            col1, col2 = st.columns(2)
            col1.metric("Candidate", person.get("name") or "Not provided")
            col2.metric(
                "Semantic similarity",
                similarity.get("similarity_score", "Not returned"),
            )
            st.json(single_result)
            st.warning(
                "This one-CV test is not automatically added to Saved candidates. "
                "Saving results and running Gmail ingestion from the website require backend endpoints."
            )

    with tab_rank:
        st.write("Recalculate ranking from the candidates currently stored in the backend.")
        top_n = st.number_input("Maximum shortlist size", min_value=1, max_value=100, value=20, step=1)
        if st.button("Recalculate ranking", type="primary"):
            try:
                result = api_post("/candidates/rank", {"top_n": int(top_n)}, timeout=60)
                st.success("Ranking endpoint completed.")
                a, b = st.columns(2)
                a.metric("Candidates processed", result.get("total_candidates", "—"))
                b.metric("Qualified candidates", result.get("qualified_candidates", "—"))
                st.markdown("#### Shortlist returned by API")
                shortlist = result.get("shortlist", [])
                if shortlist:
                    rows = []
                    for item in shortlist:
                        person = get_candidate_info(item)
                        ranking = get_ranking(item)
                        rows.append({
                            "Name": person.get("name") or "Not provided",
                            "Email": person.get("email") or "Not provided",
                            "Score": ranking.get("score", "—"),
                            "Category": ranking.get("category", "—"),
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info("The API returned an empty shortlist. This may mean no candidates satisfied all must-have requirements.")
                st.session_state.pop("candidate_cache", None)
            except (requests.RequestException, ValueError) as error:
                show_api_error(error)

# ----------------------------- HR Decisions ---------------------------

elif page == "HR Decisions":
    st.subheader("Human Resources decisions")
    st.caption("These are HR decisions, not decisions made by the AI model.")

    try:
        candidates = get_all_candidates()
        decisions = api_get("/candidate-decisions")
        if not isinstance(decisions, dict):
            decisions = {}
    except (requests.RequestException, ValueError) as error:
        candidates, decisions = [], {}
        show_api_error(error)

    if not candidates:
        st.info("No saved candidates are available to decide on.")
    else:
        options = list(range(len(candidates)))
        selected_index = st.selectbox(
            "Candidate",
            options=options,
            format_func=lambda i: (
                f"{get_candidate_info(candidates[i]).get('name') or 'Unknown'} — "
                f"{get_candidate_info(candidates[i]).get('email') or 'no email'}"
            ),
        )
        selected_candidate = candidates[selected_index]
        person = get_candidate_info(selected_candidate)
        candidate_id = get_candidate_id(selected_candidate)
        existing = decisions.get(candidate_id, {}) if candidate_id else {}
        if not isinstance(existing, dict):
            existing = {}

        st.write("**Email:**", person.get("email") or "Not provided")
        st.write("**Current saved decision:**", existing.get("decision", "No decision yet"))
        st.write("**Previous notes:**", existing.get("notes") or "No notes")

        with st.form("decision_form"):
            decision = st.selectbox(
                "HR decision",
                ["Shortlist", "Review Later", "Reject"],
                index=(
                    ["Shortlist", "Review Later", "Reject"].index(existing["decision"])
                    if existing.get("decision") in ["Shortlist", "Review Later", "Reject"]
                    else 1
                ),
            )
            notes = st.text_area("Notes", value=existing.get("notes", ""), max_chars=1000)
            save = st.form_submit_button("Save HR decision", type="primary")

        if save:
            try:
                result = api_put(
                    f"/candidates/{selected_index}/decision",
                    {"decision": decision, "notes": notes},
                )
                st.success("Decision saved.")
                st.json(result)
            except (requests.RequestException, ValueError) as error:
                show_api_error(error)

        st.divider()
        st.markdown("#### Decisions already saved")
        if decisions:
            decision_rows = [
                {
                    "Candidate ID": key,
                    "Decision": value.get("decision", "—") if isinstance(value, dict) else "—",
                    "Notes": value.get("notes", "") if isinstance(value, dict) else "",
                }
                for key, value in decisions.items()
            ]
            st.dataframe(pd.DataFrame(decision_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No HR decisions have been saved yet.")

st.divider()
st.caption(
    "Prototype limitation: jobs are held in backend memory, and Gmail ingestion, persistence of single-CV screening, editable requirement storage, and original-CV download need backend support."
)
