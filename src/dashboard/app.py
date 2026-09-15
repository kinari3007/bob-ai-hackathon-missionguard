"""MissionGuard AI — Streamlit Dashboard.

Launch:
    .venv\\Scripts\\python.exe -m streamlit run src/dashboard/app.py

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
READINESS_COLOURS = {"READY": "🟢", "WARNING": "🟡", "NOT_READY": "🔴"}
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
        /* KPI card */
        .kpi-card {
            background: #1e2330;
            border-radius: 10px;
            padding: 18px 20px 14px 20px;
            text-align: center;
            border: 1px solid #2d3348;
        }
        .kpi-label { font-size: 0.78rem; color: #8892a4; text-transform: uppercase;
                     letter-spacing: 0.06em; margin-bottom: 6px; }
        .kpi-value { font-size: 2.2rem; font-weight: 700; line-height: 1; }
        .kpi-green  { color: #22c55e; }
        .kpi-yellow { color: #eab308; }
        .kpi-red    { color: #ef4444; }
        .kpi-blue   { color: #60a5fa; }
        .kpi-white  { color: #f1f5f9; }

        /* Section heading */
        .section-heading {
            font-size: 1.05rem; font-weight: 600; color: #94a3b8;
            text-transform: uppercase; letter-spacing: 0.07em;
            margin: 0 0 10px 0; padding-bottom: 6px;
            border-bottom: 1px solid #2d3348;
        }

        /* Disclaimer */
        .disclaimer {
            background: #1e2330; border-left: 3px solid #f59e0b;
            padding: 10px 14px; border-radius: 4px;
            font-size: 0.78rem; color: #94a3b8; line-height: 1.6;
        }

        /* Risk factor bullet */
        .risk-factor {
            background: #1e2330; border-left: 3px solid #ef4444;
            padding: 7px 12px; border-radius: 4px; margin-bottom: 6px;
            font-size: 0.9rem; color: #f1f5f9;
        }

        /* Recommended action box */
        .action-box {
            background: #162032; border: 1px solid #1d4ed8;
            border-radius: 8px; padding: 14px 16px;
            font-size: 0.92rem; color: #bfdbfe; line-height: 1.6;
        }

        /* Hide Streamlit's default menu for cleaner demo */
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
    """Draw a horizontal readiness breakdown using Streamlit columns + metric."""
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


def _priority_queue_table(assets: list[dict[str, Any]], client: MissionGuardClient, top_n: int = 15) -> None:
    """Build maintenance priority queue sorted by failure_probability (proxy for priority)."""
    # Sort by failure_probability descending — avoids N extra API calls.
    # Full priority rank comes from the detail view.
    sorted_assets = sorted(assets, key=lambda a: float(a.get("failure_probability", 0)), reverse=True)
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
    """Render the detail panel for a selected asset."""
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

    readiness = status.get("readiness_status", "UNKNOWN")
    risk_level = risk.get("risk_level", "UNKNOWN")
    health = float(risk.get("health_score", 0))
    prob = float(risk.get("failure_probability", 0))
    p_score = float(priority.get("priority_score", 0))
    p_rank  = priority.get("priority_rank", "?")
    p_total = priority.get("total_assets", 100)

    # ── identity row ─────────────────────────────────────────────────────────
    st.markdown(
        f"### {asset_id} — {status.get('asset_type', '')}",
        unsafe_allow_html=False,
    )

    # ── core metrics ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Health Score", f"{health:.1f} / 100")
    c2.metric("Failure Probability", f"{prob:.1%}")
    c3.metric("Risk Level", f"{RISK_COLOURS.get(risk_level, '')} {risk_level}")
    c4.metric("Readiness", READINESS_BADGE.get(readiness, readiness))
    c5.metric("Priority Rank", f"#{p_rank} of {p_total}")

    st.progress(
        min(max(health / 100.0, 0.0), 1.0),
        text=f"Health: {health:.1f}%",
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

        # Priority reasons (from /priority endpoint)
        reasons = priority.get("priority_reasons", [])
        if reasons:
            st.markdown('<p class="section-heading" style="margin-top:16px;">Priority drivers</p>', unsafe_allow_html=True)
            for r in reasons:
                st.markdown(f"- {r}")

    with right:
        st.markdown('<p class="section-heading">Recommended action</p>', unsafe_allow_html=True)
        action = status.get("recommended_action") or risk.get("recommended_action", "")
        if action:
            st.markdown(f'<div class="action-box">{action}</div>', unsafe_allow_html=True)
        else:
            st.info("No action recommended.")

        # Priority score gauge
        st.markdown('<p class="section-heading" style="margin-top:16px;">Maintenance priority score</p>', unsafe_allow_html=True)
        st.progress(
            min(max(p_score / 100.0, 0.0), 1.0),
            text=f"Priority score: {p_score:.1f} / 100  (higher = more urgent)",
        )


# ── Sidebar ───────────────────────────────────────────────────────────────────

def _render_sidebar(client: MissionGuardClient) -> tuple[str | None, str, str]:
    """Render sidebar controls; return (selected_asset_id, readiness_filter, type_filter)."""
    st.sidebar.title("🛡️ MissionGuard AI")
    st.sidebar.caption("Mission Readiness & Predictive Maintenance")
    st.sidebar.divider()

    # Backend status
    ok, info = client.health_check()
    if ok:
        st.sidebar.success(f"Backend online  v{info}")
    else:
        st.sidebar.error("Backend offline")
        st.sidebar.caption(f"Start the FastAPI server:\n\n`uvicorn src.api.main:app --reload`")

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

    # Asset selector populated after main data load
    return None, readiness_filter, type_filter


# ── Disclaimer ────────────────────────────────────────────────────────────────

def _disclaimer() -> None:
    st.markdown(
        """
        <div class="disclaimer">
        <strong>⚠️ Prototype Decision Support System</strong><br>
        Data is entirely <strong>synthetic and fictional</strong>. Risk probabilities are model
        estimates, not observed failure rates. This system is <strong>NOT validated for real
        military operations</strong>. All assessments are for hackathon demonstration purposes
        only. Do not use for actual mission-critical decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Main app ──────────────────────────────────────────────────────────────────

