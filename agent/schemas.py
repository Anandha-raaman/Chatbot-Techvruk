"""
Pydantic data schemas for Task Planner Agent.
Covers inputs, task hierarchies, currency allocations, tools, and execution traces.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CurrencyInfo(BaseModel):
    code: str
    symbol: str
    name: str
    rate_to_usd: float

class TaskPlanRequest(BaseModel):
    goal: str = Field(..., description="The user's goal or task to be planned")
    budget: float = Field(0.0, description="User specified budget/price cap")
    currency: str = Field("USD", description="Currency chosen by user (e.g. USD, EUR, INR, GBP, JPY)")
    target_duration: Optional[str] = Field(None, description="Preferred duration or timeframe")
    depth: str = Field("balanced", description="balanced or deep")
    gemini_api_key: Optional[str] = Field(None, description="Optional Google Gemini API key")

class SubTask(BaseModel):
    id: str
    title: str
    description: str
    phase: str
    estimated_duration: str
    duration_hours: float = 0.0
    estimated_cost: float = 0.0
    currency: str = "USD"
    required_tools: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    priority: str = "Medium"
    completed: bool = False

class PhasePlan(BaseModel):
    phase_id: str
    phase_name: str
    description: str
    duration_days: int
    phase_budget: float
    currency: str
    subtasks: List[SubTask] = Field(default_factory=list)

class RiskItem(BaseModel):
    risk: str
    impact: str  # Low, Medium, High, Critical
    probability: str  # Low, Medium, High
    mitigation: str

class ResourceItem(BaseModel):
    category: str
    item: str
    estimated_cost: float
    currency: str
    essential: bool = True

class BudgetAnalysis(BaseModel):
    total_budget: float
    currency: str
    allocated_cost: float
    contingency_reserve: float
    remaining_buffer: float
    feasibility_score: int  # 0 to 100
    is_within_budget: bool
    currency_rate_to_usd: float
    breakdown_by_phase: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)

class AgenticStepLog(BaseModel):
    step_number: int
    step_type: str  # PLAN, ACT, OBSERVE, ADJUST, RESPOND
    title: str
    thought: str
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class PlanOutput(BaseModel):
    plan_id: str
    goal: str
    summary: str
    category: str
    currency: str
    target_budget: float
    estimated_total_cost: float
    contingency_reserve: float
    duration_summary: str
    feasibility_score: int
    phases: List[PhasePlan] = Field(default_factory=list)
    budget_analysis: BudgetAnalysis
    risks: List[RiskItem] = Field(default_factory=list)
    resources: List[ResourceItem] = Field(default_factory=list)
    execution_steps: List[AgenticStepLog] = Field(default_factory=list)
    created_at: str
