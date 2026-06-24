import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Founder Validation Copilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Minimal custom CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
.score-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 8px;
}
.go    { background:#1a7a3c; color:#fff; }
.nogo  { background:#c0392b; color:#fff; }
.pivot { background:#d68910; color:#fff; }
.step-box {
    background: #1e1e2e;
    border-left: 3px solid #7c3aed;
    padding: 10px 16px;
    border-radius: 4px;
    margin: 6px 0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session state bootstrap ──────────────────────────────────────────────────
def _init():
    defaults = {
        "view": "validate",           # validate | history | detail
        "current_opp": None,          # Opportunity object being viewed
        "validation_running": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚀 Founder Validation Copilot")
    st.divider()
    if st.button("✨ New Validation", use_container_width=True, type="primary"):
        st.session_state.view = "validate"
        st.session_state.current_opp = None
    if st.button("📋 Opportunity History", use_container_width=True):
        st.session_state.view = "history"
    st.divider()
    st.caption("Paste any startup signal and get a structured validation in minutes.")


# ════════════════════════════════════════════════════════════════════════════
# VIEW: VALIDATE
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.view == "validate":
    st.title("Founder Validation Copilot")
    st.markdown("Turn any startup signal into a GO / NO-GO decision — in minutes.")
    st.divider()

    user_input = st.text_area(
        "Paste Anything",
        height=160,
        placeholder=(
            "Examples:\n"
            "• https://github.com/org/repo\n"
            "• https://firecrawl.dev\n"
            "• People keep complaining about poor RAG data quality.\n"
            "• AI SEO assistant for Shopify store owners."
        ),
    )

    col_btn, col_hint = st.columns([1, 4])
    with col_btn:
        start = st.button("🔍 Start Validation", type="primary", use_container_width=True,
                          disabled=st.session_state.validation_running)
    with col_hint:
        st.caption("Accepts GitHub repos, websites, ideas, Reddit threads, HN posts, or plain text.")

    if start and user_input.strip():
        st.session_state.validation_running = True

        status_area = st.empty()
        progress = st.progress(0)

        def step(msg: str, pct: int):
            status_area.markdown(f'<div class="step-box">⚙️ {msg}</div>', unsafe_allow_html=True)
            progress.progress(pct)

        try:
            from src.ai import classify_and_extract, score_opportunity, generate_report
            from src.search import research_market
            from src.storage import save_opportunity
            from src.models import Opportunity

            # Step 1 — classify
            step("Step 1/4 — Identifying input type and extracting metadata…", 10)
            meta = classify_and_extract(user_input)

            input_type = meta.get("input_type", "Startup Idea")
            product_name = meta.get("product_name", "Unknown Product")
            product_category = meta.get("product_category", "General")
            core_problem = meta.get("core_problem", "")
            target_audience = meta.get("target_audience", "")
            keywords = meta.get("keywords", [])
            competitors = meta.get("competitors", [])

            st.info(f"**Identified:** {input_type} · **Product:** {product_name} · **Category:** {product_category}")

            # Step 2 — search
            step("Step 2/4 — Researching market demand, competitors, and pricing signals…", 35)
            research_data = research_market(
                product_name, product_category, core_problem, target_audience, keywords, competitors
            )

            # Step 3 — score
            step("Step 3/4 — Scoring opportunity…", 60)
            research_summary = research_data[:3000]  # Keep prompt manageable
            score_data = score_opportunity(
                product_name, product_category, core_problem, target_audience, research_summary
            )

            # Step 4 — report
            step("Step 4/4 — Generating validation report…", 80)
            report_md = generate_report(
                input_type, product_name, product_category, core_problem,
                target_audience, keywords, research_data, score_data
            )

            # Persist
            opp = Opportunity(
                title=product_name,
                input_type=input_type,
                original_input=user_input,
                keywords=keywords,
                score=score_data.get("score", 0),
                decision=score_data.get("decision", "NO-GO"),
                status="Validated",
                report_markdown=report_md,
            )
            try:
                save_opportunity(opp)
            except Exception as save_err:
                st.warning(f"Report generated but could not save to GitHub: {save_err}")

            progress.progress(100)
            status_area.success("✅ Validation complete!")
            st.session_state.current_opp = opp
            st.session_state.view = "detail"
            st.session_state.validation_running = False
            st.rerun()

        except Exception as e:
            progress.empty()
            status_area.error(f"Validation failed: {e}")
            st.session_state.validation_running = False

    elif start and not user_input.strip():
        st.warning("Please paste something first.")


# ════════════════════════════════════════════════════════════════════════════
# VIEW: DETAIL — show a validation report
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "detail" and st.session_state.current_opp is not None:
    opp = st.session_state.current_opp
    from src.models import STATUS_OPTIONS
    from src.storage import update_status, save_opportunity
    from src.ai import generate_brd

    # Header
    score = opp.score
    decision = opp.decision
    badge_class = "go" if decision == "GO" else ("pivot" if decision == "PIVOT" else "nogo")
    decision_emoji = "✅" if decision == "GO" else ("🔄" if decision == "PIVOT" else "❌")

    col_title, col_score = st.columns([3, 1])
    with col_title:
        st.title(opp.title)
        st.caption(f"**Type:** {opp.input_type} · **Created:** {opp.created_at[:10]} · **Keywords:** {', '.join(opp.keywords)}")
    with col_score:
        st.markdown(
            f'<div class="score-badge {badge_class}">{decision_emoji} {decision} — {score}/10</div>',
            unsafe_allow_html=True
        )
        new_status = st.selectbox("Status", STATUS_OPTIONS,
                                  index=STATUS_OPTIONS.index(opp.status) if opp.status in STATUS_OPTIONS else 0,
                                  key="status_select")
        if new_status != opp.status:
            opp.status = new_status
            st.session_state.current_opp = opp
            try:
                update_status(opp.id, new_status)
                st.success("Status updated.")
            except Exception as e:
                st.warning(f"Could not persist status: {e}")

    st.divider()

    # Report tabs
    tab_report, tab_research, tab_brd = st.tabs(["📊 Validation Report", "🔎 Raw Research", "📄 Generate BRD"])

    with tab_report:
        st.markdown(opp.report_markdown)

        st.divider()
        col_dl, _ = st.columns([1, 3])
        with col_dl:
            st.download_button(
                "⬇️ Download Report (.md)",
                data=opp.report_markdown,
                file_name=f"{opp.title.replace(' ', '_')}_validation.md",
                mime="text/markdown",
            )

    with tab_research:
        st.caption("Raw Brave Search results used during validation.")
        # We don't re-store raw research — show a re-run option
        st.info("Raw research data is not stored separately. Re-run validation to see fresh search results.")

    with tab_brd:
        st.markdown("Generate a full Business Requirements Document based on this validation.")
        if st.button("📄 Generate BRD", type="primary"):
            with st.spinner("Generating BRD…"):
                try:
                    brd_md = generate_brd(
                        opp.title, "", "", "", opp.score, opp.decision, opp.report_markdown
                    )
                    st.markdown(brd_md)
                    st.download_button(
                        "⬇️ Download BRD.md",
                        data=brd_md,
                        file_name=f"{opp.title.replace(' ', '_')}_BRD.md",
                        mime="text/markdown",
                    )
                except Exception as e:
                    st.error(f"BRD generation failed: {e}")


# ════════════════════════════════════════════════════════════════════════════
# VIEW: HISTORY
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.view == "history":
    st.title("📋 Opportunity History")
    st.divider()

    from src.storage import list_opportunities, load_opportunity

    try:
        opps = list_opportunities()
    except Exception as e:
        st.error(f"Could not load history: {e}")
        opps = []

    if not opps:
        st.info("No validations saved yet. Run your first validation to get started.")
    else:
        st.caption(f"{len(opps)} opportunit{'y' if len(opps)==1 else 'ies'} saved.")

        # Filter bar
        filter_col, status_col = st.columns([2, 1])
        with filter_col:
            search_term = st.text_input("🔍 Filter by title / keywords", placeholder="Search…")
        with status_col:
            from src.models import STATUS_OPTIONS
            status_filter = st.selectbox("Status", ["All"] + STATUS_OPTIONS)

        filtered = opps
        if search_term:
            q = search_term.lower()
            filtered = [o for o in filtered if q in o.get("title", "").lower()]
        if status_filter != "All":
            filtered = [o for o in filtered if o.get("status") == status_filter]

        for opp_summary in filtered:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                with c1:
                    st.markdown(f"**{opp_summary.get('title', 'Untitled')}**")
                    st.caption(f"{opp_summary.get('input_type', '')} · {opp_summary.get('created_at', '')[:10]}")
                with c2:
                    score = opp_summary.get("score", 0)
                    st.metric("Score", f"{score}/10")
                with c3:
                    decision = opp_summary.get("decision", "")
                    color = "🟢" if decision == "GO" else ("🟡" if decision == "PIVOT" else "🔴")
                    st.markdown(f"{color} **{decision}**")
                with c4:
                    st.markdown(f"`{opp_summary.get('status', '')}`")
                    if st.button("Open →", key=f"open_{opp_summary['id']}"):
                        try:
                            full_opp = load_opportunity(opp_summary["id"])
                            if full_opp:
                                st.session_state.current_opp = full_opp
                                st.session_state.view = "detail"
                                st.rerun()
                        except Exception as e:
                            st.error(f"Could not load report: {e}")