def main() -> None:
    _inject_css()

    client = MissionGuardClient(base_url=API_URL)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    _, readiness_filter, type_filter = _render_sidebar(client)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("## 🛡️ MissionGuard AI")
    st.markdown("**Mission Readiness & Predictive Maintenance Copilot** · Team Nova · IBM BoB AI Innovation Hackathon 2026")
    _disclaimer()
    st.divider()

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        all_assets = _fetch_all_assets(API_URL)
    except BackendUnavailableError as exc:
        st.error(
            "**MissionGuard backend is unavailable.**\n\n"
            f"{exc}\n\n"
            "Start the FastAPI server in a separate terminal:\n\n"
            "```\n.venv\\Scripts\\python.exe -m uvicorn src.api.main:app --reload --port 8000\n```"
        )
        st.stop()

    if not all_assets:
        st.warning("No asset data returned from the backend.")
        st.stop()

    # ── Apply filters ─────────────────────────────────────────────────────────
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

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(_kpi_card("Total Assets", total, "kpi-blue"), unsafe_allow_html=True)
    k2.markdown(_kpi_card("Ready", readiness_counts["READY"], "kpi-green"), unsafe_allow_html=True)
    k3.markdown(_kpi_card("Warning", readiness_counts["WARNING"], "kpi-yellow"), unsafe_allow_html=True)
    k4.markdown(_kpi_card("Not Ready", readiness_counts["NOT_READY"], "kpi-red"), unsafe_allow_html=True)
    k5.markdown(_kpi_card("High Risk", risk_counts["HIGH"], "kpi-red"), unsafe_allow_html=True)

    st.divider()

    # ── Overview charts row ───────────────────────────────────────────────────
    ov_left, ov_right = st.columns(2)

    with ov_left:
        st.markdown('<p class="section-heading">Fleet Readiness Overview</p>', unsafe_allow_html=True)
        _readiness_bar(readiness_counts, total)

        # Simple bar chart via Streamlit's built-in
        import pandas as pd
        readiness_df = pd.DataFrame(
            {"Status": list(readiness_counts.keys()), "Count": list(readiness_counts.values())}
        )
        st.bar_chart(readiness_df.set_index("Status"), color=["#60a5fa"])

    with ov_right:
        st.markdown('<p class="section-heading">Risk Level Distribution</p>', unsafe_allow_html=True)
        _risk_bar(risk_counts, total)

        risk_df = pd.DataFrame(
            {"Level": list(risk_counts.keys()), "Count": list(risk_counts.values())}
        )
        st.bar_chart(risk_df.set_index("Level"), color=["#f87171"])

    st.divider()

    # ── Maintenance priority queue ────────────────────────────────────────────
    st.markdown('<p class="section-heading">Maintenance Priority Queue — Top 15 Most Urgent</p>', unsafe_allow_html=True)
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

    # ── Asset detail ──────────────────────────────────────────────────────────
    st.markdown('<p class="section-heading">Asset Detail View</p>', unsafe_allow_html=True)

    asset_ids = [a["asset_id"] for a in all_assets]
    # Default to the highest-risk asset for a compelling demo first view
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

    # ── Footer ────────────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        "MissionGuard AI · Team Nova · IBM BoB AI Innovation Hackathon 2026 · "
        "Prototype — synthetic data only · Not for operational use"
    )


if __name__ == "__main__":
    main()
