"""
Techvruk AI Agentic System Package.
"""
from .core import SupportAgent
from .state import AgentState, PlanStep, AgentAction, EscalationDetail
from .tools import (
    search_knowledge_base,
    lookup_customer_order,
    check_refund_eligibility,
    process_refund,
    escalate_to_human,
    log_support_ticket,
    TOOL_METADATA
)

__all__ = [
    "SupportAgent",
    "AgentState",
    "PlanStep",
    "AgentAction",
    "EscalationDetail",
    "search_knowledge_base",
    "lookup_customer_order",
    "check_refund_eligibility",
    "process_refund",
    "escalate_to_human",
    "log_support_ticket",
    "TOOL_METADATA"
]
