"""
Autonomous Tool Registry for Customer Support & Escalation Agent.
All tools return structured, deterministic outputs for the ReAct loop.
"""

import json
import os
import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional

# Locate data directory relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KB_FILE = os.path.join(DATA_DIR, "knowledge_base.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.json")


def _load_json(file_path: str) -> Any:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(file_path: str, data: Any) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def search_knowledge_base(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Search company policy, warranty, returns, and escalation documents.
    Args:
        query: Keywords or question describing the policy needed.
        category: Optional category filter (returns, damages, shipping, cancellations, escalations).
    Returns:
        Dict with status, match_count, and ranked relevant articles.
    """
    articles = _load_json(KB_FILE)
    q_tokens = set(query.lower().split())

    scored_results = []
    for art in articles:
        if category and art.get("category", "").lower() != category.lower():
            continue

        score = 0
        title_lower = art.get("title", "").lower()
        content_lower = art.get("content", "").lower()
        keywords = [k.lower() for k in art.get("keywords", [])]

        # Calculate keyword relevance score
        for token in q_tokens:
            if token in title_lower:
                score += 3
            if token in content_lower:
                score += 1
            for kw in keywords:
                if token in kw:
                    score += 4

        if score > 0:
            scored_results.append((score, art))

    scored_results.sort(key=lambda x: x[0], reverse=True)

    if not scored_results:
        # Fallback to general returns policy if none matched
        return {
            "status": "partial_match",
            "matches_found": 0,
            "articles": [articles[0]] if articles else [],
            "message": "No direct keyword match; provided standard return & refund policy."
        }

    return {
        "status": "success",
        "matches_found": len(scored_results),
        "articles": [item[1] for item in scored_results[:3]]
    }


def lookup_customer_order(order_id: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """
    Look up customer account, purchase history, and shipping status.
    Args:
        order_id: Specific order identifier (e.g., ORD-89421).
        email: Customer's email address.
    Returns:
        Dict containing customer profile and matching order details.
    """
    customers = _load_json(CUSTOMERS_FILE)

    target_customer = None
    target_order = None

    for cust in customers:
        if email and cust.get("email", "").lower() == email.lower():
            target_customer = cust
            if order_id:
                for ord_entry in cust.get("orders", []):
                    if ord_entry.get("order_id", "").lower() == order_id.lower():
                        target_order = ord_entry
                        break
            else:
                target_order = cust.get("orders", [])[0] if cust.get("orders") else None
            break

        if order_id:
            for ord_entry in cust.get("orders", []):
                if ord_entry.get("order_id", "").lower() == order_id.lower():
                    target_customer = cust
                    target_order = ord_entry
                    break
        if target_order:
            break

    if not target_order:
        return {
            "status": "not_found",
            "message": f"No order found matching query (Order ID: {order_id}, Email: {email}).",
            "order": None
        }

    return {
        "status": "success",
        "customer": {
            "customer_id": target_customer["customer_id"],
            "name": target_customer["name"],
            "tier": target_customer.get("tier", "Standard"),
            "email": target_customer["email"]
        },
        "order": target_order
    }


def check_refund_eligibility(order_id: str, item_id: Optional[str] = None, reason: str = "Unspecified") -> Dict[str, Any]:
    """
    Evaluate company return policy against order delivery date and item condition.
    Args:
        order_id: The order ID to check.
        item_id: Specific item ID within the order (optional).
        reason: Stated reason for return/refund.
    Returns:
        Dict with eligibility boolean, days elapsed, policy applied, and reason.
    """
    lookup = lookup_customer_order(order_id=order_id)
    if lookup["status"] != "success":
        return {
            "eligible": False,
            "reason": f"Order {order_id} not found in database."
        }

    order = lookup["order"]
    delivery_date_str = order.get("delivery_date")
    status = order.get("status")

    if not delivery_date_str:
        if "delayed" in status.lower() or "transit" in status.lower():
            return {
                "eligible": True,
                "type": "carrier_delay_investigation",
                "days_since_delivery": None,
                "policy": "KB-004: Shipping Delays & Carrier Trace",
                "recommendation": "Package still in transit. Initiate carrier trace or offer priority reshipment."
            }
        return {
            "eligible": False,
            "reason": f"Order has not been delivered yet (Current Status: {status})."
        }

    delivery_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
    # Assume reference date is current contest window (Sept 2026)
    today = date(2026, 9, 25)
    days_elapsed = (today - delivery_date).days

    if days_elapsed <= 30:
        return {
            "eligible": True,
            "days_since_delivery": days_elapsed,
            "policy": "KB-001: Standard 30-Day Return Window",
            "refund_window_days": 30,
            "action": "Autonomous Refund Authorized",
            "message": f"Order delivered {days_elapsed} days ago (within 30-day window). Eligible for full refund or exchange."
        }
    else:
        return {
            "eligible": False,
            "days_since_delivery": days_elapsed,
            "policy": "KB-001: Standard 30-Day Return Window",
            "refund_window_days": 30,
            "action": "Policy Exception Required",
            "message": f"Order delivered {days_elapsed} days ago, exceeding the 30-day limit. Standard autonomous return is closed. Requires supervisor or human escalation if extenuating circumstances exist."
        }


def process_refund(order_id: str, item_id: Optional[str] = None, amount: Optional[float] = None, reason: str = "") -> Dict[str, Any]:
    """
    Execute autonomous refund against payment processor and update customer order record.
    Args:
        order_id: Order ID to refund.
        item_id: Item ID to refund.
        amount: Amount to refund (defaults to total order amount if omitted).
        reason: Justification recorded for accounting.
    Returns:
        Dict with transaction ID, refunded amount, and updated order status.
    """
    customers = _load_json(CUSTOMERS_FILE)
    refund_record = None

    for cust in customers:
        for ord_entry in cust.get("orders", []):
            if ord_entry.get("order_id", "").lower() == order_id.lower():
                refund_amount = amount if amount is not None else ord_entry.get("total_amount", 0.0)
                txn_id = f"TXN-REF-{uuid.uuid4().hex[:8].upper()}"

                ord_entry["refund_status"] = "Refunded"
                ord_entry["refund_txn_id"] = txn_id
                ord_entry["refund_amount"] = refund_amount
                ord_entry["refund_date"] = datetime.now().strftime("%Y-%m-%d")

                refund_record = {
                    "status": "success",
                    "transaction_id": txn_id,
                    "order_id": order_id,
                    "customer_name": cust["name"],
                    "refunded_amount": refund_amount,
                    "payment_method": ord_entry.get("payment_method"),
                    "reason": reason,
                    "estimated_arrival": "3-5 business days"
                }
                break
        if refund_record:
            break

    if refund_record:
        _save_json(CUSTOMERS_FILE, customers)
        return refund_record

    return {
        "status": "failed",
        "message": f"Could not process refund for order {order_id}. Order not found."
    }


def escalate_to_human(customer_name: str, email: str, issue_summary: str, urgency: str = "normal", sentiment: str = "neutral") -> Dict[str, Any]:
    """
    Trigger Tier-2 Human Support Escalation protocol.
    Creates an urgent incident packet for a human supervisor.
    Args:
        customer_name: Full name of customer.
        email: Contact email.
        issue_summary: Comprehensive synopsis of customer issue and agent actions taken.
        urgency: Level ('low', 'normal', 'high', 'critical').
        sentiment: Observed sentiment ('neutral', 'frustrated', 'distressed', 'angry').
    Returns:
        Dict containing escalation ticket reference, SLA target, and assigned team.
    """
    ticket_id = f"ESC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    sla_map = {
        "critical": 10,
        "high": 15,
        "normal": 60,
        "low": 120
    }
    sla_mins = sla_map.get(urgency.lower(), 30)

    escalation_payload = {
        "ticket_id": ticket_id,
        "type": "HUMAN_ESCALATION_TIER2",
        "customer_name": customer_name,
        "email": email,
        "urgency": urgency.upper(),
        "sentiment": sentiment.upper(),
        "summary": issue_summary,
        "assigned_queue": "Priority Incident Resolution Team",
        "sla_target_minutes": sla_mins,
        "created_at": datetime.now().isoformat(),
        "status": "Assigned to Human Specialist"
    }

    # Persist into tickets store
    tickets = _load_json(TICKETS_FILE)
    tickets.append(escalation_payload)
    _save_json(TICKETS_FILE, tickets)

    return {
        "status": "escalated",
        "ticket_id": ticket_id,
        "assigned_to": "Tier-2 Human Specialist",
        "urgency": urgency,
        "sla_minutes": sla_mins,
        "message": f"Incident successfully escalated to a Human Specialist under Ticket #{ticket_id}. Expected response within {sla_mins} minutes."
    }


def log_support_ticket(customer_name: str, email: str, category: str, description: str, resolution_status: str) -> Dict[str, Any]:
    """
    Log general support conversation into permanent CRM archive.
    """
    ticket_id = f"TCK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    ticket = {
        "ticket_id": ticket_id,
        "type": "STANDARD_SUPPORT_TICKET",
        "customer_name": customer_name,
        "email": email,
        "category": category,
        "description": description,
        "resolution_status": resolution_status,
        "created_at": datetime.now().isoformat()
    }
    tickets = _load_json(TICKETS_FILE)
    tickets.append(ticket)
    _save_json(TICKETS_FILE, tickets)

    return {
        "status": "logged",
        "ticket_id": ticket_id,
        "timestamp": ticket["created_at"]
    }


# Tool Definitions Metadata for LLM Tool Calling (Gemini Function Declarations)
TOOL_METADATA = [
    {
        "name": "search_knowledge_base",
        "description": "Searches the official corporate knowledge base for return, refund, shipping, warranty, and escalation policies.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query, topic, or policy keyword."},
                "category": {"type": "string", "description": "Optional category filter: returns, damages, shipping, cancellations, escalations."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "lookup_customer_order",
        "description": "Retrieves real-time order status, tracking info, delivery dates, and purchased items by Order ID or email.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID such as ORD-89421 or ORD-77312."},
                "email": {"type": "string", "description": "The customer's registered email address."}
            }
        }
    },
    {
        "name": "check_refund_eligibility",
        "description": "Evaluates return eligibility by checking delivery dates against the 30-day window policy and item conditions.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID to verify."},
                "item_id": {"type": "string", "description": "Specific item ID (optional)."},
                "reason": {"type": "string", "description": "Reason for return or refund request."}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "process_refund",
        "description": "Executes an approved refund transaction for an eligible order and updates order accounting status.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID to refund."},
                "item_id": {"type": "string", "description": "Optional specific item ID."},
                "amount": {"type": "number", "description": "Refund amount."},
                "reason": {"type": "string", "description": "Documented reason for the refund."}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Escalates complex, high-value, or distressed customer inquiries to a Tier-2 Human Support Specialist with priority SLA.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Name of customer."},
                "email": {"type": "string", "description": "Customer contact email."},
                "issue_summary": {"type": "string", "description": "Detailed synopsis of the issue and why human escalation is required."},
                "urgency": {"type": "string", "description": "Urgency level: low, normal, high, critical."},
                "sentiment": {"type": "string", "description": "Customer sentiment: neutral, frustrated, distressed, angry."}
            },
            "required": ["customer_name", "email", "issue_summary"]
        }
    },
    {
        "name": "log_support_ticket",
        "description": "Logs the completed customer interaction into CRM records with final resolution details.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Customer's name."},
                "email": {"type": "string", "description": "Customer's email address."},
                "category": {"type": "string", "description": "Ticket category (e.g., Refund, Inquiry, Shipping)."},
                "description": {"type": "string", "description": "Summary of the request."},
                "resolution_status": {"type": "string", "description": "Final resolution status."}
            },
            "required": ["customer_name", "email", "category", "description", "resolution_status"]
        }
    }
]
