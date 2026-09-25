"""
Universal Autonomous Tool Registry for Task Planner Agent.
Handles ANY arbitrary task or goal across any domain.
"""

import json
import os
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PLANS_FILE = os.path.join(DATA_DIR, "plans.json")


def _load_json(file_path: str) -> Any:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(file_path: str, data: Any) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def analyze_task_intent(goal: str) -> Dict[str, Any]:
    """
    Universally analyze ANY goal or prompt to extract intent, complexity, category, and constraints.
    """
    lower = goal.lower()

    # Domain categorization
    if any(w in lower for w in ["trip", "travel", "vacation", "visit", "tour", "flight", "hotel", "city", "explore"]):
        category = "Travel & Leisure"
    elif any(w in lower for w in ["code", "app", "software", "mvp", "build", "develop", "website", "api", "database", "ai"]):
        category = "Software & Tech Engineering"
    elif any(w in lower for w in ["study", "exam", "learn", "course", "cert", "read", "research", "paper", "write"]):
        category = "Education & Research"
    elif any(w in lower for w in ["event", "hackathon", "party", "wedding", "conference", "meetup", "celebrate", "birthday"]):
        category = "Event & Community"
    elif any(w in lower for w in ["market", "launch", "sales", "campaign", "growth", "branding", "ad", "social media"]):
        category = "Business & Marketing"
    elif any(w in lower for w in ["workout", "fitness", "run", "marathon", "diet", "gym", "health", "train"]):
        category = "Health & Fitness"
    elif any(w in lower for w in ["clean", "renovate", "organize", "move", "relocate", "paint", "house", "apartment"]):
        category = "Personal & Domestic Operations"
    else:
        category = "General Project Execution"

    # Timeline extraction
    days = 7  # default fallback
    days_m = re.search(r"(\d+)\s*(?:-| )(?:day|days)", lower)
    weeks_m = re.search(r"(\d+)\s*(?:-| )(?:week|weeks)", lower)
    months_m = re.search(r"(\d+)\s*(?:-| )(?:month|months)", lower)
    hours_m = re.search(r"(\d+)\s*(?:-| )(?:hour|hours)", lower)

    if days_m:
        days = int(days_m.group(1))
    elif weeks_m:
        days = int(weeks_m.group(1)) * 7
    elif months_m:
        days = int(months_m.group(1)) * 30
    elif hours_m:
        days = max(1, int(hours_m.group(1)) // 8)

    # Budget extraction
    budget = None
    budget_m = re.search(r"\$\s*([0-9,]+)", goal) or re.search(r"([0-9,]+)\s*(?:dollars|usd|budget)", lower)
    if budget_m:
        try:
            budget = float(budget_m.group(1).replace(",", ""))
        except ValueError:
            budget = None

    # Complexity heuristic
    word_count = len(goal.split())
    if days > 21 or (budget and budget > 3000) or word_count > 25:
        complexity = "High (Multi-Phase Complex)"
    elif days > 3 or (budget and budget > 500) or word_count > 10:
        complexity = "Medium (Standard Project)"
    else:
        complexity = "Focused (Rapid Sprint)"

    return {
        "status": "success",
        "category": category,
        "complexity": complexity,
        "timeline_days": days,
        "budget": budget,
        "key_intent": goal[:80] + ("..." if len(goal) > 80 else "")
    }


def audit_feasibility_and_effort(goal: str, timeline_days: int = 7, complexity: str = "Medium", budget: Optional[float] = None) -> Dict[str, Any]:
    """
    Assess operational feasibility, workload intensity, and potential bottlenecks for the given goal.
    """
    score = 92
    warnings = []
    recommendations = []

    # Timeline sanity check
    if timeline_days <= 1:
        score -= 25
        warnings.append("Ultra-compressed timeframe (<= 1 day). Requires strictly sequential focus.")
        recommendations.append("Eliminate optional subtasks; focus purely on the MVP deliverable.")
    elif timeline_days > 90:
        recommendations.append("Long-horizon goal: establish weekly recurring cadence to prevent momentum loss.")

    # Budget sanity check
    if budget is not None:
        if budget < 50:
            warnings.append("Extremely frugal budget ceiling. Emphasize open-source / zero-cost resources.")
        elif budget > 10000:
            recommendations.append("High capital headroom. Outsource non-core subtasks to accelerate delivery.")

    # Feasibility status
    if score >= 85:
        feasibility_status = "Optimal Feasibility"
    elif score >= 65:
        feasibility_status = "Feasible with Active Scoping"
    else:
        feasibility_status = "Highly Constrained"

    est_hours = timeline_days * 4.5  # average dedicated effort

    return {
        "status": "success",
        "feasibility_score": score,
        "feasibility_status": feasibility_status,
        "estimated_total_hours": est_hours,
        "warnings": warnings,
        "recommendations": recommendations
    }


def decompose_any_task(goal: str, category: str, complexity: str, timeline_days: int = 7) -> Dict[str, Any]:
    """
    Universally breaks down ANY task into structured, chronological subtasks across 4 core phases.
    """
    subtasks = []
    task_num = 1

    clean_goal = re.sub(r"^(plan|build|launch|organize|create|write|prepare for|do)\s+", "", goal, flags=re.IGNORECASE).strip()
    if clean_goal:
        clean_goal = clean_goal[0].upper() + clean_goal[1:]
    else:
        clean_goal = goal

    # PHASE 1: Preparation & Scoping
    subtasks.append({
        "task_id": f"TASK-0{task_num}",
        "phase": "Phase 1: Inception & Scoping",
        "title": f"Define success criteria, resource boundaries & audit prerequisites for '{clean_goal[:45]}'",
        "estimated_duration": "2-4 Hours" if timeline_days <= 3 else "1 Day",
        "priority": "High",
        "dependencies": [],
        "deliverable": "Project scope charter and confirmed resource checklist"
    })
    task_num += 1

    subtasks.append({
        "task_id": f"TASK-0{task_num}",
        "phase": "Phase 1: Inception & Scoping",
        "title": "Procure essential tooling, environment access & foundational assets",
        "estimated_duration": "2-3 Hours",
        "priority": "Medium",
        "dependencies": ["TASK-01"],
        "deliverable": "Operational workspace & required dependencies initialized"
    })
    task_num += 1

    # PHASE 2: Core Execution & Implementation (Tailored to Goal)
    if "travel" in category.lower() or any(w in goal.lower() for w in ["trip", "vacation", "tour"]):
        for day in range(1, timeline_days + 1):
            if day == 1:
                t_title = "Day 1: Arrival, local transit check-in, orientation walk & welcome dining"
            elif day == 2:
                t_title = "Day 2: Primary landmark exploration, cultural immersion & signature experiences"
            elif day == 3:
                t_title = "Day 3: Scenic outdoor excursion, local artisan markets & culinary evening"
            else:
                t_title = f"Day {day}: In-depth exploration, flexible excursions & regional highlights"

            subtasks.append({
                "task_id": f"TASK-0{task_num}",
                "phase": f"Phase 2: Day {day} Itinerary",
                "title": t_title,
                "estimated_duration": "Full Day (8-10 Hours)",
                "priority": "High",
                "dependencies": [f"TASK-0{task_num - 1}"],
                "deliverable": f"Day {day} itinerary completed"
            })
            task_num += 1

    elif "software" in category.lower() or any(w in goal.lower() for w in ["code", "app", "mvp", "build", "api"]):
        subtasks.append({
            "task_id": f"TASK-0{task_num}",
            "phase": "Phase 2: Core Engineering",
            "title": f"Implement core domain logic and primary data models for '{clean_goal[:35]}'",
            "estimated_duration": "2-3 Days" if timeline_days > 7 else "6-8 Hours",
            "priority": "High",
            "dependencies": [f"TASK-0{task_num - 1}"],
            "deliverable": "Working backend logic and verified service endpoints"
        })
        task_num += 1

        subtasks.append({
            "task_id": f"TASK-0{task_num}",
            "phase": "Phase 2: Core Engineering",
            "title": "Build interactive user interface and connect integration points",
            "estimated_duration": "2-3 Days" if timeline_days > 7 else "6-8 Hours",
            "priority": "High",
            "dependencies": [f"TASK-0{task_num - 1}"],
            "deliverable": "Responsive frontend connected to functional backend"
        })
        task_num += 1

    else:
        # Universal Milestone Progression for Any Task
        subtasks.append({
            "task_id": f"TASK-0{task_num}",
            "phase": "Phase 2: Core Execution",
            "title": f"Execute primary build / milestone milestone for '{clean_goal[:45]}'",
            "estimated_duration": "2-3 Days" if timeline_days > 5 else "4-6 Hours",
            "priority": "High",
            "dependencies": [f"TASK-0{task_num - 1}"],
            "deliverable": "Core work items executed and draft artifacts produced"
        })
        task_num += 1

        subtasks.append({
            "task_id": f"TASK-0{task_num}",
            "phase": "Phase 2: Core Execution",
            "title": "Iterate, refine components and synthesize initial feedback",
            "estimated_duration": "1-2 Days" if timeline_days > 5 else "3-4 Hours",
            "priority": "Medium",
            "dependencies": [f"TASK-0{task_num - 1}"],
            "deliverable": "Refined prototype / deliverables incorporating improvements"
        })
        task_num += 1

    # PHASE 3: Review, Quality Assurance & Polish
    subtasks.append({
        "task_id": f"TASK-0{task_num}",
        "phase": "Phase 3: Validation & Quality Control",
        "title": "Perform rigorous quality audit, edge-case testing and checklist review",
        "estimated_duration": "3-5 Hours" if timeline_days <= 3 else "1 Day",
        "priority": "High",
        "dependencies": [f"TASK-0{task_num - 1}"],
        "deliverable": "QA sign-off with zero unresolved blockers"
    })
    task_num += 1

    # PHASE 4: Final Handover, Launch & Archival
    subtasks.append({
        "task_id": f"TASK-0{task_num}",
        "phase": "Phase 4: Launch & Final Delivery",
        "title": f"Final execution, stakeholder handover and publication of '{clean_goal[:35]}'",
        "estimated_duration": "2-4 Hours",
        "priority": "High",
        "dependencies": [f"TASK-0{task_num - 1}"],
        "deliverable": "Master objective delivered and plan closed"
    })

    return {
        "status": "success",
        "total_subtasks": len(subtasks),
        "subtasks": subtasks
    }


def derive_critical_path_and_milestones(subtasks: List[Dict[str, Any]], timeline_days: int = 7) -> Dict[str, Any]:
    """
    Extract the sequential critical path and compute 3 key project milestone gates.
    """
    critical_path = [t["task_id"] for t in subtasks if t.get("priority") == "High"]
    if not critical_path and subtasks:
        critical_path = [t["task_id"] for t in subtasks[:3]]

    milestones = [
        {"name": "Milestone Alpha: Scoping & Setup Sign-Off", "target_timing": "Day 1", "criteria": "Prerequisites and workspace confirmed."},
        {"name": "Milestone Beta: Core Deliverables Substantially Complete", "target_timing": f"Day {max(1, timeline_days // 2)}", "criteria": "Primary feature / activity executed."},
        {"name": "Milestone Final: Complete Goal Delivery & Closure", "target_timing": f"Day {timeline_days}", "criteria": "All deliverables validated and archived."}
    ]

    return {
        "status": "success",
        "critical_path": critical_path,
        "critical_path_length": len(critical_path),
        "milestones": milestones
    }


def audit_failure_modes_and_safeguards(goal: str, category: str) -> Dict[str, Any]:
    """
    Audits universal and domain risks and provides automated mitigation safeguards.
    """
    risks = [
        {
            "risk": "Schedule slip due to unanticipated scope expansion",
            "severity": "High",
            "mitigation_strategy": "Enforce strict milestone guardrails; freeze non-essential tasks to v1.1 backlog."
        },
        {
            "risk": "External dependency delays (third-party tools, transit, weather)",
            "severity": "Medium",
            "mitigation_strategy": "Pre-arrange redundant backup options (e.g. offline assets, open vouchers)."
        },
        {
            "risk": "Resource or budget exhaustion before completion",
            "severity": "Medium",
            "mitigation_strategy": "Maintain an explicit 10-15% unallocated financial and temporal buffer."
        }
    ]

    # Category-specific additions
    if "travel" in category.lower():
        risks.append({
            "risk": "Attraction closures or sold-out reservations",
            "severity": "High",
            "mitigation_strategy": "Book timed-entry passes in advance and identify nearby backup alternatives."
        })
    elif "software" in category.lower():
        risks.append({
            "risk": "Integration bugs and unhandled API rate limits",
            "severity": "High",
            "mitigation_strategy": "Implement exponential backoff retries and local response caching."
        })

    return {
        "status": "success",
        "risks": risks
    }


def persist_master_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist compiled plan into storage.
    """
    plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    plan_data["plan_id"] = plan_id
    plan_data["saved_at"] = datetime.now().isoformat()

    plans = _load_json(PLANS_FILE)
    plans.append(plan_data)
    _save_json(PLANS_FILE, plans)

    return {
        "status": "persisted",
        "plan_id": plan_id,
        "message": f"Master plan compiled and persisted as {plan_id}."
    }


TOOL_METADATA = [
    {
        "name": "analyze_task_intent",
        "description": "Analyzes any task or goal to determine category, complexity tier, duration constraints, and budget limits.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Raw task or goal text."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "audit_feasibility_and_effort",
        "description": "Calculates workload intensity, feasibility score (0-100), and scope recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "User goal."},
                "timeline_days": {"type": "integer", "description": "Duration in days."},
                "complexity": {"type": "string", "description": "Complexity tier."},
                "budget": {"type": "number", "description": "Optional budget."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "decompose_any_task",
        "description": "Dynamically breaks down any task into phased, chronological subtasks with duration estimates and deliverables.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "User goal."},
                "category": {"type": "string", "description": "Identified category."},
                "complexity": {"type": "string", "description": "Complexity level."},
                "timeline_days": {"type": "integer", "description": "Timeline in days."}
            },
            "required": ["goal", "category"]
        }
    },
    {
        "name": "derive_critical_path_and_milestones",
        "description": "Derives the sequential bottleneck path and milestone checkpoints across subtasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "subtasks": {"type": "array", "description": "List of subtask dictionaries."},
                "timeline_days": {"type": "integer", "description": "Timeline in days."}
            },
            "required": ["subtasks"]
        }
    },
    {
        "name": "audit_failure_modes_and_safeguards",
        "description": "Evaluates operational risks and pairs each with an automated contingency safeguard.",
        "parameters": {
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "User goal."},
                "category": {"type": "string", "description": "Goal category."}
            },
            "required": ["goal"]
        }
    },
    {
        "name": "persist_master_plan",
        "description": "Persists the complete structured master plan into permanent records.",
        "parameters": {
            "type": "object",
            "properties": {
                "plan_data": {"type": "object", "description": "Complete plan dictionary."}
            },
            "required": ["plan_data"]
        }
    }
]
