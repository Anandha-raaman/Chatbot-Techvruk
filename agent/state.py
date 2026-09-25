"""
Agent State Models for Techvruk AI Agentic System.
Maintains structured context across the Plan -> Act -> Observe -> Respond lifecycle.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentAction(BaseModel):
    """Record of an executed tool action and observation in the ReAct loop."""
    step_num: int
    thought: str = Field(description="Agent's reasoning behind choosing this action")
    action_name: str = Field(description="Name of the tool invoked")
    action_input: Dict[str, Any] = Field(default_factory=dict, description="Parameters supplied to the tool")
    observation: Any = Field(default=None, description="Raw feedback or output received from the tool")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PlanStep(BaseModel):
    """Sub-task step within the decomposed plan."""
    step_id: int
    description: str
    status: str = Field(default="pending", description="Status: pending, in_progress, completed, failed")
    tool_hint: Optional[str] = None


class EscalationDetail(BaseModel):
    """Metadata recorded when a query exceeds autonomous policy or customer is distressed."""
    is_escalated: bool = False
    urgency: str = "normal"  # low, normal, high, critical
    sentiment: str = "neutral"  # positive, neutral, frustrated, angry
    escalation_reason: str = ""
    assigned_tier: str = "Tier-2 Human Specialist"
    sla_minutes: int = 15
    ticket_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AgentState(BaseModel):
    """State maintaining full context across multi-step execution."""
    session_id: str
    user_query: str
    plan: List[PlanStep] = Field(default_factory=list)
    scratchpad: List[AgentAction] = Field(default_factory=list)
    identified_customer_id: Optional[str] = None
    identified_order_id: Optional[str] = None
    escalation: EscalationDetail = Field(default_factory=EscalationDetail)
    final_response: Optional[str] = None
    status: str = "initialized"  # initialized, planning, executing, completed, escalated

    def add_action(self, thought: str, action_name: str, action_input: Dict[str, Any], observation: Any) -> AgentAction:
        action = AgentAction(
            step_num=len(self.scratchpad) + 1,
            thought=thought,
            action_name=action_name,
            action_input=action_input,
            observation=observation
        )
        self.scratchpad.append(action)
        return action

    def get_context_summary(self) -> str:
        """Returns a formatted summary of observations made so far."""
        if not self.scratchpad:
            return "No tool observations recorded yet."
        lines = []
        for a in self.scratchpad:
            lines.append(f"Step {a.step_num} [{a.action_name}]: {a.thought}")
            lines.append(f"   -> Result: {a.observation}")
        return "\n".join(lines)
