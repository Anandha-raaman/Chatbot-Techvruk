"""
Streamlit Web UI for Techvruk AI Agentic System.
Interactive demonstration showcasing real-time Planning, ReAct Tool Execution, and Human Escalation.
"""

import streamlit as st
import json
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import SupportAgent
from agent.tools import _load_json, KB_FILE, CUSTOMERS_FILE, TICKETS_FILE

st.set_page_config(
    page_title="Techvruk AI Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern dark/light contrast
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #2563eb, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 12px;
        background-color: #e0f2fe;
        color: #0369a1;
        font-weight: 600;
        border-radius: 9999px;
        font-size: 0.85rem;
        margin-right: 8px;
    }
    .escalation-box {
        background-color: #fef2f2;
        border-left: 5px solid #ef4444;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 10px 0;
        color: #991b1b;
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
    st.session_state.agent = SupportAgent()

if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/bot.png", width=60)
    st.title("Techvruk Agent")
    st.markdown("**Autonomous Customer Support & Escalation System**")
    st.markdown("`Plan -> Act -> Observe -> Respond`")
    st.divider()

    st.subheader("🧪 1-Click Evaluation Scenarios")
    st.caption("Click any preset scenario to evaluate the agent against the hackathon rubric:")

    scenarios = {
        "Policy FAQ (Search KB)": "What is your standard return and refund policy for retail goods?",
        "Order Status (DB Lookup)": "Can you check the tracking status of my order ORD-89421?",
        "Autonomous Refund (30-Day Window)": "I received order ORD-89421 on September 16, but it is defective. Please refund my payment.",
        "Expired Return Policy (Denial)": "I need a refund for my order ORD-77312 that arrived back in July.",
        "Critical Escalation (Human Tier-2)": "This is completely UNACCEPTABLE! My order ORD-90214 was over $640, it is severely delayed, and your carrier won't respond. Escalate this to a human manager immediately or I contact my attorney!"
    }

    selected_scenario = st.radio("Choose Scenario:", list(scenarios.keys()))
    if st.button("Load & Run Scenario", use_container_width=True, type="primary"):
        st.session_state.current_prompt = scenarios[selected_scenario]

    st.divider()
    with st.expander("📂 Inspect Knowledge Base (JSON)"):
        kb_data = _load_json(KB_FILE)
        st.json(kb_data)

    with st.expander("👤 Inspect Customer Database (JSON)"):
        cust_data = _load_json(CUSTOMERS_FILE)
        st.json(cust_data)

    with st.expander("🎫 Inspect Tickets / Escalations (JSON)"):
        tickets_data = _load_json(TICKETS_FILE)
        st.json(tickets_data)


# Main Content Area
st.markdown('<div class="main-title">Autonomous Support & Escalation Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">A complete agentic system exhibiting multi-step planning, tool execution, context memory, and dynamic escalation protocol.</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div style="margin-bottom: 20px;">
    <span class="metric-badge">🧠 ReAct Architecture</span>
    <span class="metric-badge">🔧 6 Autonomous Tools</span>
    <span class="metric-badge">⚡ Tier-2 Human Escalation</span>
    <span class="metric-badge">📦 Free-Tier / Zero-Key Fallback</span>
</div>
""", unsafe_allow_html=True)

# Input container
user_input = st.text_area(
    "Enter Customer Query or Prompt:",
    value=st.session_state.get("current_prompt", ""),
    height=80,
    placeholder="e.g. Can you track my order ORD-89421 and explain the return window?"
)

col1, col2 = st.columns([1, 5])
with col1:
    submit_clicked = st.button("Execute Agent", type="primary", use_container_width=True)
with col2:
    if st.button("Clear Chat", use_container_width=False):
        st.session_state.history = []
        st.session_state.current_prompt = ""
        st.rerun()

if submit_clicked and user_input.strip():
    with st.spinner("Agent is reasoning, planning, and executing tools..."):
        state = st.session_state.agent.run(user_input.strip())
        st.session_state.history.append((user_input.strip(), state))
        st.session_state.current_prompt = ""

# Display Conversation and Telemetry
if st.session_state.history:
    for query, state in reversed(st.session_state.history):
        st.markdown("---")
        st.markdown(f"### 💬 User Query: *\"{query}\"*")

        # Telemetry columns: Left is Agent Output, Right is Step-by-Step Reasoner
        out_col, trace_col = st.columns([3, 2])

        with out_col:
            st.subheader("🌟 Agent Response")
            st.markdown(state.final_response)

            if state.escalation.is_escalated:
                esc = state.escalation
                st.markdown(f"""
                <div class="escalation-box">
                    <strong>⚠️ TIER-2 HUMAN ESCALATION DISPATCHED</strong><br>
                    <strong>Ticket ID:</strong> <code>{esc.ticket_id}</code><br>
                    <strong>Urgency:</strong> {esc.urgency.upper()} | <strong>Sentiment:</strong> {esc.sentiment.upper()}<br>
                    <strong>Target SLA:</strong> Within {esc.sla_minutes} minutes | <strong>Queue:</strong> {esc.assigned_tier}
                </div>
                """, unsafe_allow_html=True)

        with trace_col:
            st.subheader("⚡ Agentic Telemetry")

            # 1. Action Plan
            with st.expander("📋 Decomposed Plan Steps", expanded=False):
                for p in state.plan:
                    icon = "✅" if p.status == "completed" else ("⏳" if p.status == "in_progress" else "⚪")
                    st.markdown(f"**{icon} Step {p.step_id}:** {p.description}")

            # 2. ReAct Scratchpad Loop
            with st.expander(f"🛠️ ReAct Execution Loop ({len(state.scratchpad)} tool calls)", expanded=True):
                for act in state.scratchpad:
                    st.markdown(f"**Step #{act.step_num}: `{act.action_name}`**")
                    st.markdown(f"<div class='thought-bubble'><strong>Thought:</strong> {act.thought}</div>", unsafe_allow_html=True)
                    st.caption(f"Input: `{json.dumps(act.action_input)}`")
                    with st.expander(f"View Observation #{act.step_num}", expanded=False):
                        st.json(act.observation)
                    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px dashed #cbd5e1;' />", unsafe_allow_html=True)
else:
    st.info("💡 Select one of the preset scenarios on the left or type your own query above to test the agent!")
