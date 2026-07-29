"""
app.py
======
AI Career Assistant — Streamlit frontend.

Upload a resume (PDF) and get:
  1. Resume Skills Analysis — extracted skills as badges + raw text
  2. Job Recommendation      — top 10 matching jobs as cards
  3. Missing Skills          — skill gaps grouped by category + priority

This file only calls backend.py's three functions:
    backend.extract_skills_from_resume(pdf_file)
    backend.recommend_jobs(skills)
    backend.recommend_missing_skills(skills)
No AI/matching logic lives here — it's a pure presentation layer.
"""

import time
import streamlit as st

import backend


# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
def inject_css():
    st.markdown("""
    <style>
    /* whole app */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    .block-container {
        background: #0F172A !important;
    }

    /* top bar / header area */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* removes the extra empty space at the top */
    .block-container {
        padding-top: 0.8rem !important;
    }

    /* optional: if toolbar is visible */   
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)


    st.markdown(
        """
        <style>
        /* ---- global ---- */
        .stApp {
            background: #0F172A;
        }
        html, body, [class*="css"] {
            font-family: 'Segoe UI', Inter, system-ui, sans-serif;
            color: #FFFFFF;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* ---- header banner ---- */
        .app-header {
            background: linear-gradient(120deg, #4F46E5 0%, #3B82F6 50%, #06B6D4 100%);
            padding: 2.1rem 2.4rem;
            border-radius: 18px;
            margin-bottom: 1.6rem;
            box-shadow: 0 8px 24px rgba(79, 70, 229, 0.25);
        }
        .app-header h1 {
            color: #FFFFFF;
            font-size: 2.2rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.02em;
        }
        .app-header p {
            color: #FFFFFF;   /* changed from rgba(255,255,255,0.92) to pure white */
            font-size: 1.02rem;
            margin: 0.5rem 0 0 0;
        }

        

        /* ---- sidebar ---- */
        [data-testid="stSidebar"] {
            background-color: #111827;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            color: #FFFFFF;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
            background-color: #1F2937;
            border-color: #FFFFFF;
        }
        [data-testid="stSidebar"] .stRadio input:checked + div {
            background-color: #4F46E5 !important;
            border-color: #4F46E5 !important;
        }
        [data-testid="stSidebar"] .stRadio input:checked + div + div {
            color: #FFFFFF !important;
        }

        /* ---- metric cards ---- */
        .metric-card {
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
            text-align: center;
            color: white;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.18);
        }
        .metric-card .label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #FFFFFF;   /* changed from rgba(255,255,255,0.85) to pure white */
        }
        .metric-card .value {
            font-size: 2.1rem;
            font-weight: 800;
            margin-top: 0.15rem;
            color: #FFFFFF;
        }

        /* ---- badges/tags ---- */
        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0.6rem 0 0.3rem 0;
        }
        .skill-badge {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            background: #FFFFFF;
            color: #0F172A;
            border: 1px solid #FFFFFF;
        }
        .skill-badge.missing {
            background: #FFFFFF;
            color: #DC2626;
            border: 1px solid #EF4444;
        }
        .skill-badge.matched {
            background: #FFFFFF;
            color: #059669;
            border: 1px solid #10B981;
        }

        /* ---- priority tags ---- */
        .priority-tag {
            display: inline-block;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-left: 0.5rem;
        }
        .priority-High {
            background: #FFFFFF;
            color: #DC2626;
            border: 1px solid #EF4444;
        }
        .priority-Medium {
            background: #FFFFFF;
            color: #B45309;
            border: 1px solid #F59E0B;
        }
        .priority-Low {
            background: #FFFFFF;
            color: #059669;
            border: 1px solid #22C55E;
        }

        /* ---- job card ---- */
        .job-title {
            font-size: 1.25rem;
            font-weight: 800;
            margin-bottom: 0.1rem;
            color: #FFFFFF;
        }
        .job-sub {
            color: #FFFFFF;
            font-size: 0.88rem;
            margin-bottom: 0.5rem;
        }
        .section-label {
            font-weight: 700;
            font-size: 0.85rem;
            color: #FFFFFF;
            margin-top: 0.7rem;
        }

        /* ---- progress bar ---- */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #4F46E5, #06B6D4) !important;
        }
        .stProgress > div > div > div {
            background-color: #FFFFFF !important;
        }

        /* ---- upload area ---- */
        .upload-hint {
            text-align: center;
            color: #FFFFFF;
            font-size: 0.9rem;
            margin-top: -0.5rem;
        }
        [data-testid="stFileUploader"] {
            background-color: #1E293B;
            border: 2px dashed #FFFFFF;
            border-radius: 12px;
            padding: 1rem;
        }
        [data-testid="stFileUploader"]:hover {
            background-color: #273549;
            border-color: #4F46E5;
        }

        /* ---- buttons ---- */
        .stButton > button {
            background-color: #4F46E5;
            color: #FFFFFF;
            border: none;
            font-weight: 600;
        }
        .stButton > button:hover {
            background-color: #6366F1;
        }
        .stButton > button:active {
            background-color: #4338CA;
        }

        /* ---- alerts / messages ---- */
        div.stAlert {
            border-radius: 8px;
            background-color: #1E293B;
            border: 1px solid #FFFFFF;
        }
        div.stAlert [data-testid="stNotification"] {
            background-color: transparent;
        }

        /* ---- dividers ---- */
        hr {
            border-color: #FFFFFF;
        }

        /* ---- expanders ---- */
        .streamlit-expanderHeader {
            color: #0F172A;
        }

        /* ---- force white text on standard Streamlit components ---- */
        .stCaption, .stCaption p, .stCaption span {
            color: #FFFFFF !important;
        }
        .stMetric label, .stMetric div, .stMetric span {
            color: #FFFFFF !important;
        }
        .stAlert div, .stAlert p, .stAlert span {
            color: #FFFFFF !important;
        }
        .stInfo, .stSuccess, .stWarning, .stError {
            color: #FFFFFF !important;
        }
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
        }
        [data-testid="stMetricLabel"] {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_badges(skills, kind="default"):
    """Render a wrapped row of pill-shaped skill badges."""
    if not skills:
        st.caption("None")
        return
    css_class = "skill-badge" + (f" {kind}" if kind != "default" else "")
    html = "".join(f'<span class="{css_class}">{s}</span>' for s in skills)
    st.markdown(f'<div class="badge-row">{html}</div>', unsafe_allow_html=True)


def metric_card(label, value, color_from, color_to):
    st.markdown(
        f"""
        <div class="metric-card" style="background: linear-gradient(135deg, {color_from}, {color_to});">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
def show_header():
    st.markdown(
        """
        <div class="app-header">
            <h1>🧭 AI Career Assistant</h1>
            <p>Upload your resume and let AI analyze your skills, recommend suitable jobs,
            and identify the skills you should learn.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown("## 🧭 AI Career Assistant")
        st.caption("Navigation")

        mode = st.radio(
            "Choose a mode",
            options=["Resume Skills Analysis", "Job Recommendation", "Missing Skills"],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("### ℹ️ About")

        stats = backend.get_dataset_stats()
        skills_count = f"{stats['skills']:,}+" if stats else "500+"
        jobs_count = f"{stats['jobs']:,}+" if stats else "300+"
        companies_count = f"{stats['companies']:,}+" if stats else "150+"

        c1, c2, c3 = st.columns(3)
        c1.metric("🧩 Skills", skills_count)
        c2.metric("💼 Jobs", jobs_count)
        c3.metric("🏢 Companies", companies_count)

        st.caption(
            "Powered by a Mistral-based resume parser and a frequency-filtered "
            "job/skill matching engine trained on real job-posting data."
        )

    return mode


# ---------------------------------------------------------------------------
# Upload section
# ---------------------------------------------------------------------------
def upload_resume():
    st.markdown("### 📄 Upload Your Resume")
    left, center, right = st.columns([1, 2, 1])
    with center:
        uploaded_file = st.file_uploader(
            "Drag and drop your resume here, or click to browse",
            type=["pdf"],
            help="Only PDF files are supported.",
        )
        st.markdown(
            '<p class="upload-hint">PDF only · max recommended size 10 MB</p>',
            unsafe_allow_html=True,
        )

    if uploaded_file is not None:
        size_kb = uploaded_file.size / 1024
        st.success("✅ Resume uploaded successfully!")
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"📁 **Filename:** {uploaded_file.name}")
        with c2:
            st.info(f"💾 **File size:** {size_kb:,.1f} KB")

    return uploaded_file


# ---------------------------------------------------------------------------
# Analysis (calls the backend)
# ---------------------------------------------------------------------------
def run_analysis(resume_file):
    progress = st.progress(0, text="Analyzing resume...")
    with st.spinner("Analyzing resume..."):
        progress.progress(15, text="Warming up models & datasets (first run can take a while)...")
        resume_data = backend.extract_skills_from_resume(resume_file)

        progress.progress(55, text="Matching your skills to job roles...")
        jobs = backend.recommend_jobs(resume_data["skills"], top_n=10)

        progress.progress(85, text="Identifying skill gaps...")
        missing = backend.recommend_missing_skills(resume_data["skills"])

        progress.progress(100, text="Done!")
        time.sleep(0.3)

    progress.empty()
    st.session_state["analysis"] = {
        "resume_data": resume_data,
        "jobs": jobs,
        "missing": missing,
    }
    st.success("✅ Resume analyzed successfully!")


# ---------------------------------------------------------------------------
# Output — metrics
# ---------------------------------------------------------------------------
def show_metrics(analysis):
    skills_found = len(analysis["resume_data"]["skills"])
    jobs = analysis["jobs"]
    recommended_jobs = len(jobs)
    avg_match = round(sum(j["score"] for j in jobs) / len(jobs), 1) if jobs else 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("🎯 Skills Found", skills_found, "#4F46E5", "#3B82F6")
    with c2:
        metric_card("💼 Recommended Jobs", recommended_jobs, "#06B6D4", "#14B8A6")
    with c3:
        metric_card("📊 Average Match", f"{avg_match}%", "#4F46E5", "#06B6D4")


# ---------------------------------------------------------------------------
# Mode 1 — Resume Skills Analysis
# ---------------------------------------------------------------------------
def show_skills(analysis):
    resume_data = analysis["resume_data"]
    skills = resume_data["skills"]

    st.markdown("## 🧩 Extracted Skills")
    render_badges(skills)
    st.caption(f"**Total skills detected:** {len(skills)}")

    st.divider()
    with st.expander("📃 View Raw Text"):
        st.text(resume_data.get("raw_text", "") or "No text extracted.")


# ---------------------------------------------------------------------------
# Mode 2 — Job Recommendation
# ---------------------------------------------------------------------------
def show_jobs(analysis):
    jobs = analysis["jobs"]

    st.markdown("## 💼 Top Recommended Jobs")
    if not jobs:
        st.info("No job matches found yet — try uploading a resume with more listed skills.")
        return

    for job in jobs:
        with st.container(border=True):
            top_row = st.columns([3, 1])
            with top_row[0]:
                st.markdown(
                    f'<div class="job-title">{job["job"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    # f'<div class="job-sub">🏭 {job["industry"]} &nbsp;·&nbsp; '
                    f'📈 based on {job["postings"]} postings</div>',
                    unsafe_allow_html=True,
                )
            with top_row[1]:
                st.metric("Match", f"{job['score']}%")

            st.progress(min(int(job["score"]), 100))

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    '<div class="section-label">✅ Matched Skills</div>',
                    unsafe_allow_html=True,
                )
                render_badges(job["matched_skills"], kind="matched")
            with col_b:
                st.markdown(
                    '<div class="section-label">❌ Missing Skills</div>',
                    unsafe_allow_html=True,
                )
                render_badges(job["missing_skills"], kind="missing")

            st.markdown(
                '<div class="section-label">💡 Reason for Recommendation</div>',
                unsafe_allow_html=True,
            )
            st.write(job["reason"])
        st.write("")  # spacer

    with st.expander("🧠 AI Career Advisor Report (full written analysis)"):
        if st.button("Generate full report", key="career_advice_btn"):
            with st.spinner("Writing your personalized career report..."):
                report = backend.generate_career_advice(
                    jobs, analysis["resume_data"]["skills"]
                )
            st.markdown(report)
        else:
            st.caption(
                "Generates a longer written summary from the AI model — strengths, job ranking, and a learning roadmap."
            )


# ---------------------------------------------------------------------------
# Mode 3 — Missing Skills
# ---------------------------------------------------------------------------
def show_missing_skills(analysis):
    categories = analysis["missing"]

    st.markdown("## 📚 Skills to Learn")
    if not categories:
        st.info(
            "No missing skills detected — your resume already covers the top matched roles well!"
        )
        return

    for category, items in categories.items():
        with st.expander(f"📂 {category}  ({len(items)})", expanded=True):
            for item in items:
                st.markdown(
                    f'{item["skill"]}'
                    f'<span class="priority-tag priority-{item["priority"]}">{item["priority"]}</span>',
                    unsafe_allow_html=True,
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    inject_css()
    show_header()
    mode = show_sidebar()

    resume_file = upload_resume()
    st.divider()

    if resume_file is not None:
        analyze_clicked = st.button(
            "🔍 Analyze Resume", type="primary", use_container_width=True
        )
        if analyze_clicked:
            run_analysis(resume_file)

    analysis = st.session_state.get("analysis")
    if analysis:
        st.divider()
        show_metrics(analysis)
        st.divider()

        if mode == "Resume Skills Analysis":
            show_skills(analysis)
        elif mode == "Job Recommendation":
            show_jobs(analysis)
        elif mode == "Missing Skills":
            show_missing_skills(analysis)
    elif resume_file is None:
        st.info("👆 Upload a resume PDF to get started.")


if __name__ == "__main__":
    main()