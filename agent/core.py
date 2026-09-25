"""
Core Universal Task Planner Agent Engine for Techvruk AI Contest.
Deconstructs ANY arbitrary task or goal into phased subtasks, critical path schedules,
and contingency safeguards using the ReAct pattern: Plan -> Act -> Observe -> Respond.
"""

import os
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from .state import AgentState, StructuredPlan, SubTask, RiskItem, Milestone, AgentAction
from .tools import (
    analyze_task_intent,
    audit_feasibility_and_effort,
    decompose_any_task,
    derive_critical_path_and_milestones,
    audit_failure_modes_and_safeguards,
    persist_master_plan,
    TOOL_METADATA
)


class TaskPlannerAgent:
    """
    Universal Autonomous Task Planner Agent.
    Accepts ANY task or goal from the user, autonomously decomposes it into
    actionable subtasks, maps dependencies, and generates a structured master plan.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.has_llm = bool(self.api_key)

    def run(self, user_goal: str, session_id: Optional[str] = None) -> AgentState:
        """
        Execute full agentic cycle: Plan -> Act -> Observe -> Respond.
        """
        session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        state = AgentState(
            session_id=session_id,
            user_goal=user_goal.strip(),
            status="planning"
        )

        # 1. PHASE 1: REASONING & INTENT PARSING
        intent_obs = analyze_task_intent(goal=user_goal)
        state.parsed_constraints = intent_obs
        state.status = "executing"

        # 2. PHASE 2: REACT EXECUTION LOOP (Act -> Observe -> Reason)
        self._execute_react_loop(state)

        # 3. PHASE 3: MASTER PLAN SYNTHESIS
        final_answer = self._generate_final_response(state)
        state.final_response = final_answer
        state.status = "completed"

        return state

    def _execute_react_loop(self, state: AgentState) -> None:
        """
        ReAct Execution Loop: iteratively invokes specialized tools, records observations,
        and builds the comprehensive structured plan.
        """
        goal = state.user_goal
        c = state.parsed_constraints
        category = c.get("category", "General Project")
        complexity = c.get("complexity", "Medium")
        timeline_days = c.get("timeline_days", 7)
        budget = c.get("budget")

        # --- STEP 1: Analyze Task Intent & Scope ---
        thought_1 = f"Deconstructing user intent for goal '{goal[:50]}...'. Classifying as '{category}' with '{complexity}' complexity."
        state.add_action(
            thought=thought_1,
            action_name="analyze_task_intent",
            action_input={"goal": goal},
            observation=c
        )

        # --- STEP 2: Audit Feasibility & Workload ---
        thought_2 = f"Auditing operational feasibility and workload intensity over {timeline_days} days."
        feas_obs = audit_feasibility_and_effort(
            goal=goal,
            timeline_days=timeline_days,
            complexity=complexity,
            budget=budget
        )
        state.add_action(
            thought=thought_2,
            action_name="audit_feasibility_and_effort",
            action_input={"goal": goal, "timeline_days": timeline_days, "complexity": complexity},
            observation=feas_obs
        )

        # --- STEP 3: Decompose Any Task into Phased Subtasks ---
        thought_3 = "Partitioning the objective into chronologically ordered, phase-aligned subtasks with dependency tags."
        decomp_obs = decompose_any_task(
            goal=goal,
            category=category,
            complexity=complexity,
            timeline_days=timeline_days
        )
        state.add_action(
            thought=thought_3,
            action_name="decompose_any_task",
            action_input={"goal": goal, "category": category, "timeline_days": timeline_days},
            observation=decomp_obs
        )
        raw_subtasks = decomp_obs.get("subtasks", [])

        # --- STEP 4: Derive Critical Path & Milestones ---
        thought_4 = "Calculating sequential critical path dependencies and establishing milestone gates."
        sched_obs = derive_critical_path_and_milestones(
            subtasks=raw_subtasks,
            timeline_days=timeline_days
        )
        state.add_action(
            thought=thought_4,
            action_name="derive_critical_path_and_milestones",
            action_input={"subtask_count": len(raw_subtasks), "timeline_days": timeline_days},
            observation=sched_obs
        )

        # --- STEP 5: Audit Failure Modes & Safeguards ---
        thought_5 = "Auditing operational failure points and injecting concrete mitigation safeguards."
        risk_obs = audit_failure_modes_and_safeguards(goal=goal, category=category)
        state.add_action(
            thought=thought_5,
            action_name="audit_failure_modes_and_safeguards",
            action_input={"goal": goal, "category": category},
            observation=risk_obs
        )

        # Build SubTask, Milestone, and Risk models
        subtask_models = [SubTask(**t) for t in raw_subtasks]
        milestone_models = [Milestone(**m) for m in sched_obs.get("milestones", [])]
        risk_models = [RiskItem(**r) for r in risk_obs.get("risks", [])]

        raw_plan = {
            "goal": goal,
            "category": category,
            "complexity": complexity,
            "timeline_days": timeline_days,
            "estimated_hours": feas_obs.get("estimated_total_hours", 20.0),
            "total_budget": budget,
            "subtasks": [s.model_dump() for s in subtask_models],
            "critical_path": sched_obs.get("critical_path", []),
            "milestones": [m.model_dump() for m in milestone_models],
            "risks": [r.model_dump() for r in risk_models]
        }

        # --- STEP 6: Persist Master Plan ---
        thought_6 = "Exporting and persisting compiled structured plan object into permanent memory."
        persist_obs = persist_master_plan(raw_plan)
        state.add_action(
            thought=thought_6,
            action_name="persist_master_plan",
            action_input={"goal": goal},
            observation=persist_obs
        )

        plan_id = persist_obs.get("plan_id", f"PLAN-{uuid.uuid4().hex[:6].upper()}")
        state.structured_plan = StructuredPlan(
            plan_id=plan_id,
            goal=goal,
            category=category,
            complexity=complexity,
            timeline_days=timeline_days,
            estimated_hours=feas_obs.get("estimated_total_hours", 20.0),
            total_budget=budget,
            subtasks=subtask_models,
            critical_path=sched_obs.get("critical_path", []),
            milestones=milestone_models,
            risks=risk_models
        )

    def _generate_final_response(self, state: AgentState) -> str:
        """
        Synthesize the structured plan into a clean, executive presentation roadmap.
        """
        p = state.structured_plan
        c = state.parsed_constraints

        # Group tasks by phase
        phases_map: Dict[str, List[SubTask]] = {}
        for task in p.subtasks:
            phases_map.setdefault(task.phase, []).append(task)

        task_sections = []
        for phase_name, tasks in phases_map.items():
            task_lines = [f"#### 📍 {phase_name}"]
            for t in tasks:
                p_icon = "🔴" if t.priority == "High" else "🟡"
                deps = f" *(Depends on `{', '.join(t.dependencies)}`)*" if t.dependencies else ""
                task_lines.append(f"- **`{t.task_id}` {p_icon} {t.title}** ({t.estimated_duration}){deps}")
                task_lines.append(f"  *Deliverable:* {t.deliverable}")
            task_sections.append("\n".join(task_lines))

        tasks_md = "\n\n".join(task_sections)

        # Milestones
        milestones_md = "\n".join([f"- **{m.name}** (`{m.target_timing}`): {m.criteria}" for m in p.milestones])

        # Risks
        risk_rows = []
        for r in p.risks:
            risk_rows.append(f"| {r.risk} | `{r.severity.upper()}` | {r.mitigation_strategy} |")
        risks_md = "\n".join(risk_rows)

        budget_str = f"${p.total_budget:,.2f}" if p.total_budget else "Flexible"

        return (
            f"### 📋 Autonomous Master Execution Plan: `{p.plan_id}`\n\n"
            f"> **Primary Goal:** *\"{p.goal}\"*\n"
            f"> **Category:** `{p.category}` | **Timeline:** **{p.timeline_days} Days** (~{p.estimated_hours:.0f} Total Hours) | **Budget:** **{budget_str}**\n\n"
            f"---\n\n"
            f"### 🎯 Decomposed Sub-Task Roadmap\n\n"
            f"{tasks_md}\n\n"
            f"---\n\n"
            f"### ⚡ Critical Path & Key Milestones\n"
            f"- **Sequential Critical Path:** `{' ➔ '.join(p.critical_path)}`\n\n"
            f"{milestones_md}\n\n"
            f"---\n\n"
            f"### 🛡️ Risk Audit & Contingency Safeguards\n\n"
            f"| Identified Risk | Severity | Automated Mitigation Protocol |\n"
            f"|:---|:---:|:---|\n"
            f"{risks_md}\n\n"
            f"---\n\n"
            f"✅ **Plan Status:** Compiled and archived into persistent memory as `{p.plan_id}`. Ready for execution."
        )
