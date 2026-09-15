"""MissionGuard AI — Streamlit Dashboard.

Launch:
    python -m streamlit run src/dashboard/app.py

Requires the FastAPI backend running on http://localhost:8000 (or
MISSIONGUARD_API_URL env var).
"""

from __future__ import annotations

import os
from typing import Any

import streamlit as st

from src.dashboard.api_client import (
    AssetNotFoundError,
    BackendUnavailableError,
    MissionGuardClient,
)

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="MissionGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Constants ─────────────────────────────────────────────────────────────────
API_URL = os.environ.get("MISSIONGUARD_API_URL", "http://localhost:8000")

RISK_COLOURS = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
READINESS_COLOURS = {"READY": "🟢", "WARNING": "⚠️", "NOT_READY": "🚫"}
READINESS_BADGE = {
    "READY": "✅ READY",
    "WARNING": "⚠️ WARNING",
    "NOT_READY": "🚫 NOT READY",
}


# ── Styling ───────────────────────────────────────────────────────────────────
def _inject_css() -> None:
    st.markdown(
        """
        <style>
        /* ── Global font override ─────────────────────────────────────────── */
        html, body, [class*="css"], .stMarkdown, .stMetric,
        .stSelectbox, .stDataFrame, button, input, textarea, label {
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif !important;
        }

        /* ── KPI card ────────────────────────────────────────────────────── */
        .kpi-card {
            background: #1e2330;
            border-radius: 10px;
            padding: 18px 20px 14px 20px;
            text-align: center;
            border: 1px solid #2d3348;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .kpi-label {
            font-size: 0.72rem;
            font-weight: 500;
            color: #8892a4;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 2.1rem;
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.01em;
        }
        .kpi-green  { color: #22c55e; }
        .kpi-yellow { color: #eab308; }
        .kpi-red    { color: #ef4444; }
        .kpi-blue   { color: #60a5fa; }
        .kpi-white  { color: #f1f5f9; }

        /* ── Section heading ─────────────────────────────────────────────── */
        .section-heading {
            font-size: 0.78rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 0 0 12px 0;
            padding-bottom: 7px;
            border-bottom: 1px solid #2d3348;
        }

        /* ── Asset detail header ─────────────────────────────────────────── */
        .asset-header {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: -0.01em;
            margin-bottom: 4px;
        }
        .asset-subheader {
            font-size: 0.82rem;
            font-weight: 400;
            color: #64748b;
            letter-spacing: 0.02em;
            margin-bottom: 16px;
        }

        /* ── Metric labels — tighter font ───────────────────────────────── */
        [data-testid="stMetricLabel"] p {
            font-size: 0.72rem !important;
            font-weight: 500 !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.07em !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.45rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
            white-space: nowrap !important;
            overflow: visible !important;
        }

        /* ── Disclaimer ──────────────────────────────────────────────────── */
        .disclaimer {
            background: #1e2330;
            border-left: 3px solid #f59e0b;
            padding: 10px 14px;
            border-radius: 4px;
            font-size: 0.78rem;
            color: #94a3b8;
            line-height: 1.6;
        }

        /* ── Risk factor bullet ──────────────────────────────────────────── */
        .risk-factor {
            background: #1e2330;
            border-left: 3px solid #ef4444;
            padding: 8px 14px;
            border-radius: 4px;
            margin-bottom: 7px;
            font-size: 0.87rem;
            font-weight: 400;
            color: #e2e8f0;
            line-height: 1.5;
        }

        /* ── Recommended action box ──────────────────────────────────────── */
        .action-box {
            background: #0f1f35;
            border: 1px solid #1d4ed8;
            border-radius: 8px;
            padding: 14px 16px;
            font-size: 0.88rem;
            font-weight: 400;
            color: #bfdbfe;
            line-height: 1.65;
        }

        /* ── About page styles ───────────────────────────────────────────── */
        .about-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e2330 100%);
            border: 1px solid #2d3348;
            border-radius: 14px;
            padding: 36px 40px;
            margin-bottom: 24px;
        }
        .about-hero h1 {
            font-size: 2rem;
            font-weight: 800;
            color: #f1f5f9;
            letter-spacing: -0.02em;
            margin: 0 0 8px 0;
        }
        .about-hero p {
            font-size: 1.05rem;
            font-weight: 400;
            color: #94a3b8;
            line-height: 1.7;
            margin: 0;
        }
        .about-card {
            background: #1e2330;
            border: 1px solid #2d3348;
            border-radius: 10px;
            padding: 22px 24px;
            margin-bottom: 16px;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        .about-card h3 {
            font-size: 0.75rem;
            font-weight: 600;
            color: #60a5fa;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 0 0 10px 0;
            flex-shrink: 0;
        }
        .about-card p {
            font-size: 0.9rem;
            font-weight: 400;
            color: #cbd5e1;
            line-height: 1.65;
            margin: 0;
            flex: 1;
        }
        .flow-step {
            background: #1e2330;
            border: 1px solid #2d3348;
            border-radius: 10px;
            padding: 18px 20px;
            text-align: center;
            position: relative;
            min-height: 145px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
        }
        .flow-step .step-icon {
            font-size: 1.8rem;
            margin-bottom: 8px;
        }
        .flow-step .step-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 5px;
            letter-spacing: -0.01em;
        }
        .flow-step .step-desc {
            font-size: 0.75rem;
            font-weight: 400;
            color: #64748b;
            line-height: 1.5;
        }
        .flow-arrow {
            font-size: 1.4rem;
            color: #334155;
            text-align: center;
            padding-top: 28px;
        }
        .tech-pill {
            display: inline-block;
            background: #0f1f35;
            border: 1px solid #1d4ed8;
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 0.78rem;
            font-weight: 500;
            color: #93c5fd;
            margin: 3px 4px 3px 0;
        }
        .team-card {
            background: #1e2330;
            border: 1px solid #2d3348;
            border-radius: 10px;
            padding: 18px 20px;
            text-align: center;
            min-height: 130px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .team-card .team-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 4px;
        }
        .team-card .team-role {
            font-size: 0.75rem;
            font-weight: 400;
            color: #60a5fa;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        /* ── Hide Streamlit chrome for cleaner demo ──────────────────────── */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_data(ttl=60, show_spinner=False)
def _fetch_all_assets(api_url: str) -> list[dict[str, Any]]:
    """Fetch all assets; cached for 60 s so page interactions don't re-hit the API."""
    client = MissionGuardClient(base_url=api_url)
    return client.get_assets()


def _kpi_card(label: str, value: str | int, colour_class: str) -> str:
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value {colour_class}">{value}</div>'
        f"</div>"
    )


