"""AI Test Case Generator - Streamlit application entry point.

A premium, dashboard-style UI that turns software requirements into a full suite
of enterprise QA documentation using an LLM.

Run locally:
    streamlit run app.py
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import streamlit as st

import exporters
from ai_service import AIService, AIServiceError
from config import (
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    SUPPORTED_UPLOAD_FORMATS,
    configure_logging,
    get_settings,
)
from pdf_reader import DocumentReadError, extract_text
from sample_apps import SAMPLE_APPS, get_sample_app
from utils import count_by_category, count_by_field, safe_filename

configure_logging()
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
def inject_css(dark_mode: bool) -> None:
    """Inject theme-aware CSS for a premium SaaS look."""
    if dark_mode:
        bg, card, text, muted, accent = "#0f172a", "#1e293b", "#f8fafc", "#94a3b8", "#6366f1"
    else:
        bg, card, text, muted, accent = "#f8fafc", "#ffffff", "#0f172a", "#64748b", "#4f46e5"

    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        .metric-card {{
            background: {card};
            border: 1px solid {accent}33;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        }}
        .metric-card h3 {{ margin: 0; font-size: 2rem; color: {accent}; }}
        .metric-card p {{ margin: 0; color: {muted}; font-size: 0.85rem; }}
        .hero-title {{ font-size: 2.2rem; font-weight: 800; color: {text}; }}
        .hero-sub {{ color: {muted}; margin-top: -8px; }}
        .badge {{
            display:inline-block; padding:2px 10px; border-radius:999px;
            background:{accent}22; color:{accent}; font-size:0.75rem; font-weight:600;
        }}
        .stDownloadButton button, .stButton button {{ border-radius: 10px; font-weight:600; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
def init_state() -> None:
    defaults: dict[str, Any] = {
        "dark_mode": True,
        "requirements": "",
        "application": "",
        "test_cases": {},
        "flat_rows": [],
        "analysis": {},
        "api_artifacts": {},
        "history": [],
        "generated_at": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #
def run_generation(requirements: str, application: str, include_api: bool) -> None:
    """Execute the full AI generation pipeline with progress feedback."""
    from utils import flatten_test_cases

    service = AIService()
    progress = st.progress(0, text="Starting AI generation...")

    try:
        progress.progress(15, text="Generating test cases across all categories...")
        test_cases = service.generate_test_cases(requirements, application)

        progress.progress(55, text="Analysing requirements (risk, coverage, plans)...")
        analysis = service.generate_analysis(requirements, application)

        api_artifacts: dict[str, Any] = {}
        if include_api:
            progress.progress(80, text="Generating API test artifacts...")
            api_artifacts = service.generate_api_artifacts(requirements, application)

        progress.progress(95, text="Finalising documentation...")
        flat_rows = flatten_test_cases(test_cases)

        st.session_state.update(
            requirements=requirements,
            application=application,
            test_cases=test_cases,
            flat_rows=flat_rows,
            analysis=analysis,
            api_artifacts=api_artifacts,
            generated_at=datetime.utcnow(),
        )
        st.session_state.history.insert(
            0,
            {
                "application": application,
                "when": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                "test_case_count": len(flat_rows),
            },
        )
        progress.progress(100, text="Done!")
        st.success(f"Generated {len(flat_rows)} test cases for {application}.")
    except AIServiceError as exc:
        st.error(f"AI generation failed: {exc}")
    except Exception as exc:  # noqa: BLE001 - top-level UI guard
        logger.exception("Unexpected generation error")
        st.error(f"An unexpected error occurred: {exc}")
    finally:
        progress.empty()


# --------------------------------------------------------------------------- #
# UI sections
# --------------------------------------------------------------------------- #
def render_sidebar() -> tuple[str, str, bool]:
    """Render the input sidebar. Returns (requirements, application, include_api)."""
    with st.sidebar:
        st.markdown(f"### 🧪 {APP_NAME}")
        st.caption(f"v{APP_VERSION}")
        st.session_state.dark_mode = st.toggle("🌙 Dark mode", value=st.session_state.dark_mode)

        settings = get_settings()
        if settings.has_api_key:
            st.markdown('<span class="badge">API key detected</span>', unsafe_allow_html=True)
        else:
            st.warning("No OPENAI_API_KEY set. Add it to your .env to generate.")

        st.divider()
        mode = st.radio("Input source", ["Built-in application", "Upload document"], index=0)

        requirements, application, include_api = "", "", True

        if mode == "Built-in application":
            options = {app.name: key for key, app in SAMPLE_APPS.items()}
            label = st.selectbox("Choose an application", list(options))
            sample = get_sample_app(options[label])
            if sample:
                application = sample.name
                requirements = sample.requirements
                include_api = sample.has_api
                with st.expander("Feature list", expanded=False):
                    for feature in sample.features:
                        st.markdown(f"- {feature}")
        else:
            accepted = list(SUPPORTED_UPLOAD_FORMATS)
            uploaded = st.file_uploader(
                "Upload requirements", type=accepted, accept_multiple_files=False
            )
            application = st.text_input("Application name", value="Custom Requirements")
            include_api = st.checkbox("Generate API artifacts", value=True)
            if uploaded is not None:
                try:
                    requirements = extract_text(uploaded.getvalue(), uploaded.name)
                    st.success(f"Loaded {len(requirements):,} characters.")
                except DocumentReadError as exc:
                    st.error(str(exc))

        st.divider()
        generate = st.button("⚡ Generate QA Documentation", type="primary", use_container_width=True)
        if generate:
            if not requirements.strip():
                st.error("Please provide requirements first.")
            else:
                run_generation(requirements, application, include_api)

    return requirements, application, include_api


def render_dashboard() -> None:
    rows = st.session_state.flat_rows
    st.markdown(f'<div class="hero-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">{APP_TAGLINE}</div>', unsafe_allow_html=True)
    st.write("")

    if not rows:
        st.info("Select an application or upload a document, then click Generate.")
        return

    cols = st.columns(4)
    analysis = st.session_state.analysis or {}
    coverage = (analysis.get("coverage") or {}).get("percentage", "—")
    complexity = (analysis.get("complexity_score") or {}).get("score", "—")
    metrics = [
        ("Test Cases", len(rows)),
        ("Categories", len(st.session_state.test_cases)),
        ("Coverage %", coverage),
        ("Complexity", f"{complexity}/10" if complexity != "—" else "—"),
    ]
    for col, (label, value) in zip(cols, metrics):
        col.markdown(
            f'<div class="metric-card"><h3>{value}</h3><p>{label}</p></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    chart_cols = st.columns(2)
    _render_category_chart(chart_cols[0], rows)
    _render_priority_chart(chart_cols[1], rows)


def _render_category_chart(container: Any, rows: list[dict[str, str]]) -> None:
    try:
        import plotly.express as px
    except ImportError:
        container.bar_chart(count_by_category(rows))
        return
    data = count_by_category(rows)
    fig = px.bar(
        x=list(data.values()),
        y=list(data.keys()),
        orientation="h",
        labels={"x": "Count", "y": "Category"},
        title="Test cases by category",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=420)
    container.plotly_chart(fig, use_container_width=True)


def _render_priority_chart(container: Any, rows: list[dict[str, str]]) -> None:
    try:
        import plotly.express as px
    except ImportError:
        container.bar_chart(count_by_field(rows, "priority"))
        return
    data = count_by_field(rows, "priority")
    fig = px.pie(
        names=list(data.keys()),
        values=list(data.values()),
        title="Priority distribution",
        hole=0.5,
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=420)
    container.plotly_chart(fig, use_container_width=True)


def render_test_cases() -> None:
    rows = st.session_state.flat_rows
    st.subheader("Generated Test Cases")
    if not rows:
        st.info("No test cases yet.")
        return

    categories = sorted({r["category"] for r in rows})
    fcol1, fcol2, fcol3 = st.columns([2, 2, 3])
    selected_cat = fcol1.multiselect("Category", categories, default=[])
    priorities = sorted({r["priority"] for r in rows if r["priority"]})
    selected_pri = fcol2.multiselect("Priority", priorities, default=[])
    query = fcol3.text_input("Search", placeholder="Search feature / expected result...")

    filtered = [
        r
        for r in rows
        if (not selected_cat or r["category"] in selected_cat)
        and (not selected_pri or r["priority"] in selected_pri)
        and (
            not query
            or query.lower() in (r.get("feature", "") + r.get("expected_result", "")).lower()
        )
    ]

    page_size = 15
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start = (page - 1) * page_size
    page_rows = filtered[start : start + page_size]
    st.caption(f"Showing {len(page_rows)} of {len(filtered)} filtered ({len(rows)} total).")

    try:
        import pandas as pd

        st.dataframe(pd.DataFrame(page_rows), use_container_width=True, hide_index=True)
    except ImportError:
        st.table(page_rows)


def render_analysis() -> None:
    analysis = st.session_state.analysis or {}
    st.subheader("AI Analysis")
    if not analysis:
        st.info("No analysis yet.")
        return

    summary = analysis.get("requirement_summary")
    if summary:
        st.markdown("#### Requirement Summary")
        st.write(summary)

    coverage = analysis.get("coverage") or {}
    if coverage:
        st.markdown("#### Coverage")
        st.progress(min(100, int(coverage.get("percentage", 0))) / 100)
        for gap in coverage.get("gaps", []) or []:
            st.markdown(f"- ⚠️ Gap: {gap}")

    for title, key in [("Test Strategy", "test_strategy"), ("Test Plan", "test_plan")]:
        value = analysis.get(key)
        if value:
            with st.expander(title):
                st.markdown(value)


def render_risk() -> None:
    analysis = st.session_state.analysis or {}
    risks = analysis.get("risk_analysis") or []
    st.subheader("Risk Dashboard")
    if not risks:
        st.info("No risk analysis yet.")
        return
    try:
        import pandas as pd

        st.dataframe(pd.DataFrame(risks), use_container_width=True, hide_index=True)
    except ImportError:
        st.table(risks)


def render_traceability() -> None:
    analysis = st.session_state.analysis or {}
    matrix = analysis.get("traceability_matrix") or []
    st.subheader("Requirement Traceability Matrix")
    if not matrix:
        st.info("No traceability matrix yet.")
        return
    normalised = [
        {
            "Requirement ID": m.get("requirement_id", ""),
            "Requirement": m.get("requirement", ""),
            "Test Case IDs": ", ".join(m.get("test_case_ids", []) or []),
        }
        for m in matrix
        if isinstance(m, dict)
    ]
    try:
        import pandas as pd

        st.dataframe(pd.DataFrame(normalised), use_container_width=True, hide_index=True)
    except ImportError:
        st.table(normalised)


def render_downloads() -> None:
    rows = st.session_state.flat_rows
    analysis = st.session_state.analysis
    application = st.session_state.application or "requirements"
    st.subheader("Downloads")
    if not rows:
        st.info("Generate documentation first.")
        return

    stem = safe_filename(application, "qa_documentation")
    cols = st.columns(4)
    try:
        cols[0].download_button(
            "⬇️ Excel", exporters.to_excel(rows, analysis), f"{stem}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        cols[1].download_button(
            "⬇️ CSV", exporters.to_csv(rows), f"{stem}.csv", "text/csv",
            use_container_width=True,
        )
        cols[2].download_button(
            "⬇️ PDF", exporters.to_pdf(rows, analysis, application), f"{stem}.pdf",
            "application/pdf", use_container_width=True,
        )
        md = exporters.to_markdown(rows, analysis, application)
        cols[3].download_button(
            "⬇️ Markdown", md.encode("utf-8"), f"{stem}.md", "text/markdown",
            use_container_width=True,
        )
        with st.expander("Copy Markdown to clipboard"):
            st.code(md, language="markdown")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Export failed")
        st.error(f"Export failed: {exc}")


def render_api() -> None:
    api = st.session_state.api_artifacts or {}
    st.subheader("API Test Artifacts")
    cases = api.get("api_test_cases") or []
    if not cases:
        st.info("No API artifacts (either not generated or the app has no API).")
        return
    try:
        import pandas as pd

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "ID": c.get("test_case_id", ""),
                        "Title": c.get("title", ""),
                        "Method": c.get("method", ""),
                        "Endpoint": c.get("endpoint", ""),
                        "Category": c.get("category", ""),
                        "Status": c.get("expected_status", ""),
                    }
                    for c in cases
                    if isinstance(c, dict)
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    except ImportError:
        st.table(cases)

    if api.get("postman_collection"):
        import json

        st.download_button(
            "⬇️ Postman Collection",
            json.dumps(api["postman_collection"], indent=2).encode("utf-8"),
            "postman_collection.json",
            "application/json",
        )


def render_history() -> None:
    st.subheader("History")
    history = st.session_state.history
    if not history:
        st.info("No runs yet this session.")
        return
    try:
        import pandas as pd

        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
    except ImportError:
        st.table(history)


def render_settings() -> None:
    st.subheader("Settings")
    settings = get_settings()
    st.markdown(
        f"""
        - **Model:** `{settings.openai_model}`
        - **Temperature:** `{settings.temperature}`
        - **Max output tokens:** `{settings.max_output_tokens}`
        - **Request timeout:** `{settings.request_timeout}s`
        - **API key configured:** `{settings.has_api_key}`
        """
    )
    st.caption("Configure these via environment variables or a .env file. Secrets are never stored.")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    init_state()
    inject_css(st.session_state.dark_mode)
    render_sidebar()

    tabs = st.tabs(
        [
            "📊 Dashboard",
            "🧪 Test Cases",
            "🤖 AI Analysis",
            "🔗 Traceability",
            "⚠️ Risk",
            "🌐 API",
            "⬇️ Downloads",
            "🕑 History",
            "⚙️ Settings",
        ]
    )
    with tabs[0]:
        render_dashboard()
    with tabs[1]:
        render_test_cases()
    with tabs[2]:
        render_analysis()
    with tabs[3]:
        render_traceability()
    with tabs[4]:
        render_risk()
    with tabs[5]:
        render_api()
    with tabs[6]:
        render_downloads()
    with tabs[7]:
        render_history()
    with tabs[8]:
        render_settings()


if __name__ == "__main__":
    main()
