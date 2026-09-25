"""
Core Agentic Workflow Engine for Techvruk AI Contest.
Implements the explicit ReAct pattern: Plan -> Act -> Observe -> Respond.
"""

import os
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

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


class SupportAgent:
    """
    Autonomous Customer Support & Escalation Agent.
    Deconstructs tasks into multi-step plans, invokes tools, maintains state,
    and handles dynamic escalation logic.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.has_llm = bool(self.api_key)

    def run(self, user_query: str, session_id: Optional[str] = None) -> AgentState:
        """
        Execute full agentic cycle: Plan -> Act -> Observe -> Respond.
        """
        session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        state = AgentState(
            session_id=session_id,
            user_query=user_query,
            status="planning"
        )

        # 1. PHASE 1: PLANNING
        plan = self._generate_plan(user_query)
        state.plan = plan
        state.status = "executing"

        # 2. PHASE 2: ACT & OBSERVE (The ReAct Loop)
        self._execute_react_loop(state)

        # 3. PHASE 3: FINAL RESPONSE GENERATION
        final_answer = self._generate_final_response(state)
        state.final_response = final_answer
        state.status = "escalated" if state.escalation.is_escalated else "completed"

        return state

    def _generate_plan(self, query: str) -> List[PlanStep]:
        """
        Decompose the user goal into a sequence of logical steps.
        """
        plan_steps = []
        lower_q = query.lower()

        # Step 1: Query & Entity Extraction
        plan_steps.append(PlanStep(
            step_id=1,
            description="Analyze user query, identify customer intent, and extract relevant entities (Order ID, Email, Item).",
            tool_hint="entity_parser"
        ))

        # Step 2: Policy & Knowledge Base Check
        plan_steps.append(PlanStep(
            step_id=2,
            description="Search official knowledge base to retrieve applicable policies, warranties, or refund windows.",
            tool_hint="search_knowledge_base"
        ))

        # Step 3: Order & Customer Profile Lookup
        if any(term in lower_q for term in ["ord-", "order", "bought", "purchased", "tracking", "refund", "return", "status", "cancel"]):
            plan_steps.append(PlanStep(
                step_id=3,
                description="Retrieve customer profile, order history, delivery verification, and tracking data.",
                tool_hint="lookup_customer_order"
            ))

        # Step 4: Eligibility & Rule Evaluation
        if any(term in lower_q for term in ["refund", "return", "money back", "replace", "damaged", "broken"]):
            plan_steps.append(PlanStep(
                step_id=4,
                description="Evaluate return eligibility against the 30-day delivery policy and item condition.",
                tool_hint="check_refund_eligibility"
            ))

        # Step 5: Execution or Escalation
        plan_steps.append(PlanStep(
            step_id=5,
            description="Execute authorized action (e.g. process refund, record carrier trace) or trigger Human Escalation if criteria met.",
            tool_hint="process_refund / escalate_to_human"
        ))

        # Step 6: CRM Logging & Resolution
        plan_steps.append(PlanStep(
            step_id=6,
            description="Persist transaction details into permanent CRM records and synthesize user response.",
            tool_hint="log_support_ticket"
        ))

        return plan_steps

    def _execute_react_loop(self, state: AgentState) -> None:
        """
        Executes the reasoning, tool calling, and observation accumulation loop.
        """
        query = state.user_query
        lower_q = query.lower()

        # Extract entities via regex
        order_match = re.search(r"ORD-\d+", query, re.IGNORECASE)
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", query)

        order_id = order_match.group(0).upper() if order_match else None
        email = email_match.group(0).lower() if email_match else None

        state.identified_order_id = order_id

        # Detect sentiment & urgency
        urgency = "normal"
        sentiment = "neutral"
        if any(w in lower_q for w in ["furious", "unacceptable", "lawyer", "scam", "sue", "legal", "terrible", "fraud"]):
            sentiment = "angry"
            urgency = "critical"
        elif any(w in lower_q for w in ["urgent", "asap", "emergency", "immediately", "frustrated", "delayed"]):
            sentiment = "frustrated"
            urgency = "high"

        # --- STEP 1: Search Knowledge Base ---
        step1 = next((s for s in state.plan if s.tool_hint == "search_knowledge_base"), None)
        if step1:
            step1.status = "in_progress"
            thought = "I need to check the company's knowledge base to understand the exact policy rules applicable to the user's issue."
            kb_res = search_knowledge_base(query=query)
            state.add_action(
                thought=thought,
                action_name="search_knowledge_base",
                action_input={"query": query},
                observation=kb_res
            )
            step1.status = "completed"

        # --- STEP 2: Lookup Customer Order (if relevant) ---
        step2 = next((s for s in state.plan if s.tool_hint == "lookup_customer_order"), None)
        order_data = None
        customer_data = None

        if step2:
            step2.status = "in_progress"
            thought = f"Looking up customer order details for Order ID '{order_id}' or Email '{email}' to verify purchase date and delivery status."
            order_res = lookup_customer_order(order_id=order_id, email=email)
            state.add_action(
                thought=thought,
                action_name="lookup_customer_order",
                action_input={"order_id": order_id, "email": email},
                observation=order_res
            )
            if order_res.get("status") == "success":
                order_data = order_res.get("order")
                customer_data = order_res.get("customer")
                state.identified_customer_id = customer_data.get("customer_id")
            step2.status = "completed"

        # --- STEP 3: Policy Eligibility Check ---
        step3 = next((s for s in state.plan if s.tool_hint == "check_refund_eligibility"), None)
        eligibility_data = None

        if step3:
            step3.status = "in_progress"
            if order_data:
                target_order_id = order_data.get("order_id")
                thought = f"Evaluating return/refund eligibility for {target_order_id} based on delivery date {order_data.get('delivery_date')} against the 30-day window policy."
                eligibility_data = check_refund_eligibility(order_id=target_order_id, reason=query)
                state.add_action(
                    thought=thought,
                    action_name="check_refund_eligibility",
                    action_input={"order_id": target_order_id, "reason": query},
                    observation=eligibility_data
                )
                step3.status = "completed"
            else:
                thought = "Cannot verify refund eligibility because no specific order ID was provided or located."
                state.add_action(
                    thought=thought,
                    action_name="check_refund_eligibility",
                    action_input={"query": query},
                    observation={"eligible": False, "reason": "Order lookup required first."}
                )
                step3.status = "failed"

        # --- STEP 4: Action Execution OR Human Escalation ---
        step4 = next((s for s in state.plan if "escalate_to_human" in s.tool_hint or "process_refund" in s.tool_hint), None)
        if step4:
            step4.status = "in_progress"

            # Check if escalation conditions are triggered:
            # 1. Customer is distressed/angry or mentions legal/fraud
            # 2. High value order (> $500) with carrier delays
            # 3. Policy denied refund but extenuating circumstances claimed
            # 4. Explicit request for human/manager
            needs_escalation = (
                sentiment in ["angry", "frustrated"] or
                urgency in ["critical", "high"] or
                any(t in lower_q for t in ["talk to human", "real person", "escalate", "manager", "supervisor"]) or
                (order_data and order_data.get("total_amount", 0) > 500 and "delayed" in str(order_data.get("status")).lower()) or
                (eligibility_data and not eligibility_data.get("eligible") and any(w in lower_q for w in ["hospital", "emergency", "stolen", "unfair"]))
            )

            if needs_escalation:
                cust_name = customer_data.get("name") if customer_data else (email or "Valued Customer")
                cust_email = customer_data.get("email") if customer_data else (email or "customer@example.com")
                thought = f"Escalation trigger activated: Customer exhibits {sentiment} sentiment with {urgency} urgency. Routing to Tier-2 Human Specialist per Protocol KB-006."

                summary_text = (
                    f"Customer: {cust_name} ({cust_email})\n"
                    f"Order: {order_id or 'N/A'}\n"
                    f"User Query: {query}\n"
                    f"Findings: Order Status={order_data.get('status') if order_data else 'Unknown'}. "
                    f"Eligibility={eligibility_data.get('message') if eligibility_data else 'N/A'}."
                )

                esc_res = escalate_to_human(
                    customer_name=cust_name,
                    email=cust_email,
                    issue_summary=summary_text,
                    urgency=urgency,
                    sentiment=sentiment
                )

                state.add_action(
                    thought=thought,
                    action_name="escalate_to_human",
                    action_input={"customer_name": cust_name, "email": cust_email, "urgency": urgency, "sentiment": sentiment},
                    observation=esc_res
                )

                state.escalation = EscalationDetail(
                    is_escalated=True,
                    urgency=urgency,
                    sentiment=sentiment,
                    escalation_reason=f"Triggered by sentiment '{sentiment}' or complex policy exception.",
                    ticket_id=esc_res.get("ticket_id"),
                    sla_minutes=esc_res.get("sla_minutes", 15)
                )

            elif eligibility_data and eligibility_data.get("eligible") and any(w in lower_q for w in ["refund", "money back", "cancel"]):
                # Autonomous refund execution
                target_order_id = order_data["order_id"]
                refund_amount = order_data.get("total_amount")
                thought = f"Order {target_order_id} is verified as delivered within 30 days. Policy KB-001 authorizes autonomous refund of ${refund_amount}."

                refund_res = process_refund(
                    order_id=target_order_id,
                    amount=refund_amount,
                    reason=f"Customer request: {query[:50]}"
                )

                state.add_action(
                    thought=thought,
                    action_name="process_refund",
                    action_input={"order_id": target_order_id, "amount": refund_amount},
                    observation=refund_res
                )

            step4.status = "completed"

        # --- STEP 5: Log Permanent CRM Record ---
        step5 = next((s for s in state.plan if s.tool_hint == "log_support_ticket"), None)
        if step5:
            step5.status = "in_progress"
            thought = "Recording interaction and outcome into persistent CRM ticketing system."
            cust_name = customer_data.get("name") if customer_data else "Guest Customer"
            cust_email = customer_data.get("email") if customer_data else (email or "guest@example.com")
            cat = "Refund" if "refund" in lower_q else ("Escalation" if state.escalation.is_escalated else "Inquiry")

            ticket_res = log_support_ticket(
                customer_name=cust_name,
                email=cust_email,
                category=cat,
                description=query[:150],
                resolution_status="Escalated to Human" if state.escalation.is_escalated else "Resolved Autonomously"
            )

            state.add_action(
                thought=thought,
                action_name="log_support_ticket",
                action_input={"customer_name": cust_name, "category": cat},
                observation=ticket_res
            )
            step5.status = "completed"

    def _generate_final_response(self, state: AgentState) -> str:
        """
        Synthesize tool observations into a coherent, professional response.
        """
        # Collect actions
        actions = {a.action_name: a.observation for a in state.scratchpad}

        # Scenario 1: Escalated to Human Agent
        if state.escalation.is_escalated:
            esc = state.escalation
            esc_obs = actions.get("escalate_to_human", {})
            order_obs = actions.get("lookup_customer_order", {}).get("order", {})

            return (
                f"### 🛡️ Priority Support Escalation Notice\n\n"
                f"Dear Customer,\n\n"
                f"I have reviewed your inquiry regarding "
                f"{('Order **' + str(order_obs.get('order_id')) + '**') if order_obs else 'your account'}. "
                f"Because your situation requires specialized attention, I have formally escalated your case directly to our **{esc.assigned_tier}**.\n\n"
                f"**Escalation Summary:**\n"
                f"- **Incident Ticket ID:** `{esc.ticket_id}`\n"
                f"- **Priority Level:** `{esc.urgency.upper()}`\n"
                f"- **Target Response SLA:** Under **{esc.sla_minutes} minutes**\n"
                f"- **Assigned Team:** Priority Incident Resolution Team\n\n"
                f"A Senior Support Specialist is already reviewing the full dialogue transcript and order telemetry. You will receive an immediate update at your registered contact address."
            )

        # Scenario 2: Autonomous Refund Processed
        if "process_refund" in actions and actions["process_refund"].get("status") == "success":
            ref = actions["process_refund"]
            return (
                f"### ✅ Refund Successfully Processed\n\n"
                f"Good news! We have processed your refund request autonomously in accordance with our **30-Day Return & Refund Policy (KB-001)**.\n\n"
                f"**Transaction Breakdown:**\n"
                f"- **Order ID:** `{ref.get('order_id')}`\n"
                f"- **Refund Amount:** **${ref.get('refunded_amount', 0.0):.2f}**\n"
                f"- **Payment Method Credited:** {ref.get('payment_method')}\n"
                f"- **Transaction Reference:** `{ref.get('transaction_id')}`\n"
                f"- **Estimated Credit Time:** {ref.get('estimated_arrival', '3-5 business days')}\n\n"
                f"You will receive a confirmation email shortly with full banking details."
            )

        # Scenario 3: Order Status / Shipping Inquiry
        if "lookup_customer_order" in actions and actions["lookup_customer_order"].get("status") == "success":
            ord_data = actions["lookup_customer_order"]["order"]
            items_str = ", ".join([f"{i['name']} (x{i['quantity']})" for i in ord_data.get("items", [])])
            return (
                f"### 📦 Order & Shipping Details\n\n"
                f"Here is the real-time telemetry for **Order `{ord_data.get('order_id')}`**:\n\n"
                f"- **Current Status:** `{ord_data.get('status')}`\n"
                f"- **Carrier:** {ord_data.get('carrier')} (Tracking: `{ord_data.get('tracking_number')}`)\n"
                f"- **Order Date:** {ord_data.get('order_date')}\n"
                f"- **Delivery Date:** {ord_data.get('delivery_date') or 'Pending Delivery'}\n"
                f"- **Items:** {items_str}\n"
                f"- **Total Amount:** ${ord_data.get('total_amount'):.2f}\n\n"
                f"Please let me know if you would like to initiate an exchange, return, or request further delivery assistance."
            )

        # Scenario 4: General Knowledge Base Response
        if "search_knowledge_base" in actions and actions["search_knowledge_base"].get("articles"):
            articles = actions["search_knowledge_base"]["articles"]
            primary_art = articles[0]
            return (
                f"### 📋 {primary_art.get('title')}\n\n"
                f"{primary_art.get('content')}\n\n"
                f"*(Policy Reference: `{primary_art.get('id')}`)*\n\n"
                f"If you have a specific order number (e.g., `ORD-89421`), please provide it so I can verify your account telemetry directly."
            )

        return (
            "I have logged your inquiry into our support system. Please provide an Order ID (e.g. `ORD-89421`) "
            "or contact email so I can assist you with real-time order and policy actions."
        )
