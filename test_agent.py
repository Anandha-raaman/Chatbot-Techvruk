"""
Automated Test Suite for Techvruk Task Planner Agent.
Verifies all core contest requirements:
- Goal acceptance (text-based input)
- Task breakdown into logical steps (planning)
- LLM/Agent reasoning & tool use (Act & Observe)
- State and context maintenance
- Final coherent structured plan generation.
"""

import unittest
import sys
import os

# Add local path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import TaskPlannerAgent
from agent.tools import (
    search_domain_blueprints,
    analyze_goal_feasibility,
    decompose_into_subtasks,
    calculate_schedule_and_critical_path,
    assess_risks_and_mitigations,
    export_structured_plan
)


class TestTaskPlannerAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = TaskPlannerAgent()

    def test_01_search_domain_blueprints(self):
        """Verify tool: search_domain_blueprints identifies trip and software phases."""
        res = search_domain_blueprints("plan a 3-day trip to Tokyo")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["domain"], "trip_planning")
        self.assertGreater(len(res["phases"]), 0)

    def test_02_analyze_goal_feasibility(self):
        """Verify tool: analyze_goal_feasibility computes feasibility scores and warnings."""
        res = analyze_goal_feasibility(goal="Launch complete enterprise ERP in 1 day", timeline_days=1)
        self.assertLess(res["feasibility_score"], 80)
        self.assertGreater(len(res["warnings"]), 0)

    def test_03_decompose_trip_planning_goal(self):
        """Verify tool: decompose_into_subtasks correctly builds phased tasks for a 3-day trip."""
        res = decompose_into_subtasks(goal="plan a 3-day trip to Tokyo", domain="trip_planning", timeline_days=3)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["total_subtasks"], 5)
        task_titles = [t["title"] for t in res["subtasks"]]
        self.assertTrue(any("Day 1" in t for t in task_titles))
        self.assertTrue(any("Day 2" in t for t in task_titles))
        self.assertTrue(any("Day 3" in t for t in task_titles))

    def test_04_critical_path_and_schedule(self):
        """Verify tool: calculate_schedule_and_critical_path identifies critical chain and milestones."""
        decomp = decompose_into_subtasks(goal="plan a 3-day trip to Tokyo", domain="trip_planning", timeline_days=3)
        res = calculate_schedule_and_critical_path(subtasks=decomp["subtasks"], timeline_days=3)
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["critical_path"]), 0)
        self.assertGreaterEqual(len(res["milestones"]), 2)

    def test_05_risk_assessment_and_mitigation(self):
        """Verify tool: assess_risks_and_mitigations extracts mitigations."""
        res = assess_risks_and_mitigations(goal="plan a 3-day trip", domain="trip_planning")
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["risk_matrix"]), 0)
        for r in res["risk_matrix"]:
            self.assertIn("risk", r)
            self.assertIn("mitigation", r)

    def test_06_end_to_end_agentic_workflow_trip_plan(self):
        """Verify complete ReAct cycle: given a goal, breaks it into sub-tasks and generates a structured plan."""
        goal = "Plan a 3-day cultural and culinary trip to Tokyo on a $1,200 budget for 2 people"
        state = self.agent.run(goal)

        # 1. State Context Checks
        self.assertEqual(state.status, "completed")
        self.assertEqual(state.parsed_constraints["timeline_days"], 3)
        self.assertEqual(state.parsed_constraints["budget"], 1200.0)

        # 2. Tool Execution Checks (Act & Observe Scratchpad)
        tool_names = [a.action_name for a in state.scratchpad]
        self.assertIn("search_domain_blueprints", tool_names)
        self.assertIn("analyze_goal_feasibility", tool_names)
        self.assertIn("decompose_into_subtasks", tool_names)
        self.assertIn("calculate_schedule_and_critical_path", tool_names)
        self.assertIn("assess_risks_and_mitigations", tool_names)
        self.assertIn("export_structured_plan", tool_names)

        # 3. Structured Plan Integrity Checks
        plan = state.structured_plan
        self.assertIsNotNone(plan)
        self.assertTrue(plan.plan_id.startswith("PLAN-"))
        self.assertEqual(plan.timeline_days, 3)
        self.assertGreater(len(plan.subtasks), 4)
        self.assertGreater(len(plan.critical_path), 0)
        self.assertGreater(len(plan.budget_breakdown), 0)

        # 4. Final Output Verification
        self.assertIn("Autonomous Master Execution Plan", state.final_response)
        self.assertIn("Decomposed Sub-Task Roadmap", state.final_response)
        self.assertIn("Critical Path", state.final_response)
        self.assertIn("Budget Allocation", state.final_response)


if __name__ == "__main__":
    unittest.main()
