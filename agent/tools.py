"""
Autonomous Tool Registry for Task Planner Agent.
Provides specialized tools for goal analysis, task decomposition, scheduling, risk auditing, and export.
"""

import json
import os
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
BLUEPRINTS_FILE = os.path.join(DATA_DIR, "planner_blueprints.json")
PLANS_FILE = os.path.join(DATA_DIR, "plans.json")


def _load_json(file_path: str) -> Any:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(file_path: str, data: Any) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def search_domain_blueprints(domain_or_goal: str) -> Dict[str, Any]:
    """
    Search domain-specific planning templates and historical task blueprints.
    Args:
        domain_or_goal: The user goal or domain name (e.g., 'trip', 'software launch', 'event').
    Returns:
        Dict with matched blueprint, standard phases, and baseline tasks.
    """
    blueprints = _load_json(BLUEPRINTS_FILE)
    tokens = set(re.findall(r"\w+", domain_or_goal.lower()))

    best_match = None
    best_score = -1

    for bp in blueprints:
        score = 0
        keywords = bp.get("keywords", [])
        for t in tokens:
            if t in bp.get("domain", ""):
                score += 5
            for kw in keywords:
                if t in kw:
                    score += 3
        if score > best_score:
            best_score = score
            best_match = bp

    if not best_match or best_score == 0:
        # Default fallback to trip planning template if ambiguous
        best_match = blueprints[0] if blueprints else {}

    return {
        "status": "success",
        "domain": best_match.get("domain", "general_project"),
        "blueprint_name": best_match.get("name", "Standard Project Blueprint"),
        "phases": best_match.get("phases", []),
        "budget_allocation_pct": best_match.get("budget_allocation_pct", {}),
        "typical_risks": best_match.get("typical_risks", [])
    }


def analyze_goal_feasibility(goal: str, timeline_days: int = 3, budget: Optional[float] = None) -> Dict[str, Any]:
    """
    Evaluate scope, timeline, and budget feasibility.
    Args:
        goal: Stated objective.
        timeline_days: Available days/duration.
        budget: Stated budget if provided.
    Returns:
        Feasibility score (0-100), risk status, and scope recommendations.
    """
    score = 90
    warnings = []
    recommendations = []

    # Timeline constraint checks
    if timeline_days < 1:
        score -= 40
        warnings.append("Timeline is too compressed (< 1 day) for meaningful execution.")
    elif timeline_days <= 2 and any(w in goal.lower() for w in ["software", "hackathon", "conference", "erp", "enterprise", "system", "app"]):
        score -= 30
        warnings.append("Complex technical projects in <= 2 days face severe scope compression.")
        recommendations.append("Limit scope to an ultra-focused prototype demonstration.")

    # Budget constraint checks
    if budget is not None:
        if budget < 100:
            score -= 20
            warnings.append("Extremely tight budget; prioritize free/public transit and open-source tools.")
        elif budget > 5000:
            recommendations.append("High budget headroom; reserve premier experiences and comprehensive contingencies.")

    feasibility_status = "Highly Feasible" if score >= 80 else ("Feasible with Scoping" if score >= 60 else "High Risk / Constrained")

    return {
        "feasibility_score": max(0, min(100, score)),
        "status": feasibility_status,
        "timeline_days": timeline_days,
        "budget": budget,
        "warnings": warnings,
        "recommendations": recommendations
    }


def decompose_into_subtasks(goal: str, domain: str, timeline_days: int = 3, pace: str = "moderate") -> Dict[str, Any]:
    """
    Deconstruct goal into chronologically ordered, phase-aligned subtasks with dependency tags.
    """
    blueprint_res = search_domain_blueprints(domain)
    phases = blueprint_res.get("phases", [])

    generated_subtasks = []
    task_counter = 1

    # Specific handling for Trip Planning (e.g. 3-day trip)
    if "trip" in domain or any(k in goal.lower() for k in ["trip", "vacation", "tokyo", "paris", "bali", "tour", "travel"]):
        # Phase 1: Planning & Logistics
        generated_subtasks.append({
            "task_id": f"TASK-0{task_counter}",
            "phase": "Phase 1: Pre-Departure Logistics",
            "title": "Finalize transit tickets, airport transfers & book central accommodations",
            "estimated_duration": "4 Hours",
            "priority": "High",
            "dependencies": [],
            "deliverable": "Confirmed booking vouchers & arrival itinerary"
        })
        task_counter += 1

        generated_subtasks.append({
            "task_id": f"TASK-0{task_counter}",
            "phase": "Phase 1: Pre-Departure Logistics",
            "title": "Secure local eSIM/mobile data and pre-order regional transit passes",
            "estimated_duration": "1 Hour",
            "priority": "Medium",
            "dependencies": ["TASK-01"],
            "deliverable": "Active connectivity & digital transit cards"
        })
        task_counter += 1

        # Phase 2: Daily Itineraries based on timeline_days
        for day in range(1, timeline_days + 1):
            if day == 1:
                title = "Day 1: Arrival, neighborhood orientation walk, and signature welcome dinner"
            elif day == 2:
                title = "Day 2: Morning cultural heritage landmarks, afternoon museums & evening food tour"
            elif day == 3:
                title = "Day 3: Scenic outdoor/nature exploration, artisan market shopping & farewell dinner"
            else:
                title = f"Day {day}: Extended excursion, specialty workshops, and regional sightseeing"

            generated_subtasks.append({
                "task_id": f"TASK-0{task_counter}",
                "phase": f"Phase 2: Day {day} Execution",
                "title": title,
                "estimated_duration": "Full Day (8-10 Hours)",
                "priority": "High",
                "dependencies": [f"TASK-0{task_counter - 1}"],
                "deliverable": f"Completed Day {day} experiential itinerary"
            })
            task_counter += 1

        # Phase 3: Departure Logistics
        generated_subtasks.append({
            "task_id": f"TASK-0{task_counter}",
            "phase": "Phase 3: Wrap-Up & Departure",
            "title": "Pack souvenirs, settle lodging expenses & execute return transit transfer",
            "estimated_duration": "3 Hours",
            "priority": "Medium",
            "dependencies": [f"TASK-0{task_counter - 1}"],
            "deliverable": "Smooth checkout and return departure"
        })

    else:
        # General Software / Event / Project decomposition
        for p_idx, phase in enumerate(phases):
            p_name = phase.get("phase_name", f"Phase {p_idx+1}")
            for t_idx, standard_t in enumerate(phase.get("standard_tasks", [])):
                dep = [f"TASK-0{task_counter-1}"] if task_counter > 1 else []
                generated_subtasks.append({
                    "task_id": f"TASK-0{task_counter}",
                    "phase": p_name,
                    "title": standard_t,
                    "estimated_duration": "1-2 Days" if timeline_days > 7 else "3-5 Hours",
                    "priority": "High" if t_idx == 0 else "Medium",
                    "dependencies": dep,
                    "deliverable": f"Completed deliverable for {standard_t[:30]}..."
                })
                task_counter += 1

    return {
        "status": "success",
        "total_subtasks": len(generated_subtasks),
        "subtasks": generated_subtasks
    }