def _readiness_bar(counts: dict[str, int], total: int) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        pct = round(100 * counts.get("READY", 0) / max(total, 1))
        st.metric("✅ READY", counts.get("READY", 0), f"{pct}% of fleet")
    with c2:
        pct = round(100 * counts.get("WARNING", 0) / max(total, 1))
        st.metric("⚠️ WARNING", counts.get("WARNING", 0), f"{pct}% of fleet")
    with c3:
        pct = round(100 * counts.get("NOT_READY", 0) / max(total, 1))
        st.metric("🚫 NOT READY", counts.get("NOT_READY", 0), f"{pct}% of fleet")


def _risk_bar(counts: dict[str, int], total: int) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        pct = round(100 * counts.get("LOW", 0) / max(total, 1))
        st.metric("🟢 LOW RISK", counts.get("LOW", 0), f"{pct}% of fleet")
    with c2:
        pct = round(100 * counts.get("MEDIUM", 0) / max(total, 1))
        st.metric("🟡 MEDIUM RISK", counts.get("MEDIUM", 0), f"{pct}% of fleet")
    with c3:
        pct = round(100 * counts.get("HIGH", 0) / max(total, 1))
        st.metric("🔴 HIGH RISK", counts.get("HIGH", 0), f"{pct}% of fleet")


