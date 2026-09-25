"""
Streamlit Web Dashboard for Techvruk Universal Task Planner Agent.
Features an ultra-smooth Red & White Gemini-inspired user interface.
Handles ANY arbitrary task, breaking it down autonomously using ReAct workflow.
"""

import streamlit as st
import json
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import TaskPlannerAgent
from agent.tools import _load_json, PLANS_FILE

st.set_page_config(
    page_title="Task Planner Agent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ultra-Smooth Red & White Gemini-Style Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Background */
    .stApp {
        background-color: #FAFAFC;
    }

    /* Gemini-Style Centered Greeting */
    .gemini-hero {
        text-align: center;
        padding: 40px 20px 25px 20px;
        max-width: 850px;
        margin: 0 auto;
    }

    .gemini-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #DC2626 0%, #E11D48 50%, #991B1B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        margin-bottom: 10px;
        line-height: 1.15;
    }

    .gemini-subtitle {
        font-size: 1.15rem;
        color: #64748B;
        font-weight: 400;
        line-height: 1.6;
        margin-bottom: 25px;
    }

    /* Feature Badge Row */
    .badge-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 30px;
    }

    .gemini-badge {
        background: #FFFFFF;
        color: #DC2626;
        border: 1px solid #FECACA;
        padding: 6px 16px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(220, 38, 38, 0.08);
        transition: all 0.2s ease;
    }

    .gemini-badge:hover {
        background: #FEF2F2;
        transform: translateY(-1px);
    }

    /* Card Containers */
    .plan-card {
        background: #FFFFFF;
        border: 1px solid #F1F5F9;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        margin-bottom: 20px;
    }

    .plan-header {
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 16px;
        margin-bottom: 20px;
    }

    /* Metrics Bar */
    .metric-row {
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    .metric-box {
        flex: 1;
        min-width: 140px;
        background: #FFFFFF;
        border: 1px solid #FEE2E2;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 2px 6px rgba(220, 38, 38, 0.04);
    }

    .metric-box-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .metric-box-val {
        font-size: 1.35rem;
        font-weight: 800;
        color: #1E293B;
    }

    /* Subtask Item Card */
    .subtask-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #DC2626;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }

    .subtask-item:hover {
        border-color: #DC2626;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.08);
    }

    .subtask-title {
        font-weight: 700;
        color: #0F172A;
        font-size: 0.98rem;
        margin-bottom: 4px;
    }

    .subtask-meta {
        font-size: 0.82rem;
        color: #64748B;
    }

    .priority-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 6px;
    }

    .priority-high {
        background: #FEE2E2;
        color: #B91C1C;
    }

    .priority-medium {
        background: #FEF3C7;
        color: #B45309;
    }

    /* Telemetry Bubble */
    .telemetry-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
        font-size: 0.88rem;
    }

    .thought-text {
        color: #0F172A;
        font-weight: 500;
        margin-bottom: 6px;
    }

    .action-badge {
        background: #FEF2F2;
        color: #DC2626;
        font-family: monospace;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
    }

    /* Red Primary Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(220, 38, 38, 0.3) !important;
        transition: all 0.2s ease !important;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #B91C1C 0%, #991B1B 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(220, 38, 38, 0.4) !important;
    }

    /* Input text area styling */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1.5px solid #E2E8F0 !important;
        padding: 16px !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
    }

    .stTextArea textarea:focus {
        border-color: #DC2626 !important;
        box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15) !important;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if "agent" not in st.session_state:
    st.session_state.agent = TaskPlannerAgent()

if "history" not in st.session_state:
    st.session_state.history = []


# Sidebar for Settings & Blueprints
with st.sidebar:
    st.markdown("<h3 style='color: #DC2626; margin-bottom: 4px;'>⚙️ Planner Settings</h3>", unsafe_allow_html=True)
    st.caption("Universal Agentic Execution Engine")

    # API Key Config
    api_key_input = st.text_input("Gemini API Key (Optional)", type="password", placeholder="Paste AI Studio Key here")
    if api_key_input:
        st.session_state.agent = TaskPlannerAgent(api_key=api_key_input.strip())
        st.success("Connected to live Gemini API!")
    else:
        st.info("Operating in Zero-Key Offline Mode (100% Free-Tier compliant).")

    st.divider()

    st.markdown("<h4 style='color: #1E293B;'>💾 Plan Archives</h4>", unsafe_allow_html=True)
    saved_plans = _load_json(PLANS_FILE)
    st.caption(f"{len(saved_plans)} Master Plans Compiled")
    if saved_plans:
        with st.expander("View Saved Plans JSON"):
            st.json(saved_plans[-3:] if len(saved_plans) > 3 else saved_plans)

    st.divider()
    if st.button("Clear Conversation History", use_container_width=True):
        st.session_state.history = []
        st.rerun()


# Gemini Hero Header
st.markdown("""
<div class="gemini-hero">
    <div class="gemini-title">What task would you like to plan?</div>
    <div class="gemini-subtitle">
        Enter any arbitrary goal, trip, project, or event. The autonomous agent breaks it into phased sub-tasks,
        calculates critical path schedules, and generates an actionable master roadmap.
    </div>
    <div class="badge-container">
        <span class="gemini-badge">⚡ ReAct Architecture</span>
        <span class="gemini-badge">📋 Any Task / Universal Scope</span>
        <span class="gemini-badge">🎯 Critical Path Analysis</span>
        <span class="gemini-badge">🛡️ Contingency Safeguards</span>
    </div>
</div>
""", unsafe_allow_html=True)


