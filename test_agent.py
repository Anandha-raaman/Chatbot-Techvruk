"""
Automated Test Suite for Universal Task Planner Agent.
Verifies all contest criteria for ANY arbitrary goal or task input.
"""

import unittest
import sys
import os

# Add local path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import TaskPlannerAgent
from agent.tools import (
    analyze_task_intent,
    audit_feasibility_and_effort,
    decompose_any_task,
    derive_critical_path_and_milestones,
    audit_failure_modes_and_safeguards,
    persist_master_plan
)


class TestUniversalTaskPlanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = TaskPlannerAgent()

    def test_01_analyze_task_intent(self):
        """Test tool: analyze_task_intent extracts category, duration, and complexity from any prompt."""
        t1 = analyze_task_intent("Plan a 3-day trip to Tokyo with cultural sightseeing")
        self.assertEqual(t1["category"], "Travel & Leisure")
        self.assertEqual(t1["timeline_days"], 3)

        t2 = analyze_task_intent("Build an AI web app in 2 weeks with a $500 budget")
        self.assertEqual(t2["category"], "Software & Tech Engineering")
        self.assertEqual(t2["timeline_days"], 14)
        self.assertEqual(t2["budget"], 500.0)

    def test_02_audit_feasibility(self):
        """Test tool: audit_feasibility_and_effort calculates score and estimated hours."""
        res = audit_feasibility_and_effort(goal="Organize a technical summit", timeline_days=10)
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["feasibility_score"], 70)
        self.assertGreater(res["estimated_total_hours"], 10)

    def test_03_decompose_arbitrary_task(self):
        """Test tool: decompose_any_task decomposes ANY task into 4 phased subtasks with deliverables."""
        res = decompose_any_task(
            goal="Write a 20-page research paper on quantum computing in 10 days",
            category="Education & Research",
            complexity="Medium",
            timeline_days=10
        )
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["total_subtasks"], 5)
        for task in res["subtasks"]:
            self.assertTrue(task["task_id"].startswith("TASK-"))
            self.assertIn("phase", task)
            self.assertIn("deliverable", task)

    def test_04_critical_path_and_milestones(self):
        """Test tool: derive_critical_path_and_milestones establishes critical chain and gates."""
        decomp = decompose_any_task("Organize a 2-day hackathon", "Event & Community", "Medium", 14)
        res = derive_critical_path_and_milestones(decomp["subtasks"], timeline_days=14)
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["critical_path"]), 0)
        self.assertEqual(len(res["milestones"]), 3)

    def test_05_risk_safeguards(self):
        """Test tool: audit_failure_modes_and_safeguards returns mitigations."""
        res = audit_failure_modes_and_safeguards("Renovate kitchen with $4000", "Personal & Domestic Operations")
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(len(res["risks"]), 3)

    def test_06_end_to_end_universal_planning(self):
        """Test full ReAct cycle on an arbitrary custom goal."""
        goal = "Prepare for the AWS Solutions Architect exam in 30 days studying 2 hours a day"
        state = self.agent.run(goal)

        self.assertEqual(state.status, "completed")
        self.assertEqual(state.parsed_constraints["timeline_days"], 30)

        # Check all tools executed in scratchpad
        tool_names = [a.action_name for a in state.scratchpad]
        self.assertIn("analyze_task_intent", tool_names)
        self.assertIn("audit_feasibility_and_effort", tool_names)
        self.assertIn("decompose_any_task", tool_names)
        self.assertIn("derive_critical_path_and_milestones", tool_names)
        self.assertIn("audit_failure_modes_and_safeguards", tool_names)
        self.assertIn("persist_master_plan", tool_names)

        # Verify structured plan and response
        plan = state.structured_plan
        self.assertIsNotNone(plan)
        self.assertTrue(plan.plan_id.startswith("PLAN-"))
        self.assertIn("Autonomous Master Execution Plan", state.final_response)


if __name__ == "__main__":
    unittest.main()