def _priority_queue_table(
    assets: list[dict[str, Any]], client: MissionGuardClient, top_n: int = 15
) -> None:
    sorted_assets = sorted(
        assets, key=lambda a: float(a.get("failure_probability", 0)), reverse=True
    )
    top = sorted_assets[:top_n]

    rows = []
    for rank, asset in enumerate(top, start=1):
        readiness = asset.get("readiness_status", "")
        risk = asset.get("risk_level", "")
        rows.append(
            {
                "Rank": rank,
                "Asset ID": asset.get("asset_id", ""),
                "Type": asset.get("asset_type", ""),
                "Health": f"{asset.get('health_score', 0):.1f}",
                "Risk": f"{RISK_COLOURS.get(risk, '')} {risk}",
                "Readiness": f"{READINESS_COLOURS.get(readiness, '')} {readiness}",
                "Action": asset.get("recommended_action", ""),
            }
        )

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _asset_detail(asset_id: str, client: MissionGuardClient) -> None:
    """Render the detail panel for a selected asset — fixed fonts + no truncation."""
    try:
        status   = client.get_asset_status(asset_id)
        risk     = client.get_asset_risk(asset_id)
        priority = client.get_asset_priority(asset_id)
    except AssetNotFoundError:
        st.error(f"Asset **{asset_id}** was not found in the backend.")
        return
    except BackendUnavailableError as exc:
        st.error(str(exc))
        return

    readiness  = status.get("readiness_status", "UNKNOWN")
    risk_level = risk.get("risk_level", "UNKNOWN")
    health     = float(risk.get("health_score", 0))
    prob       = float(risk.get("failure_probability", 0))
    p_score    = float(priority.get("priority_score", 0))
    p_rank     = priority.get("priority_rank", "?")
    p_total    = priority.get("total_assets", 100)
    asset_type = status.get("asset_type", "")

    # ── identity row ─────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="asset-header">{asset_id} &mdash; {asset_type}</div>'
        f'<div class="asset-subheader">Asset detail · Risk analysis · Maintenance priority</div>',
        unsafe_allow_html=True,
    )

    # ── core metrics — use custom HTML so labels/values never truncate ────────
    risk_icon     = RISK_COLOURS.get(risk_level, "")
    readiness_icon = READINESS_COLOURS.get(readiness, "")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Health Score</div>'
            f'<div class="kpi-value kpi-{"green" if health >= 65 else "yellow" if health >= 40 else "red"}">'
            f'{health:.1f}<span style="font-size:1rem;font-weight:400;color:#64748b"> / 100</span></div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        prob_class = "kpi-red" if prob >= 0.65 else "kpi-yellow" if prob >= 0.35 else "kpi-green"
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Failure Probability</div>'
            f'<div class="kpi-value {prob_class}">{prob:.1%}</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        risk_class = "kpi-red" if risk_level == "HIGH" else "kpi-yellow" if risk_level == "MEDIUM" else "kpi-green"
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Risk Level</div>'
            f'<div class="kpi-value {risk_class}">{risk_icon} {risk_level}</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        r_class = "kpi-green" if readiness == "READY" else "kpi-yellow" if readiness == "WARNING" else "kpi-red"
        # Full text, no truncation
        r_text = {"READY": "READY", "WARNING": "WARNING", "NOT_READY": "NOT READY"}.get(readiness, readiness)
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Readiness</div>'
            f'<div class="kpi-value {r_class}" style="font-size:1.4rem;">{readiness_icon} {r_text}</div></div>',
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">Priority Rank</div>'
            f'<div class="kpi-value kpi-white"><span style="font-size:1.1rem;color:#64748b">#</span>'
            f'{p_rank}<span style="font-size:0.9rem;font-weight:400;color:#64748b"> of {p_total}</span></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(
        min(max(health / 100.0, 0.0), 1.0),
        text=f"Health: {health:.1f} / 100",
    )

    st.divider()

    # ── why at risk + recommended action ─────────────────────────────────────
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<p class="section-heading">Why is this asset at risk?</p>', unsafe_allow_html=True)
        factors = status.get("top_risk_factors") or risk.get("top_risk_factors") or []
        if factors:
            for f in factors:
                st.markdown(f'<div class="risk-factor">• {f}</div>', unsafe_allow_html=True)
        else:
            st.info("No specific risk factors identified.")

        reasons = priority.get("priority_reasons", [])
        if reasons:
            st.markdown(
                '<p class="section-heading" style="margin-top:18px;">Priority drivers</p>',
                unsafe_allow_html=True,
            )
            for r in reasons:
                st.markdown(f"- {r}")

    with right:
        st.markdown('<p class="section-heading">Recommended action</p>', unsafe_allow_html=True)
        action = status.get("recommended_action") or risk.get("recommended_action", "")
        if action:
            st.markdown(f'<div class="action-box">{action}</div>', unsafe_allow_html=True)
        else:
            st.info("No action recommended.")

        st.markdown(
            '<p class="section-heading" style="margin-top:18px;">Maintenance priority score</p>',
            unsafe_allow_html=True,
        )
        st.progress(
            min(max(p_score / 100.0, 0.0), 1.0),
            text=f"Priority score: {p_score:.1f} / 100  (higher = more urgent)",
        )