def calculate_schedule_and_critical_path(subtasks: List[Dict[str, Any]], timeline_days: int = 3) -> Dict[str, Any]:
    """
    Calculate critical path and parallel execution tracks across the schedule.
    """
    critical_path = [t["task_id"] for t in subtasks if t.get("priority") == "High"]
    
    # Identify milestones
    milestones = []
    if subtasks:
        milestones.append({"milestone": "Logistics & Readiness Milestone", "target_day": "Day 1 (Morning)"})
        halfway = max(1, timeline_days // 2)
        milestones.append({"milestone": "Midpoint Core Execution Checkpoint", "target_day": f"Day {halfway}"})
        milestones.append({"milestone": "Final Completion & Wrap-Up", "target_day": f"Day {timeline_days}"})

    return {
        "status": "success",
        "critical_path": critical_path,
        "critical_task_count": len(critical_path),
        "milestones": milestones,
        "recommended_pace": "Optimized Sequential Pipeline"
    }


def assess_risks_and_mitigations(goal: str, domain: str) -> Dict[str, Any]:
    """
    Identify high-impact operational risks and inject contingency protocols.
    """
    bp = search_domain_blueprints(domain)
    risks = bp.get("typical_risks", [])

    return {
        "status": "success",
        "identified_risks_count": len(risks),
        "risk_matrix": risks
    }


def export_structured_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist structured plan into permanent storage.
    """
    plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    plan_data["plan_id"] = plan_id
    plan_data["saved_at"] = datetime.now().isoformat()

    plans = _load_json(PLANS_FILE)
    plans.append(plan_data)
    _save_json(PLANS_FILE, plans)

    return {
        "status": "exported",
        "plan_id": plan_id,
        "message": f"Plan successfully compiled and saved with ID {plan_id}."
    }


TOOL_METADATA = [
    {
        "name": "search_domain_blueprints",
        "description": "Searches domain templates (trips, software launches, events) for standard phases and typical task structures.",
        "parameters": {
            "type": "object",
            "properties": {
                "domain_or_goal": {"type": "string", "description": "Goal description or domain name."}
            },
            "required": ["domain_or_goal"]
        }
    },
    {
        "name": "analyze_goal_feasibility",
        "description": "Evaluates feasibility of goal against timeline constraints and budget limits.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Primary goal to analyze."},
                "timeline_days": {"type": "integer", "description": "Total duration in days."},
                "budget": {"type": "number", "description": "Budget limit if specified."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "decompose_into_subtasks",
        "description": "Breaks down a goal into phase-aligned, sequential subtasks with duration estimates and dependencies.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "The user's goal."},
                "domain": {"type": "string", "description": "Matched domain."},
                "timeline_days": {"type": "integer", "description": "Duration in days."}
            },
            "required": ["goal", "domain"]
        }
    },
    {
        "name": "calculate_schedule_and_critical_path",
        "description": "Determines the critical path, milestones, and schedule dependencies across subtasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "subtasks": {"type": "array", "description": "List of decomposed subtasks."},
                "timeline_days": {"type": "integer", "description": "Duration in days."}
            },
            "required": ["subtasks"]
        }
    },
    {
        "name": "assess_risks_and_mitigations",
        "description": "Audits operational risks and generates concrete mitigation safeguards.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Stated goal."},
                "domain": {"type": "string", "description": "Identified domain."}
            },
            "required": ["goal", "domain"]
        }
    },
    {
        "name": "export_structured_plan",
        "description": "Saves and exports the finalized structured plan object to persistent storage.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_data": {"type": "object", "description": "Complete structured plan dictionary."}
            },
            "required": ["plan_data"]
        }
    }
]
