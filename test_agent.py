"""
Comprehensive Automated Test Suite for Techvruk AI Agentic System.
Verifies all contest criteria: Reasoning, Planning, Tool Use, Execution, and State Context.
"""

import unittest
import sys
import os

# Add local path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import SupportAgent
from agent.tools import (
    search_knowledge_base,
    lookup_customer_order,
    check_refund_eligibility,
    process_refund,
    escalate_to_human
)


class TestTechvrukAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = SupportAgent()

    def test_01_knowledge_base_search(self):
        """Test tool: search_knowledge_base returns relevant policy documents."""
        res = search_knowledge_base("what is your return window policy?")
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["matches_found"], 0)
        self.assertTrue(any("KB-001" in art["id"] for art in res["articles"]))

    def test_02_order_lookup(self):
        """Test tool: lookup_customer_order retrieves customer and order record."""
        res = lookup_customer_order(order_id="ORD-89421")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["customer"]["name"], "Sarah Jenkins")
        self.assertEqual(res["order"]["order_id"], "ORD-89421")
        self.assertEqual(res["order"]["status"], "Delivered")

    def test_03_refund_eligibility_within_30_days(self):
        """Test eligibility logic: Order within 30 days is authorized."""
        res = check_refund_eligibility(order_id="ORD-89421")
        self.assertTrue(res["eligible"])
        self.assertIn("within 30-day window", res["message"])

    def test_04_refund_eligibility_past_30_days(self):
        """Test eligibility logic: Order delivered >30 days ago is flagged for policy exception."""
        res = check_refund_eligibility(order_id="ORD-77312")
        self.assertFalse(res["eligible"])
        self.assertIn("exceeding the 30-day limit", res["message"])

    def test_05_agent_react_loop_refund_flow(self):
        """Test end-to-end agentic workflow: Plan -> Act -> Observe -> Respond for refund request."""
        query = "I bought order ORD-89421 and need a full refund because the item is defective."
        state = self.agent.run(query)

        self.assertIsNotNone(state.plan)
        self.assertGreater(len(state.plan), 2)
        self.assertGreater(len(state.scratchpad), 2)

        # Check tools were executed
        tool_names = [a.action_name for a in state.scratchpad]
        self.assertIn("search_knowledge_base", tool_names)
        self.assertIn("lookup_customer_order", tool_names)
        self.assertIn("check_refund_eligibility", tool_names)
        self.assertIn("process_refund", tool_names)

        # Verify state maintenance
        self.assertEqual(state.identified_order_id, "ORD-89421")
        self.assertIn("Refund Successfully Processed", state.final_response)

    def test_06_agent_human_escalation_protocol(self):
        """Test end-to-end agentic workflow: Distressed query triggers Tier-2 Human Escalation."""
        query = "This is UNACCEPTABLE and FRAUD! My order ORD-90214 was $649 and you lost it! Escalate to a human manager immediately or I contact my lawyer!"
        state = self.agent.run(query)

        self.assertTrue(state.escalation.is_escalated)
        self.assertEqual(state.escalation.sentiment, "angry")
        self.assertEqual(state.escalation.urgency, "critical")
        self.assertIsNotNone(state.escalation.ticket_id)
        self.assertIn("Priority Support Escalation Notice", state.final_response)
        self.assertIn(state.escalation.ticket_id, state.final_response)


if __name__ == "__main__":
    unittest.main()