# ── About page ────────────────────────────────────────────────────────────────

def _render_about() -> None:
    """Full About page — project overview, workflow diagram, tech stack, team."""

    # Hero
    st.markdown(
        """
        <div class="about-hero">
          <h1>🛡️ MissionGuard AI</h1>
          <p>
            A decision-support system that helps maintenance teams quickly understand
            which fleet assets are mission-ready, why specific assets are at risk, and
            what to service first — all explained in plain language.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── What is MissionGuard? ─────────────────────────────────────────────────
    st.markdown('<p class="section-heading">What does MissionGuard do?</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cards = [
        ("🎯", "Assess Mission Readiness",
         "Every asset in the fleet is automatically classified as READY, "
         "WARNING, or NOT READY based on its health score and risk level. "
         "No manual spreadsheet review needed."),
        ("🔍", "Explain Every Risk Score",
         "MissionGuard doesn't just say an asset is 'high risk' — it tells you "
         "exactly why. Each score comes with up to 3 plain-English risk factors "
         "and a specific recommended action."),
        ("📋", "Rank Maintenance Priorities",
         "All 100 assets are ranked by urgency. The maintenance team always knows "
         "which asset to service first, second, and third — with a deterministic "
         "score from 0 to 100."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        col.markdown(
            f'<div class="about-card"><h3>{icon} {title}</h3><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    c4, c5 = st.columns(2)
    cards2 = [
        ("📊", "Interactive Dashboard",
         "This Streamlit dashboard shows the full fleet at a glance — KPI cards, "
         "readiness/risk charts, the top-15 priority queue, and a per-asset detail "
         "panel with risk factors and recommended actions."),
        ("🤖", "Ask IBM Bob in Plain English",
         "Via the IBM Bob AI assistant and the Model Context Protocol (MCP), you can "
         "ask questions like 'Why is A-042 high risk?' and get an instant, "
         "structured answer — no SQL, no API calls, just natural language."),
    ]
    for col, (icon, title, desc) in zip([c4, c5], cards2):
        col.markdown(
            f'<div class="about-card"><h3>{icon} {title}</h3><p>{desc}</p></div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Workflow diagram ──────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">How it works — project workflow</p>', unsafe_allow_html=True)

    # Row 1: data → risk engine
    cols = st.columns([3, 1, 3, 1, 3, 1, 3])
    steps_row1 = [
        ("📁", "Synthetic Dataset", "100 fleet assets in a CSV file.\nEach has sensor readings like temperature, vibration, fuel use, and service history."),
        ("⚙️", "Risk Engine", "A hybrid ML model (logistic regression + domain rules) scores each asset.\nOutputs: health score, failure probability, risk level."),
        ("🔎", "Explainability", "The model's top contributing factors are translated into plain-English phrases.\nExample: 'High utilization intensity'."),
        ("📡", "REST API", "FastAPI wraps the risk engine as HTTP endpoints.\nSwagger docs at localhost:8000/docs."),
    ]
    step_cols = [cols[0], cols[2], cols[4], cols[6]]
    arrow_cols = [cols[1], cols[3], cols[5]]
    for sc, (icon, title, desc) in zip(step_cols, steps_row1):
        sc.markdown(
            f'<div class="flow-step"><div class="step-icon">{icon}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )
    for ac in arrow_cols:
        ac.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: dashboard → MCP → IBM Bob
    cols2 = st.columns([3, 1, 3, 1, 3, 1, 3])
    steps_row2 = [
        ("📊", "Dashboard", "Streamlit reads the REST API and shows KPI cards, charts, priority queue, and asset detail panels.\nAvailable at localhost:8501."),
        ("🔌", "MCP Server", "Five MCP tools wrap the risk engine for AI consumption:\nlist_assets, get_asset_readiness, get_asset_failure_risk, get_asset_maintenance, get_fleet_summary."),
        ("🤖", "IBM Bob", "IBM Bob reads .bob/mcp.json, connects to the MCP server, and routes natural-language questions to the right tool.\nIBM Bob is the conversational layer — MissionGuard does the analysis."),
        ("💬", "Plain-Language Answer", "Bob formats the structured result into a natural-language response.\nExample: 'Asset A-042 is HIGH risk. Main factors: overdue maintenance, high vibration.'"),
    ]
    step_cols2 = [cols2[0], cols2[2], cols2[4], cols2[6]]
    arrow_cols2 = [cols2[1], cols2[3], cols2[5]]
    for sc, (icon, title, desc) in zip(step_cols2, steps_row2):
        sc.markdown(
            f'<div class="flow-step"><div class="step-icon">{icon}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div></div>',
            unsafe_allow_html=True,
        )
    for ac in arrow_cols2:
        ac.markdown('<div class="flow-arrow">→</div>', unsafe_allow_html=True)

    # connector between rows
    st.markdown(
        """
        <div style="text-align:left; padding: 4px 0 4px 0; color:#334155; font-size:1.3rem;">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓&nbsp;&nbsp;(also)
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Tech stack ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">Technology stack</p>', unsafe_allow_html=True)
    tech = {
        "Language": ["Python 3.14"],
        "ML / Data": ["scikit-learn", "pandas", "NumPy", "joblib"],
        "API": ["FastAPI", "uvicorn", "httpx"],
        "Dashboard": ["Streamlit", "requests"],
        "IBM / AI": ["IBM Bob", "Model Context Protocol (MCP)", "mcp[cli]"],
        "Testing": ["pytest", "pytest-asyncio"],
        "Data": ["Synthetic CSV (seed=42, 100 assets)"],
    }
    tc1, tc2 = st.columns(2)
    items = list(tech.items())
    for col, chunk in zip([tc1, tc2], [items[:4], items[4:]]):
        with col:
            for category, tools in chunk:
                pills = " ".join(f'<span class="tech-pill">{t}</span>' for t in tools)
                st.markdown(
                    f'<p style="font-size:0.72rem;font-weight:600;color:#64748b;'
                    f'text-transform:uppercase;letter-spacing:0.08em;margin:12px 0 5px 0">'
                    f'{category}</p>{pills}',
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── Key facts ─────────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">Key facts</p>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    facts = [
        ("100", "Fleet Assets", "kpi-blue"),
        ("71", "Tests Passing", "kpi-green"),
        ("5", "MCP Tools", "kpi-yellow"),
        ("3", "Readiness Levels", "kpi-white"),
    ]
    for col, (val, label, cls) in zip([f1, f2, f3, f4], facts):
        col.markdown(_kpi_card(label, val, cls), unsafe_allow_html=True)

    st.divider()

    # ── Team ──────────────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">Team Sher — IBM BoB AI Innovation Hackathon 2026</p>', unsafe_allow_html=True)
    tm1, tm2, tm3, tm4 = st.columns(4)
    members = [
        ("Kinari Thummar", "Lead Developer & Project Integration", "24AIML070"),
        ("Hetvi Patoliya", "AI/ML & Presentation Developer", "24AIML050"),
        ("Himay Thummar", "IBM Bob & MCP Integration Developer", "24AIML069"),
        ("Prince Vaghasiya", "Frontend Developer & UI Contributor", "24AIML074"),
    ]
    for col, (name, role, mid) in zip([tm1, tm2, tm3, tm4], members):
        col.markdown(
            f'<div class="team-card">'
            f'<div class="team-name">{name}</div>'
            f'<div class="team-role">{role}</div>'
            f'<div style="font-size:0.72rem;color:#334155;margin-top:6px">{mid}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="disclaimer">
        <strong>⚠️ Prototype — Synthetic Data Only</strong><br>
        All fleet data is entirely synthetic and fictional. Risk probabilities are model estimates,
        not observed failure rates. MissionGuard AI is <strong>NOT validated for real military operations</strong>.
        This project is built for the IBM BoB AI Innovation Hackathon 2026 demonstration purposes only.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _render_sidebar(client: MissionGuardClient) -> tuple[str | None, str, str]:
    st.sidebar.title("🛡️ MissionGuard AI")
    st.sidebar.caption("Mission Readiness & Predictive Maintenance")
    st.sidebar.divider()

    ok, info = client.health_check()
    if ok:
        st.sidebar.success(f"Backend online  v{info}")
    else:
        st.sidebar.error("Backend offline")
        st.sidebar.caption("Start the FastAPI server:\n\n`python -m uvicorn src.api.main:app --reload`")

    st.sidebar.divider()
    st.sidebar.markdown("**Filters**")

    readiness_filter = st.sidebar.selectbox(
        "Readiness status",
        ["All", "NOT_READY", "WARNING", "READY"],
        index=0,
    )
    type_filter = st.sidebar.selectbox(
        "Asset type",
        ["All", "UAV", "Ground Vehicle", "Generator", "Communications Relay", "Rotary Wing"],
        index=0,
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Select asset for detail view**")

    return None, readiness_filter, type_filter


# ── Disclaimer ────────────────────────────────────────────────────────────────

def _disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
        <strong>⚠️ Prototype Decision Support System</strong>&nbsp;·&nbsp;
        Data is entirely <strong>synthetic and fictional</strong>. Risk probabilities are model
        estimates, not observed failure rates. This system is <strong>NOT validated for real
        military operations</strong>. All assessments are for hackathon demonstration purposes only.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Main app ──────────────────────────────────────────────────────────────────

def main() -> None:
    _inject_css()

    client = MissionGuardClient(base_url=API_URL)

    # ── Navigation tabs ───────────────────────────────────────────────────────
    tab_dashboard, tab_about = st.tabs(["📊  Dashboard", "ℹ️  About"])

    with tab_dashboard:
        # ── Sidebar ───────────────────────────────────────────────────────────
        _, readiness_filter, type_filter = _render_sidebar(client)

        # ── Header ────────────────────────────────────────────────────────────
        st.markdown("## 🛡️ MissionGuard AI")
        st.markdown(
            "**Mission Readiness & Predictive Maintenance Copilot** · Team Nova · IBM BoB AI Innovation Hackathon 2026"
        )
        _disclaimer()
        st.divider()

        # ── Load data ──────────────────────────────────────────────────────────
        try:
            all_assets = _fetch_all_assets(API_URL)
        except BackendUnavailableError as exc:
            st.error(
                "**MissionGuard backend is unavailable.**\n\n"
                f"{exc}\n\n"
                "Start the FastAPI server in a separate terminal:\n\n"
                "```\npython -m uvicorn src.api.main:app --reload --port 8000\n```"
            )
            st.stop()

        if not all_assets:
            st.warning("No asset data returned from the backend.")
            st.stop()

        # ── Apply filters ──────────────────────────────────────────────────────
        filtered = all_assets
        if readiness_filter != "All":
            filtered = [a for a in filtered if a.get("readiness_status") == readiness_filter]
        if type_filter != "All":
            filtered = [a for a in filtered if a.get("asset_type") == type_filter]

        total = len(all_assets)
        readiness_counts: dict[str, int] = {"READY": 0, "WARNING": 0, "NOT_READY": 0}
        risk_counts: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for a in all_assets:
            r = a.get("readiness_status", "")
            if r in readiness_counts:
                readiness_counts[r] += 1
            lvl = a.get("risk_level", "")
            if lvl in risk_counts:
                risk_counts[lvl] += 1

        # ── KPI row ────────────────────────────────────────────────────────────
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.markdown(_kpi_card("Total Assets", total, "kpi-blue"), unsafe_allow_html=True)
        k2.markdown(_kpi_card("Ready", readiness_counts["READY"], "kpi-green"), unsafe_allow_html=True)
        k3.markdown(_kpi_card("Warning", readiness_counts["WARNING"], "kpi-yellow"), unsafe_allow_html=True)
        k4.markdown(_kpi_card("Not Ready", readiness_counts["NOT_READY"], "kpi-red"), unsafe_allow_html=True)
        k5.markdown(_kpi_card("High Risk", risk_counts["HIGH"], "kpi-red"), unsafe_allow_html=True)

        st.divider()

        # ── Overview charts row ────────────────────────────────────────────────
        ov_left, ov_right = st.columns(2)

        with ov_left:
            st.markdown('<p class="section-heading">Fleet Readiness Overview</p>', unsafe_allow_html=True)
            _readiness_bar(readiness_counts, total)
            import pandas as pd
            readiness_df = pd.DataFrame(
                {"Status": list(readiness_counts.keys()), "Count": list(readiness_counts.values())}
            )
            st.bar_chart(readiness_df.set_index("Status"), color=["#60a5fa"])

        with ov_right:
            st.markdown('<p class="section-heading">Risk Level Distribution</p>', unsafe_allow_html=True)
            _risk_bar(risk_counts, total)
            import pandas as pd
            risk_df = pd.DataFrame(
                {"Level": list(risk_counts.keys()), "Count": list(risk_counts.values())}
            )
            st.bar_chart(risk_df.set_index("Level"), color=["#f87171"])

        st.divider()

        # ── Maintenance priority queue ─────────────────────────────────────────
        st.markdown(
            '<p class="section-heading">Maintenance Priority Queue — Top 15 Most Urgent</p>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Sorted by failure probability (highest first). "
            "Select an asset below for full priority rank and detail."
        )

        display_assets = filtered if filtered else all_assets
        _priority_queue_table(display_assets, client, top_n=15)

        if readiness_filter != "All" or type_filter != "All":
            st.caption(
                f"Showing **{len(filtered)}** of **{total}** assets "
                f"(filters: readiness={readiness_filter}, type={type_filter}). "
                "Clear filters in the sidebar to see the full fleet."
            )

        st.divider()

        # ── Asset detail ───────────────────────────────────────────────────────
        st.markdown('<p class="section-heading">Asset Detail View</p>', unsafe_allow_html=True)

        asset_ids = [a["asset_id"] for a in all_assets]
        not_ready_ids = [
            a["asset_id"] for a in sorted(
                all_assets, key=lambda x: x.get("failure_probability", 0), reverse=True
            )
            if a.get("readiness_status") == "NOT_READY"
        ]
        default_id = not_ready_ids[0] if not_ready_ids else asset_ids[0]
        default_idx = asset_ids.index(default_id) if default_id in asset_ids else 0

        selected_id = st.selectbox(
            "Select asset to inspect",
            options=asset_ids,
            index=default_idx,
            format_func=lambda aid: (
                f"{aid}  —  "
                + next((a["asset_type"] for a in all_assets if a["asset_id"] == aid), "")
                + "  "
                + RISK_COLOURS.get(
                    next((a["risk_level"] for a in all_assets if a["asset_id"] == aid), ""), ""
                )
            ),
        )

        if selected_id:
            st.divider()
            _asset_detail(selected_id, client)

        # ── Footer ─────────────────────────────────────────────────────────────
        st.divider()
        st.caption(
            "MissionGuard AI · Team Nova · IBM BoB AI Innovation Hackathon 2026 · "
            "Prototype — synthetic data only · Not for operational use"
        )

    with tab_about:
        _render_about()


if __name__ == "__main__":
    main()
