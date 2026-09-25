"""
Streamlit Web Dashboard for Techvruk Task Planner Agent.
Demonstrates: Given a goal (e.g., 'plan a 3-day trip'), break into sub-tasks and generate a structured plan.
Includes real-time ReAct thought-action-observation telemetry, milestone timelines, budget allocations, and risk matrix.
"""

import streamlit as st
import json
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import TaskPlannerAgent
from agent.tools import _load_json, BLUEPRINTS_FILE, PLANS_FILE

st.set_page_config(
    page_title="Techvruk Task Planner Agent",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #0284c7, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.2rem;
    }
    .metric-badge {
        display: inline-block;
        padding: 5px 12px;
        background-color: #f0fdf4;
        color: #166534;
        font-weight: 600;
        border-radius: 9999px;
        font-size: 0.85rem;
        margin-right: 8px;
        border: 1px solid #bbf7d0;
    }
    .task-card {
        background-color: #f8fafc;
        border-left: 4px solid #0284c7;
        padding: 12px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .thought-bubble {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        font-family: monospace;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Agent in session state
if "agent" not in st.session_state:
    st.session_state.agent = TaskPlannerAgent()

if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/compass.png", width=60)
    st.title("Task Planner Agent")
    st.markdown("**Autonomous Goal Deconstructor & Plan Generator**")
    st.markdown("`Plan -> Act -> Observe -> Respond`")
    st.caption("Techvruk AI Contest Submission")
    st.divider()

    st.subheader("🎯 1-Click Evaluation Goals")
    st.caption("Click any preset to test the agent against the contest rubric:")

    scenarios = {
        "🌸 3-Day Tokyo Trip ($1,200)": "Plan a 3-day cultural and culinary trip to Tokyo for 2 people with historic landmarks and food markets on a $1,200 budget",
        "🗼 4-Day Paris Getaway ($1,800)": "Plan a 4-day weekend trip to Paris with museum visits, culinary dining, and scenic walks on an $1,800 budget",
        "🏝️ 5-Day Bali Vacation ($800)": "Plan a 5-day adventure and relaxation vacation to Bali for 2 travelers on an $800 budget",
        "🚀 4-Week SaaS MVP Launch ($2,000)": "Build and launch a SaaS AI MVP in 4 weeks with user authentication and payment billing on a $2,000 budget",
        "🏆 2-Day AI Hackathon ($1,500)": "Organize a 2-day technical AI hackathon for 100 participants in 3 weeks with a $1,500 prize pool"
    }

    selected_scenario = st.radio("Select Benchmark Goal:", list(scenarios.keys()))
    if st.button("Load & Plan This Goal", use_container_width=True, type="primary"):
        st.session_state.current_goal = scenarios[selected_scenario]

    st.divider()
    with st.expander("📚 Inspect Domain Blueprints (JSON)"):
        bp_data = _load_json(BLUEPRINTS_FILE)
        st.json(bp_data)

    with st.expander("💾 Inspect Saved Plans (JSON)"):
        saved_plans = _load_json(PLANS_FILE)
        st.json(saved_plans)


# Main Content Area
st.markdown('<div class="main-title">Autonomous Task Planner Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Given a high-level goal (e.g. "plan a 3-day trip"), this agent autonomously breaks it down into sequential sub-tasks, evaluates feasibility, calculates critical paths, and generates a structured master plan.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div style="margin-bottom: 20px;">
    <span class="metric-badge">🧠 Multi-Step Task Decomposition</span>
    <span class="metric-badge">⚡ Critical Path Scheduling</span>
    <span class="metric-badge">🛡️ Risk Audit & Mitigations</span>
    <span class="metric-badge">💰 Budget Allocation Matrix</span>
    <span class="metric-badge">📦 Free-Tier / Offline Ready</span>
</div>
""", unsafe_allow_html=True)

# Input container
user_input = st.text_area(
    "Enter Your High-Level Goal:",
    value=st.session_state.get("current_goal", "Plan a 3-day cultural and culinary trip to Tokyo for 2 people with historic landmarks and food markets on a $1,200 budget"),
    height=80,
    placeholder="e.g. Plan a 3-day trip to Tokyo with cultural sightseeing on a $1,200 budget"
)

col1, col2 = st.columns([1, 4])
with col1:
    plan_clicked = st.button("Generate Master Plan", type="primary", use_container_width=True)
with col2:
    if st.button("Clear History", use_container_width=False):
        st.session_state.history = []
        st.session_state.current_goal = ""
        st.rerun()

if plan_clicked and user_input.strip():
    with st.spinner("Agent is deconstructing goal into subtasks, evaluating feasibility, and compiling schedule..."):
        state = st.session_state.agent.run(user_input.strip())
        st.session_state.history.append((user_input.strip(), state))
        st.session_state.current_goal = ""

# Display Generated Master Plan and Telemetry
if st.session_state.history:
    for goal_text, state in reversed(st.session_state.history):
        p = state.structured_plan
        c = state.parsed_constraints

        st.markdown("---")
        st.markdown(f"### 🎯 Goal: *\"{goal_text}\"*")

        # Top Metric Ribbon
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Master Plan ID", p.plan_id if p else "N/A")
        with m2:
            st.metric("Domain", (p.domain if p else c.get('domain', '')).upper())
        with m3:
            st.metric("Timeline", f"{p.timeline_days if p else c.get('timeline_days')} Days")
        with m4:
            st.metric("Total Budget", f"${p.total_budget:,.2f}" if p else "Flexible")

        # Left Column: Structured Plan Output | Right Column: Agentic ReAct Telemetry
        plan_col, trace_col = st.columns([3, 2])

        with plan_col:
            st.subheader("📋 Master Execution Plan")
            st.markdown(state.final_response)

        with trace_col:
            st.subheader("⚡ Agentic ReAct Telemetry")

            # ReAct Scratchpad Loop
            with st.expander(f"🛠️ ReAct Execution Loop ({len(state.scratchpad)} tool actions)", expanded=True):
                for act in state.scratchpad:
                    st.markdown(f"**Step #{act.step_num}: `{act.action_name}`**")
                    st.markdown(f"<div class='thought-bubble'><strong>Thought:</strong> {act.thought}</div>", unsafe_allow_html=True)
                    st.caption(f"Input: `{json.dumps(act.action_input)}`")
                    with st.expander(f"View Observation #{act.step_num}", expanded=False):
                        st.json(act.observation)
                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed #cbd5e1;' />", unsafe_allow_html=True)
else:
    st.info("💡 Select one of the preset goals on the left sidebar (e.g. 3-Day Tokyo Trip) and click 'Generate Master Plan' to see the agent in action!")
