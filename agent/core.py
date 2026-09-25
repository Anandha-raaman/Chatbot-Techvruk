"""
Core Autonomous Task Planner Agent Engine for Techvruk AI Contest.
Implements the explicit ReAct pattern: Plan -> Act -> Observe -> Respond.
Given a user goal (e.g., 'plan a 3-day trip' or 'launch an MVP in 4 weeks'),
autonomously breaks it into sub-tasks and generates a comprehensive structured plan.
"""

import os
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from .state import AgentState, StructuredPlan, SubTask, RiskItem, BudgetAllocation, AgentAction
from .tools import (
    search_domain_blueprints,
    analyze_goal_feasibility,
    decompose_into_subtasks,
    calculate_schedule_and_critical_path,
    assess_risks_and_mitigations,
    export_structured_plan,
    TOOL_METADATA
)


class TaskPlannerAgent:
    """
    Autonomous Task Planner Agent.
    Deconstructs high-level user goals into structured, phased sub-tasks,
    audits feasibility, determines critical paths, assigns mitigations,
    and compiles deterministic execution plans.
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
            user_goal=user_goal,
            status="planning"
        )

        # 1. PHASE 1: CONSTRAINT PARSING & DOMAIN DETECTION
        constraints = self._extract_constraints(user_goal)
        state.parsed_constraints = constraints
        state.status = "executing"

        # 2. PHASE 2: REACT EXECUTION LOOP (Act -> Observe -> Reason)
        self._execute_react_loop(state)

        # 3. PHASE 3: FINAL STRUCTURED SYNTHESIS
        final_answer = self._generate_final_response(state)
        state.final_response = final_answer
        state.status = "completed"

        return state

    def _extract_constraints(self, goal: str) -> Dict[str, Any]:
        """
        Extract numerical duration, budget, and domain entities from goal text.
        """
        lower = goal.lower()

        # Extract days/duration
        days = 3  # default
        days_match = re.search(r"(\d+)\s*(?:-| )(?:day|days)", lower)
        week_match = re.search(r"(\d+)\s*(?:-| )(?:week|weeks)", lower)
        month_match = re.search(r"(\d+)\s*(?:-| )(?:month|months)", lower)

        if days_match:
            days = int(days_match.group(1))
        elif week_match:
            days = int(week_match.group(1)) * 7
        elif month_match:
            days = int(month_match.group(1)) * 30

        # Extract budget ($1200 or 1200 dollars)
        budget = None
        budget_match = re.search(r"\$\s*([0-9,]+)", goal) or re.search(r"([0-9,]+)\s*(?:dollars|usd|budget)", lower)
        if budget_match:
            try:
                budget = float(budget_match.group(1).replace(",", ""))
            except ValueError:
                budget = None

        # Detect domain
        domain = "trip_planning"
        if any(w in lower for w in ["trip", "vacation", "tokyo", "paris", "bali", "tour", "travel", "flight", "hotel"]):
            domain = "trip_planning"
        elif any(w in lower for w in ["software", "mvp", "app", "saas", "code", "dev", "feature", "build", "frontend"]):
            domain = "software_launch"
        elif any(w in lower for w in ["hackathon", "event", "conference", "summit", "meetup", "workshop"]):
            domain = "event_management"

        return {
            "timeline_days": days,
            "budget": budget,
            "domain": domain
        }

    def _execute_react_loop(self, state: AgentState) -> None:
        """
        ReAct Execution: iteratively calls tools, collects observations, and updates state.
        """
        goal = state.user_goal
        c = state.parsed_constraints
        domain = c["domain"]
        timeline_days = c["timeline_days"]
        budget = c["budget"]

        # --- STEP 1: Search Domain Blueprints ---
        thought_1 = f"I need to query domain blueprints for '{domain}' to identify standard milestone phases and structure."
        bp_obs = search_domain_blueprints(domain_or_goal=goal)
        state.add_action(
            thought=thought_1,
            action_name="search_domain_blueprints",
            action_input={"domain_or_goal": goal},
            observation=bp_obs
        )

        # --- STEP 2: Analyze Goal Feasibility ---
        thought_2 = f"Assessing feasibility of goal over {timeline_days} days with a target budget of ${budget if budget else 'Flexible'}."
        feas_obs = analyze_goal_feasibility(goal=goal, timeline_days=timeline_days, budget=budget)
        state.add_action(
            thought=thought_2,
            action_name="analyze_goal_feasibility",
            action_input={"goal": goal, "timeline_days": timeline_days, "budget": budget},
            observation=feas_obs
        )

        # --- STEP 3: Decompose into Subtasks ---
        thought_3 = f"Deconstructing goal into actionable, phase-aligned subtasks with dependency tagging and duration estimates."
        decomp_obs = decompose_into_subtasks(goal=goal, domain=domain, timeline_days=timeline_days)
        state.add_action(
            thought=thought_3,
            action_name="decompose_into_subtasks",
            action_input={"goal": goal, "domain": domain, "timeline_days": timeline_days},
            observation=decomp_obs
        )
        raw_subtasks = decomp_obs.get("subtasks", [])

        # --- STEP 4: Calculate Critical Path & Schedule ---
        thought_4 = "Calculating critical path, execution dependencies, and milestone checkpoints across subtasks."
        sched_obs = calculate_schedule_and_critical_path(subtasks=raw_subtasks, timeline_days=timeline_days)
        state.add_action(
            thought=thought_4,
            action_name="calculate_schedule_and_critical_path",
            action_input={"subtasks_count": len(raw_subtasks), "timeline_days": timeline_days},
            observation=sched_obs
        )

        # --- STEP 5: Assess Risks & Mitigations ---
        thought_5 = "Evaluating operational failure points and injecting concrete mitigation safeguards."
        risk_obs = assess_risks_and_mitigations(goal=goal, domain=domain)
        state.add_action(
            thought=thought_5,
            action_name="assess_risks_and_mitigations",
            action_input={"goal": goal, "domain": domain},
            observation=risk_obs
        )

        # Compile Budget Breakdown
        alloc_pct = bp_obs.get("budget_allocation_pct", {})
        base_budget = budget or (1200.0 if domain == "trip_planning" else 2500.0)
        budget_items = []
        for cat, pct in alloc_pct.items():
            budget_items.append(BudgetAllocation(
                category=cat.replace("_", " ").title(),
                percentage=pct,
                estimated_amount=round((pct / 100.0) * base_budget, 2),
                notes=f"{pct}% of overall estimated budget"
            ))

        # Build SubTask models
        subtask_models = [SubTask(**t) for t in raw_subtasks]
        risk_models = [RiskItem(risk=r["risk"], severity=r["severity"], mitigation_strategy=r["mitigation"]) for r in risk_obs.get("risk_matrix", [])]

        structured_plan_data = {
            "goal_title": goal,
            "domain": domain,
            "timeline_days": timeline_days,
            "total_budget": base_budget,
            "subtasks": [s.model_dump() for s in subtask_models],
            "critical_path": sched_obs.get("critical_path", []),
            "risks": [r.model_dump() for r in risk_models],
            "budget_breakdown": [b.model_dump() for b in budget_items]
        }

        # --- STEP 6: Export Plan to Permanent Record ---
        thought_6 = "Exporting and persisting compiled structured plan object into permanent CRM / database records."
        export_obs = export_structured_plan(structured_plan_data)
        state.add_action(
            thought=thought_6,
            action_name="export_structured_plan",
            action_input={"goal": goal},
            observation=export_obs
        )

        # Update state with plan
        structured_plan_data["plan_id"] = export_obs.get("plan_id", "PLAN-GEN")
        state.structured_plan = StructuredPlan(
            plan_id=export_obs.get("plan_id", "PLAN-GEN"),
            goal_title=goal,
            domain=domain,
            timeline_days=timeline_days,
            total_budget=base_budget,
            subtasks=subtask_models,
            critical_path=sched_obs.get("critical_path", []),
            risks=risk_models,
            budget_breakdown=budget_items
        )

    def _generate_final_response(self, state: AgentState) -> str:
        """
        Synthesize the structured plan into an executive, presentation-grade response.
        """
        p = state.structured_plan
        c = state.parsed_constraints

        # Build task list by phase
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

        # Build Budget Table
        budget_rows = []
        for b in p.budget_breakdown:
            budget_rows.append(f"| {b.category} | {b.percentage}% | **${b.estimated_amount:,.2f}** | {b.notes} |")
        budget_md = "\n".join(budget_rows)

        # Build Risk Table
        risk_rows = []
        for r in p.risks:
            s_badge = f"`{r.severity.upper()}`"
            risk_rows.append(f"| {r.risk} | {s_badge} | {r.mitigation_strategy} |")
        risk_md = "\n".join(risk_rows)

        return (
            f"### 📋 Autonomous Master Execution Plan: `{p.plan_id}`\n\n"
            f"> **Primary Goal:** *\"{p.goal_title}\"*\n"
            f"> **Domain:** `{p.domain.upper()}` | **Timeline:** **{p.timeline_days} Days** | **Estimated Budget:** **${p.total_budget:,.2f}**\n\n"
            f"---\n\n"
            f"### 🎯 Decomposed Sub-Task Roadmap\n\n"
            f"{tasks_md}\n\n"
            f"---\n\n"
            f"### ⚡ Critical Path & Milestone Schedule\n"
            f"- **Critical Sequential Path:** `{' ➔ '.join(p.critical_path)}`\n"
            f"- **Key Milestone 1 (Day 1):** Pre-departure logistics & baseline setup verified.\n"
            f"- **Key Milestone 2 (Midpoint):** Core execution underway with zero dependency blockers.\n"
            f"- **Key Milestone 3 (Final Day):** Full objective fulfilled, artifacts persisted, and wrap-up verified.\n\n"
            f"---\n\n"
            f"### 💰 Resource & Budget Allocation (${p.total_budget:,.2f})\n\n"
            f"| Expense Category | Allocation % | Estimated Cost | Notes |\n"
            f"|:---|:---:|:---:|:---|\n"
            f"{budget_md}\n\n"
            f"---\n\n"
            f"### 🛡️ Risk Audit & Contingency Matrix\n\n"
            f"| Identified Risk | Severity | Automated Mitigation Protocol |\n"
            f"|:---|:---:|:---|\n"
            f"{risk_md}\n\n"
            f"---\n\n"
            f"✅ **Plan Status:** Compiled and archived into persistent memory as `{p.plan_id}`. Ready for immediate execution."
        )
