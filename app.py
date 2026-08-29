from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_observability_agent.graph.workflow import observability_workflow
from src.data_observability_agent.services.incident_store import IncidentStore


# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Data Observability Agent",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --navy: #0b1f33;
        --blue: #2563eb;
        --cyan: #0ea5e9;
        --slate: #64748b;
        --border: #e2e8f0;
        --surface: #ffffff;
        --background: #f6f8fb;
        --good: #16a34a;
        --warn: #f59e0b;
        --bad: #ef4444;
    }

    .stApp { background: var(--background); color: #334155; }
    .block-container { max-width: 1500px; padding: 1.5rem 2rem 4rem; }

    [data-testid="stMain"] p,
    [data-testid="stMain"] label,
    [data-testid="stMain"] .stCaption,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] {
        color: #475569;
    }

    [data-testid="stSidebar"] {
        background: #0b1f33;
        border-right: 1px solid #173553;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(255,255,255,.06);
        border: 1px solid rgba(255,255,255,.14);
        border-radius: 14px;
        padding: .75rem;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,.05);
        border-color: rgba(255,255,255,.22);
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
        color: #dbeafe !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        color: #0b1f33 !important;
        background: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        color: #0f172a !important;
        background: #ffffff !important;
        border-color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        color: #0f172a !important;
        fill: #0f172a !important;
    }

    h1, h2, h3 { color: var(--navy); letter-spacing: -.025em; }
    h1 { font-size: 2rem !important; }
    hr { border-color: var(--border); }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 1.65rem 1.8rem;
        margin-bottom: 1.25rem;
        border-radius: 20px;
        color: white;
        background: linear-gradient(120deg, #071b2f 0%, #123a63 60%, #0d7490 100%);
        box-shadow: 0 12px 30px rgba(15, 23, 42, .16);
    }
    .hero::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -85px;
        top: -115px;
        border-radius: 50%;
        background: rgba(255,255,255,.08);
    }
    .hero-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
    .hero-kicker {
        margin-bottom: .55rem;
        color: #7dd3fc;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .hero-title { margin: 0; color: white; font-size: 2rem; font-weight: 800; }
    .hero-copy { max-width: 760px; margin: .45rem 0 0; color: #dbeafe; font-size: 1rem; }
    .hero-meta {
        text-align: right;
        color: #bfe4ff;
        font-size: .78rem;
        white-space: nowrap;
    }

    .section-label {
        margin: 1.6rem 0 .8rem;
        color: #0f172a;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .metric-card {
        min-height: 126px;
        padding: 1.05rem 1.1rem;
        border: 1px solid var(--border);
        border-radius: 16px;
        background: var(--surface);
        box-shadow: 0 4px 14px rgba(15, 23, 42, .05);
    }
    .metric-label { color: var(--slate); font-size: .78rem; font-weight: 700; text-transform: uppercase; }
    .metric-value { margin-top: .38rem; color: var(--navy); font-size: 1.65rem; font-weight: 800; }
    .metric-note { margin-top: .2rem; color: #94a3b8; font-size: .78rem; }
    .metric-delta { margin-top: .2rem; font-size: .78rem; font-weight: 700; }
    .delta-up { color: var(--good); }
    .delta-down { color: var(--bad); }
    .delta-flat { color: #94a3b8; }

    .status-card {
        min-height: 105px;
        padding: 1rem;
        border: 1px solid var(--border);
        border-radius: 14px;
        background: white;
    }
    .status-name { margin-bottom: .6rem; color: #334155; font-weight: 750; }
    .badge {
        display: inline-block;
        padding: .27rem .65rem;
        border-radius: 999px;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .025em;
    }
    .healthy { color: #166534; background: #dcfce7; }
    .warning { color: #9a3412; background: #ffedd5; }
    .error { color: #991b1b; background: #fee2e2; }
    .neutral { color: #475569; background: #f1f5f9; }

    .empty-state {
        padding: 2.8rem 1.5rem;
        border: 1px dashed #cbd5e1;
        border-radius: 18px;
        background: rgba(255,255,255,.72);
        text-align: center;
    }
    .empty-title { color: var(--navy); font-size: 1.2rem; font-weight: 800; }
    .empty-copy { max-width: 580px; margin: .4rem auto 0; color: var(--slate); }

    .stButton > button,
    [data-testid="stSidebar"] .stButton > button {
        min-height: 46px;
        border: 0;
        border-radius: 11px;
        color: white;
        background: linear-gradient(90deg, #2563eb, #0284c7);
        font-weight: 750;
        box-shadow: 0 5px 12px rgba(37, 99, 235, .2);
    }
    .stButton > button:hover { color: white; border: 0; background: #1d4ed8; }
    [data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
    [data-baseweb="tab-list"] {
        gap: .25rem;
        border-bottom: 1px solid #dbe3ed;
    }
    [data-baseweb="tab"] {
        border-radius: 9px 9px 0 0;
        padding: .65rem 1rem;
        color: #475569 !important;
        background: #eef2f7;
    }
    [data-baseweb="tab"] p { color: #475569 !important; font-weight: 700; }
    [data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: #1d4ed8;
    }
    [data-baseweb="tab"][aria-selected="true"] p { color: #ffffff !important; }

    [data-testid="stExpander"] {
        border: 1px solid #dbe3ed;
        border-radius: 12px;
        background: #ffffff;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #0f172a !important;
        font-weight: 700;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div { color: inherit !important; }

    [data-baseweb="popover"] li,
    [data-baseweb="popover"] [role="option"] {
        color: #0f172a !important;
        background: #ffffff !important;
    }
    [data-baseweb="popover"] [aria-selected="true"] {
        color: #0b1f33 !important;
        background: #dbeafe !important;
    }

    @media (max-width: 900px) {
        .block-container { padding: 1rem 1rem 3rem; }
        .hero { padding: 1.3rem; }
        .hero-title { font-size: 1.65rem; }
        .metric-card { min-height: 112px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

SEVERITY_ORDER = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3, "UNKNOWN": 4}


def status_class(status: str) -> str:
    normalized = status.upper()
    if normalized == "HEALTHY":
        return "healthy"
    if normalized in {"ISSUES_DETECTED", "STALE"}:
        return "warning"
    if normalized == "NO_BASELINE":
        return "neutral"
    if normalized == "ERROR":
        return "error"
    return "neutral"


def metric_card(label: str, value: str, note: str, delta: float | None = None, delta_suffix: str = "") -> None:
    delta_html = ""
    if delta is not None:
        if delta > 0:
            delta_html = f'<div class="metric-delta delta-up">▲ {delta:+.0f}{delta_suffix} vs last run</div>'
        elif delta < 0:
            delta_html = f'<div class="metric-delta delta-down">▼ {delta:+.0f}{delta_suffix} vs last run</div>'
        else:
            delta_html = '<div class="metric-delta delta-flat">— unchanged vs last run</div>'
    # Built as a single-line string (no indentation/blank lines) so an empty
    # delta_html can't leave a blank line inside the <div> block — Streamlit's
    # markdown parser treats that as the HTML block ending early, which then
    # renders any leftover closing tags as a literal code snippet.
    card_html = (
        '<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-note">{note}</div>'
        f'{delta_html}'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def health_gauge(score: int) -> go.Figure:
    color = "#16a34a" if score >= 90 else "#f59e0b" if score >= 70 else "#ef4444"
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 34, "color": "#0b1f33"}},
            title={"text": "Overall health", "font": {"size": 15, "color": "#64748b"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "white"},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "#e2e8f0",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 90], "color": "#fef3c7"},
                    {"range": [90, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    figure.update_layout(
        height=255,
        margin=dict(l=28, r=28, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
    )
    return figure


def issue_breakdown_chart(issues: list[dict[str, Any]]) -> go.Figure:
    counts: dict[str, int] = {}
    for issue in issues:
        issue_type = str(issue.get("type", "UNKNOWN")).replace("_", " ").title()
        counts[issue_type] = counts.get(issue_type, 0) + 1
    breakdown_df = pd.DataFrame({"Type": list(counts.keys()), "Count": list(counts.values())}).sort_values(
        "Count", ascending=True
    )
    figure = px.bar(
        breakdown_df,
        x="Count",
        y="Type",
        orientation="h",
        color_discrete_sequence=["#2563eb"],
    )
    figure.update_layout(
        height=max(180, 40 * len(breakdown_df) + 60),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="",
    )
    return figure


def build_report_payload(result: dict[str, Any], filename: str, rows: int, columns: int) -> dict[str, Any]:
    incident = result.get("incident_result", {})
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source_file": filename,
        "rows": rows,
        "columns": columns,
        "health_score": incident.get("health_score"),
        "severity": incident.get("severity"),
        "issues": result.get("issues", []),
        "drift_result": result.get("drift_result", {}),
        "anomaly_result": result.get("anomaly_result", {}),
        "rca": result.get("rca_result", {}).get("analysis", ""),
    }


@st.cache_resource
def get_store() -> IncidentStore:
    return IncidentStore()


store = get_store()


# --------------------------------------------------------------------------
# Hero
# --------------------------------------------------------------------------

last_run_note = ""
if st.session_state.get("observability_filename"):
    last_run_note = (
        f'<div class="hero-meta">Last run<br><strong>{st.session_state["observability_filename"]}</strong></div>'
    )

# Single-line, unindented string — same reasoning as metric_card above: an
# empty last_run_note must never leave a blank line inside the <div> block.
hero_html = (
    '<div class="hero"><div class="hero-top"><div>'
    '<div class="hero-kicker">Intelligent data reliability</div>'
    '<div class="hero-title">Data Observability Agent</div>'
    '<div class="hero-copy">Monitor quality, freshness, volume, schema and distribution '
    'drift—then turn detected signals into a clear, AI-assisted root-cause analysis.</div>'
    '</div>'
    f'{last_run_note}'
    '</div></div>'
)
st.markdown(hero_html, unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🔭 Analysis setup")
    st.caption("Upload the latest dataset and optionally a trusted baseline.")

    current_file = st.file_uploader(
        "Current dataset",
        type=["csv"],
        help="Required CSV containing the data you want to assess.",
    )
    baseline_file = st.file_uploader(
        "Baseline dataset",
        type=["csv"],
        help="Optional reference CSV used for volume, schema and distribution drift.",
    )

    current_df: pd.DataFrame | None = None
    baseline_df: pd.DataFrame | None = None
    read_error = False

    if current_file is not None:
        try:
            current_df = pd.read_csv(current_file)
            if current_df.empty:
                st.warning("Current CSV has no rows.")
            else:
                st.success(f"Current: {len(current_df):,} rows · {len(current_df.columns)} cols")
        except Exception as exc:
            st.error(f"Could not read current CSV: {exc}")
            read_error = True

    if baseline_file is not None:
        try:
            baseline_df = pd.read_csv(baseline_file)
            st.success(f"Baseline: {len(baseline_df):,} rows · {len(baseline_df.columns)} cols")
        except Exception as exc:
            st.error(f"Could not read baseline CSV: {exc}")
            read_error = True

    timestamp_column: str | None = None
    if current_df is not None and not current_df.empty:
        selected_timestamp = st.selectbox(
            "Timestamp column",
            ["Not selected", *current_df.columns.tolist()],
            help="Used to measure whether the latest record is fresh.",
        )
        timestamp_column = None if selected_timestamp == "Not selected" else selected_timestamp

    button_col, reset_col = st.columns([2, 1])
    with button_col:
        run_analysis = st.button(
            "Run analysis",
            type="primary",
            use_container_width=True,
            disabled=current_df is None or current_df.empty or read_error,
        )
    with reset_col:
        if st.button("Reset", use_container_width=True):
            for key in ("observability_result", "observability_rows", "observability_columns", "observability_filename", "saved_current_result"):
                st.session_state.pop(key, None)
            st.rerun()

    st.divider()
    st.caption("Checks included")
    st.markdown(
        "✓ Completeness & duplicates  \n✓ Freshness  \n✓ Volume change  \n"
        "✓ Schema & distribution drift  \n✓ Record anomalies"
    )


if run_analysis and current_df is not None:
    previous_score = None
    if st.session_state.get("observability_result"):
        previous_score = st.session_state["observability_result"].get("incident_result", {}).get("health_score")

    st.session_state["saved_current_result"] = False
    try:
        with st.spinner("Running observability agents and generating insights..."):
            st.session_state["observability_result"] = observability_workflow.invoke(
                {
                    "current_df": current_df,
                    "baseline_df": baseline_df,
                    "timestamp_column": timestamp_column,
                }
            )
            st.session_state["observability_rows"] = len(current_df)
            st.session_state["observability_columns"] = len(current_df.columns)
            st.session_state["observability_filename"] = current_file.name
            st.session_state["observability_previous_score"] = previous_score
        st.toast("Analysis completed", icon="✅")
    except Exception as exc:
        st.error(f"Analysis could not be completed: {exc}")


# --------------------------------------------------------------------------
# Main content
# --------------------------------------------------------------------------

result: dict[str, Any] | None = st.session_state.get("observability_result")

if result is None:
    st.markdown(
        """
        <div class="empty-state">
            <div style="font-size:2.2rem">📊</div>
            <div class="empty-title">Your data health overview will appear here</div>
            <div class="empty-copy">
                Upload a current CSV in the sidebar. Add a baseline to unlock volume,
                schema and distribution-drift comparisons, then run the analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    incident = result.get("incident_result", {})
    profile = result.get("current_profile", {})
    issues = result.get("issues", [])
    anomaly = result.get("anomaly_result", {})
    score = int(incident.get("health_score", 0))
    severity = str(incident.get("severity", "UNKNOWN"))
    rows = int(st.session_state.get("observability_rows", profile.get("row_count", 0)))
    columns = int(st.session_state.get("observability_columns", profile.get("column_count", 0)))
    previous_score = st.session_state.get("observability_previous_score")
    score_delta = (score - previous_score) if isinstance(previous_score, (int, float)) else None

    top_bar, download_bar = st.columns([4, 1])
    with top_bar:
        st.markdown('<div class="section-label">Health overview</div>', unsafe_allow_html=True)
    with download_bar:
        report_payload = build_report_payload(
            result, st.session_state.get("observability_filename", "dataset.csv"), rows, columns
        )
        st.download_button(
            "⬇ Export report",
            data=json.dumps(report_payload, indent=2, default=str),
            file_name="observability_report.json",
            mime="application/json",
            use_container_width=True,
        )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Health score", f"{score}/100", "Overall reliability score", delta=score_delta)
    with m2:
        metric_card("Severity", severity.title(), "Highest detected risk")
    with m3:
        metric_card("Incidents", f"{len(issues):,}", "Signals requiring attention")
    with m4:
        metric_card("Dataset", f"{rows:,} rows", f"{columns:,} columns analyzed")

    overview_tab, profile_tab, incidents_tab, drift_tab, rca_tab, history_tab = st.tabs(
        ["Overview", "Data profile", "Incidents", "Drift & anomalies", "AI root cause", "History"]
    )

    # ---------------------------------------------------------------- Overview
    with overview_tab:
        left, right = st.columns([1, 1.55], gap="large")
        with left:
            st.plotly_chart(health_gauge(score), use_container_width=True, config={"displayModeBar": False})
        with right:
            st.markdown("### Agent status")
            agents = [
                ("Data quality", result.get("quality_result", {})),
                ("Freshness", result.get("freshness_result", {})),
                ("Volume", result.get("volume_result", {})),
                ("Drift", result.get("drift_result", {})),
            ]
            cols = st.columns(2)
            for index, (name, agent_result) in enumerate(agents):
                status = str(agent_result.get("status", "UNKNOWN"))
                with cols[index % 2]:
                    st.markdown(
                        f'<div class="status-card"><div class="status-name">{name}</div>'
                        f'<span class="badge {status_class(status)}">{status.replace("_", " ")}</span></div>',
                        unsafe_allow_html=True,
                    )
                    st.write("")

        if issues:
            st.markdown("### Incidents by type")
            st.plotly_chart(issue_breakdown_chart(issues), use_container_width=True, config={"displayModeBar": False})

    # ------------------------------------------------------------- Data profile
    with profile_tab:
        st.markdown("### Dataset profile")
        p1, p2 = st.columns(2, gap="large")

        schema_items = list(profile.get("schema", {}).items())
        null_items = profile.get("null_percentages", {})

        schema_df = pd.DataFrame(schema_items, columns=["Column", "Data type"])
        null_df = pd.DataFrame(
            {"Column": list(null_items.keys()), "Null %": list(null_items.values())}
        ).sort_values("Null %", ascending=False)

        with p1:
            st.caption("Schema")
            search = st.text_input("Filter columns", key="schema_filter", placeholder="Search column name…")
            filtered_schema = schema_df[schema_df["Column"].str.contains(search, case=False, na=False)] if search else schema_df
            if filtered_schema.empty:
                st.info("No columns match that filter.")
            else:
                st.dataframe(filtered_schema, use_container_width=True, hide_index=True, height=350)
        with p2:
            st.caption("Completeness")
            if null_df.empty:
                st.info("No completeness data available.")
            else:
                st.dataframe(
                    null_df,
                    use_container_width=True,
                    hide_index=True,
                    height=350,
                    column_config={
                        "Null %": st.column_config.ProgressColumn("Null %", min_value=0, max_value=100, format="%.2f%%")
                    },
                )

        with st.expander("Preview uploaded data"):
            if current_df is not None:
                st.dataframe(current_df.head(50), use_container_width=True, hide_index=True)
            else:
                st.info("Re-upload the current dataset to preview its rows.")

    # --------------------------------------------------------------- Incidents
    with incidents_tab:
        st.markdown("### Detected incidents")
        if not issues:
            st.success("No significant data-quality incidents were detected.")
        else:
            st.warning(f"{len(issues)} incident signal(s) require review.")

            issue_types = sorted({str(issue.get("type", "UNKNOWN")).replace("_", " ").title() for issue in issues})
            filter_col, sort_col = st.columns([2, 1])
            with filter_col:
                selected_types = st.multiselect("Filter by type", issue_types, default=issue_types)
            with sort_col:
                sort_by_severity = st.checkbox("Sort by severity", value=True)

            filtered_issues = [
                issue for issue in issues
                if str(issue.get("type", "UNKNOWN")).replace("_", " ").title() in selected_types
            ]
            if sort_by_severity:
                filtered_issues = sorted(
                    filtered_issues,
                    key=lambda i: SEVERITY_ORDER.get(str(i.get("severity", "UNKNOWN")).upper(), 4),
                )

            if not filtered_issues:
                st.info("No incidents match the selected filters.")
            for index, issue in enumerate(filtered_issues, start=1):
                issue_type = str(issue.get("type", "UNKNOWN")).replace("_", " ").title()
                issue_severity = str(issue.get("severity", "")).title()
                message = issue.get("message", "Review the structured evidence below.")
                label = f"{index}. {issue_type}" + (f" · {issue_severity}" if issue_severity else "")
                with st.expander(label, expanded=index == 1):
                    st.write(message)
                    st.json(issue)

    # ---------------------------------------------------------- Drift & anomalies
    with drift_tab:
        drift_result = result.get("drift_result", {})
        distribution = drift_result.get("distribution_drift", [])
        d1, d2 = st.columns(2)
        with d1:
            metric_card("Anomalous records", f"{anomaly.get('anomaly_count', 0):,}", "Isolation Forest signals")
        with d2:
            metric_card("Anomaly rate", f"{anomaly.get('anomaly_percentage', 0)}%", "Share of analyzed records")

        st.write("")
        if distribution:
            drift_df = pd.DataFrame(distribution)
            drift_df["status"] = drift_df["drift_detected"].map({True: "Drift detected", False: "Stable"})
            drifted_count = int(drift_df["drift_detected"].sum())
            st.caption(f"{drifted_count} of {len(drift_df)} compared columns show drift against the baseline.")
            figure = px.bar(
                drift_df.sort_values("ks_statistic", ascending=False),
                x="column",
                y="ks_statistic",
                color="status",
                color_discrete_map={"Drift detected": "#ef4444", "Stable": "#38bdf8"},
                labels={"ks_statistic": "KS statistic", "column": "Column"},
            )
            figure.update_layout(
                height=390,
                margin=dict(l=20, r=20, t=30, b=20),
                plot_bgcolor="white",
                paper_bgcolor="rgba(0,0,0,0)",
                legend_title_text="",
            )
            st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})
            st.dataframe(drift_df, use_container_width=True, hide_index=True)
        else:
            st.info("No distribution comparison is available. Upload a baseline dataset to enable drift analysis.")

    # ------------------------------------------------------------- AI root cause
    with rca_tab:
        st.markdown("### AI root-cause analysis")
        rca = result.get("rca_result", {})
        rca_status = str(rca.get("status", "ERROR"))
        if rca_status == "ANALYZED":
            st.success("Root-cause analysis completed from the detected evidence.")
            st.markdown(rca.get("analysis", ""))
        elif rca_status == "HEALTHY":
            st.success(rca.get("analysis", "No significant incidents were detected."))
        else:
            st.warning("The checks completed, but AI root-cause analysis is temporarily unavailable.")
            with st.expander("Technical details"):
                st.code(rca.get("error") or rca.get("analysis") or "Unknown RCA error")

    # ------------------------------------------------------------------- History
    with history_tab:
        st.markdown("### Incident history")
        history = store.get_all()
        if history:
            history_df = pd.DataFrame(
                history,
                columns=["ID", "Timestamp", "Health score", "Severity", "Incident count"],
            )
            history_df["Timestamp"] = pd.to_datetime(history_df["Timestamp"], errors="coerce")
            history_df = history_df.sort_values("Timestamp")

            trend_figure = px.line(
                history_df,
                x="Timestamp",
                y="Health score",
                markers=True,
                color_discrete_sequence=["#2563eb"],
            )
            trend_figure.update_layout(
                height=280,
                margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor="white",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, 100]),
            )
            st.plotly_chart(trend_figure, use_container_width=True, config={"displayModeBar": False})
            st.dataframe(
                history_df.sort_values("Timestamp", ascending=False),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No historical incidents have been saved yet.")

    if issues and not st.session_state.get("saved_current_result", False):
        rca = result.get("rca_result", {})
        rca_text = rca.get("analysis", "") if rca.get("status") == "ANALYZED" else ""
        try:
            store.save(incident_result=incident, issues=issues, rca=rca_text)
            st.session_state["saved_current_result"] = True
            st.toast("Incident saved to history", icon="💾")
        except Exception as exc:
            st.warning(f"Analysis completed, but the incident could not be saved: {exc}")