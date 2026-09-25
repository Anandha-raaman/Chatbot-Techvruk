"""
Pydantic State Context Models for Techvruk Task Planner Agent.
Maintains structured context across the Plan -> Act -> Observe -> Respond lifecycle.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SubTask(BaseModel):
    """Discrete, actionable sub-task within the structured plan."""
    task_id: str
    phase: str
    title: str
    estimated_duration: str
    priority: str = "Medium"  # High, Medium, Low
    dependencies: List[str] = Field(default_factory=list)
    deliverable: str = ""
    status: str = "pending"


class RiskItem(BaseModel):
    """Identified risk and mitigation safeguard."""
    risk: str
    severity: str  # Critical, High, Medium, Low
    mitigation_strategy: str


class BudgetAllocation(BaseModel):
    """Categorized financial or resource allocation."""
    category: str
    percentage: float
    estimated_amount: float
    notes: str = ""


class StructuredPlan(BaseModel):
    """Final, comprehensive structured plan object."""
    plan_id: str
    goal_title: str
    domain: str
    timeline_days: int
    total_budget: Optional[float] = None
    subtasks: List[SubTask] = Field(default_factory=list)
    critical_path: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    budget_breakdown: List[BudgetAllocation] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class AgentAction(BaseModel):
    """Telemetry record of a single ReAct tool execution."""
    step_num: int
    thought: str = Field(description="Agent's reasoning before calling tool")
    action_name: str = Field(description="Name of the invoked tool")
    action_input: Dict[str, Any] = Field(default_factory=dict)
    observation: Any = Field(default=None)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class AgentState(BaseModel):
    """Global execution state maintained across all workflow phases."""
    session_id: str
    user_goal: str
    parsed_constraints: Dict[str, Any] = Field(default_factory=dict)
    scratchpad: List[AgentAction] = Field(default_factory=list)
    structured_plan: Optional[StructuredPlan] = None
    final_response: Optional[str] = None
    status: str = "initialized"  # initialized, planning, executing, completed, failed

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