# Gemini Suggestion Chips
col_chip1, col_chip2, col_chip3 = st.columns(3)
with col_chip1:
    if st.button("🌸 3-Day Trip to Tokyo ($1,200)", use_container_width=True):
        st.session_state.prompt_fill = "Plan a 3-day cultural and culinary trip to Tokyo for 2 people with historic landmarks and food markets on a $1,200 budget"

with col_chip2:
    if st.button("🚀 Build SaaS MVP in 4 Weeks", use_container_width=True):
        st.session_state.prompt_fill = "Build and launch a SaaS AI MVP in 4 weeks with authentication and payment billing on a $2,000 budget"

with col_chip3:
    if st.button("🎓 Prepare AWS Exam in 30 Days", use_container_width=True):
        st.session_state.prompt_fill = "Prepare for the AWS Solutions Architect exam in 30 days studying 2 hours daily with hands-on practice labs"


col_chip4, col_chip5, col_chip6 = st.columns(3)
with col_chip4:
    if st.button("🏆 2-Day AI Hackathon (100 devs)", use_container_width=True):
        st.session_state.prompt_fill = "Organize a 2-day technical AI hackathon for 100 participants in 3 weeks with a $1,500 prize pool"

with col_chip5:
    if st.button("🏡 Renovate Apartment ($5,000)", use_container_width=True):
        st.session_state.prompt_fill = "Renovate and furnish a 2-bedroom apartment with a $5,000 budget in 2 weeks"

with col_chip6:
    if st.button("🏃 Train for Half-Marathon (10 wks)", use_container_width=True):
        st.session_state.prompt_fill = "Train for a 21km half marathon in 10 weeks starting from a 5k baseline"

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)


# Main Goal Input Area
default_val = st.session_state.get("prompt_fill", "")
user_goal = st.text_area(
    "Enter Your Goal or Task:",
    value=default_val,
    height=85,
    placeholder="e.g. Plan a 3-day trip to Tokyo on a $1,200 budget, or launch a mobile app in 3 weeks..."
)

col_run, col_clear = st.columns([1, 5])
with col_run:
    execute_clicked = st.button("Plan Task ➔", use_container_width=True)

if execute_clicked and user_goal.strip():
    with st.spinner("Agentic ReAct Engine is decomposing goal, evaluating feasibility, and deriving schedule..."):
        state = st.session_state.agent.run(user_goal.strip())
        st.session_state.history.append((user_goal.strip(), state))
        st.session_state.prompt_fill = ""


# Render Generated Master Plans and Telemetry
if st.session_state.history:
    for goal_text, state in reversed(st.session_state.history):
        p = state.structured_plan
        c = state.parsed_constraints

        st.markdown("<hr style='border: none; border-top: 1px solid #F1F5F9; margin: 30px 0;' />", unsafe_allow_html=True)
        st.markdown(f"### 🎯 Goal: *\"{goal_text}\"*")

        # Metric Ribbon in Red & White
        b_str = f"${p.total_budget:,.2f}" if p and p.total_budget else "Flexible"
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box">
                <div class="metric-box-label">Master Plan ID</div>
                <div class="metric-box-val" style="color: #DC2626;">{p.plan_id if p else 'PLAN-001'}</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Domain Category</div>
                <div class="metric-box-val">{p.category if p else c.get('category')}</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Timeline Target</div>
                <div class="metric-box-val">{p.timeline_days if p else c.get('timeline_days')} Days</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Estimated Effort</div>
                <div class="metric-box-val">{p.estimated_hours:.0f} Hours</div>
            </div>
            <div class="metric-box">
                <div class="metric-box-label">Budget Ceiling</div>
                <div class="metric-box-val">{b_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Plan Overview & ReAct Telemetry in Two Columns
        left_col, right_col = st.columns([3, 2])

        with left_col:
            st.markdown("<div class='plan-card'>", unsafe_allow_html=True)
            st.markdown("### 📋 Master Execution Plan")
            st.markdown(state.final_response)
            st.markdown("</div>", unsafe_allow_html=True)

        with right_col:
            st.markdown("### ⚡ Agentic Telemetry")
            st.caption("Live ReAct Thought ➔ Action ➔ Observation trace")

            for act in state.scratchpad:
                st.markdown(f"""
                <div class="telemetry-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="action-badge">Step #{act.step_num}: {act.action_name}</span>
                        <span style="font-size: 0.75rem; color: #94A3B8;">{act.timestamp[11:19]}</span>
                    </div>
                    <div class="thought-text">🧠 <em>{act.thought}</em></div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander(f"View Observation #{act.step_num}", expanded=False):
                    st.json(act.observation)
else:
    st.markdown("""
    <div style="text-align: center; color: #94A3B8; padding: 40px 20px;">
        💡 Click any suggestion chip above or type your own custom task to generate a master roadmap.
    </div>
    """, unsafe_allow_html=True)
