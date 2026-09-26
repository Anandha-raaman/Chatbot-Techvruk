from __future__ import annotations
import os
import sys
import traceback
from typing import Optional, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

STATIC_DIR = os.path.join(BASE_DIR, "public") if os.path.exists(os.path.join(BASE_DIR, "public")) else os.path.join(BASE_DIR, "static")

import re
import json
import time
import uuid
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, Response, send_from_directory
from agent.dynamic_planner import DynamicTaskPlanner
from agent.tools import CurrencyConverter

app = Flask(__name__, static_folder=STATIC_DIR)
handler = app

# In-memory storage for active sessions & plans
active_sessions = {}

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/<path:path>", methods=["GET"])
def static_proxy(path):
    target = os.path.join(STATIC_DIR, path)
    if os.path.exists(target) and os.path.isfile(target):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/api/chat", methods=["POST", "OPTIONS"])
@app.route("/chat", methods=["POST", "OPTIONS"])
@app.route("/api/index", methods=["POST", "OPTIONS"])
@app.route("/api", methods=["POST", "OPTIONS"])
@app.route("/", methods=["POST", "OPTIONS"])
def chat():
    """
    Main conversational endpoint.
    Accepts natural language user input, automatically detects any task, budget,
    and currency in the background, and streams clean thinking and plan delivery.
    """
    if request.method == "OPTIONS":
        res = Response()
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return res, 204

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())[:8]
    api_key = data.get("api_key") or os.environ.get("GEMINI_API_KEY")

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    def event_stream():
        nonlocal api_key
        try:
            # Check if user passed/pasted a Gemini API Key in the prompt
            key_match = re.search(r"AIzaSy[A-Za-z0-9_-]{33}", message)
            if key_match:
                extracted_key = key_match.group(0)
                os.environ["GEMINI_API_KEY"] = extracted_key
                api_key = extracted_key
                try:
                    with open(".env", "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={extracted_key}\n")
                except Exception:
                    pass
                yield f"data: {json.dumps({'type': 'thought', 'content': '✦ Google Gemini API Key recognized and saved! Switching directly to gemini-2.5-flash...'})}\n\n"

            session = active_sessions.get(session_id)
            current_plan = session.get("current_plan") if session else None

            # Check if user is asking to switch or convert currency of the active plan
            requested_currency_change = _detect_currency_change_intent(message)

            if session and current_plan and requested_currency_change and not _is_explicit_new_goal(message):
                target_curr = CurrencyConverter.normalize_currency_code(requested_currency_change)
                old_curr = current_plan.get("currency", "USD")
                sym = CurrencyConverter.get_symbol(target_curr)

                yield f"data: {json.dumps({'type': 'thought', 'content': f'Recalculating plan budget and task cost allocations from {old_curr} to {target_curr} ({sym})...'})}\n\n"

                converted_plan = DynamicTaskPlanner.convert_plan_currency(current_plan, target_curr)
                converted_plan["session_id"] = session_id
                session["current_plan"] = converted_plan
                if "plans" in session and session["plans"]:
                    session["plans"][-1] = converted_plan
                session["history"].append({"user": message, "plan": converted_plan})

                fmt_total = CurrencyConverter.format(converted_plan.get('target_budget', 0), target_curr)
                fmt_alloc = CurrencyConverter.format(converted_plan.get('allocated_cost', 0), target_curr)
                fmt_res = CurrencyConverter.format(converted_plan.get('contingency_reserve', 0), target_curr)

                # Emit updated plan to UI
                yield f"data: {json.dumps({'type': 'plan', 'data': converted_plan, 'session_id': session_id})}\n\n"

                reply = (
                    f"✦ All budget estimates and task costs for **{converted_plan.get('title')}** have been converted to **{target_curr} ({sym})**.\n\n"
                    f"• **Target Budget:** {fmt_total} {target_curr}\n"
                    f"• **Planned Expenses:** {fmt_alloc} {target_curr}\n"
                    f"• **Emergency Buffer (12%):** {fmt_res} {target_curr}\n\n"
                    f"The plan card above has been updated with verified {target_curr} allocations."
                )
                yield f"data: {json.dumps({'type': 'followup', 'reply': reply, 'session_id': session_id})}\n\n"

            elif session and current_plan and not _is_new_plan_request(message):
                # Conversational follow-up
                plan = current_plan
                all_plans = session.get("plans", [plan])
                plan_title = plan.get("title", "")
                yield f"data: {json.dumps({'type': 'thought', 'content': f'Reviewing active plan \"{plan_title}\" to answer your question...'})}\n\n"
                reply = _generate_followup_reply(message, plan, all_plans, api_key)
                yield f"data: {json.dumps({'type': 'followup', 'reply': reply, 'session_id': session_id})}\n\n"
            else:
                # New plan generation
                extracted_budget, detected_curr = DynamicTaskPlanner.extract_budget_and_currency(message)
                sym = CurrencyConverter.get_symbol(detected_curr)

                yield f"data: {json.dumps({'type': 'thought', 'content': 'Deconstructing goal and identifying key objectives...'})}\n\n"
                yield f"data: {json.dumps({'type': 'thought', 'content': f'Auditing financial allocation in {detected_curr} ({sym}) with a 12% contingency buffer...'})}\n\n"
                yield f"data: {json.dumps({'type': 'thought', 'content': 'Structuring chronological phases, time horizons, and actionable subtasks...'})}\n\n"

                # Generate the rich contextual plan using real-world LLM
                plan = DynamicTaskPlanner.generate_plan(message, api_key=api_key)
                plan["session_id"] = session_id
                plan["original_query"] = message

                # Save session
                if session_id not in active_sessions:
                    active_sessions[session_id] = {"history": [], "current_plan": None, "plans": []}
                active_sessions[session_id]["current_plan"] = plan
                if "plans" not in active_sessions[session_id]:
                    active_sessions[session_id]["plans"] = []
                active_sessions[session_id]["plans"].append(plan)
                active_sessions[session_id]["history"].append({"user": message, "plan": plan})

                yield f"data: {json.dumps({'type': 'plan', 'data': plan, 'session_id': session_id})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Planning error: {str(e)}'})}\n\n"

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

def _detect_currency_change_intent(msg: str) -> Optional[str]:
    """
    Detects if the user wants to convert or view the current plan in a specific currency.
    Examples:
      - 'inr', 'indian rupees', 'rupees', 'change to inr', 'give in inr', 'i want in inr',
        'convert to inr', 'show in inr', 'money est in inr', 'must come in inr'
      - 'usd', 'dollars', 'change to usd', 'give in usd', 'i want in usd', 'convert to usd', 'show in usd'
    """
    if not msg:
        return None
    m = msg.strip().lower()

    # Direct short message
    if m in ["inr", "indian rupees", "indian rupee", "rupees", "rupee", "rs", "rs.", "₹"]:
        return "INR"
    if m in ["usd", "dollars", "dollar", "us dollars", "us dollar", "bucks", "$"]:
        return "USD"
    if m in ["eur", "euros", "euro", "€"]:
        return "EUR"
    if m in ["gbp", "pounds", "pound", "sterling", "£"]:
        return "GBP"
    if m in ["jpy", "yen", "¥"]:
        return "JPY"

    # Directional / intent patterns for INR
    inr_patterns = [
        r"\b(?:come\s+in|want\s+in|give\s+in|give\s+me\s+in|show\s+in|change\s+to|convert\s+to|switch\s+to|make\s+it|est\s+in|estimate\s+in|budget\s+in|cost\s+in|price\s+in|in|to|into|as)\s+(?:in\s+)?(?:indian\s+rupees?|inr|rupees?|rs\.?|₹)\b",
        r"\b(?:must\s+come\s+in|only\s+in|want\s+it\s+in)\s+(?:inr|indian\s+rupees?|rupees?)\b",
        r"\b(?:give|show|display|provide|format)\s+.*?(?:inr|indian\s+rupees?|rupees?)\b"
    ]
    for pat in inr_patterns:
        if re.search(pat, m):
            return "INR"

    # Directional / intent patterns for USD
    usd_patterns = [
        r"\b(?:come\s+in|want\s+in|give\s+in|give\s+me\s+in|show\s+in|change\s+to|convert\s+to|switch\s+to|make\s+it|est\s+in|estimate\s+in|budget\s+in|cost\s+in|price\s+in|in|to|into|as)\s+(?:in\s+)?(?:us\s+dollars?|usd|dollars?|bucks|\$)\b",
        r"\b(?:must\s+come\s+in|only\s+in|want\s+it\s+in)\s+(?:usd|dollars?|us\s+dollars?)\b",
        r"\b(?:give|show|display|provide|format)\s+.*?(?:usd|dollars?|us\s+dollars?)\b"
    ]
    for pat in usd_patterns:
        if re.search(pat, m):
            return "USD"

    # Other currencies
    other = re.search(r"\b(?:change\s+to|convert\s+to|switch\s+to|show\s+in|give\s+in|in|to)\s+(eur|euros?|gbp|pounds?|jpy|yen|cad|aud|aed|sgd|chf|cny)\b", m)
    if other:
        return CurrencyConverter.normalize_currency_code(other.group(1))

    return None

def _is_explicit_new_goal(msg: str) -> bool:
    """Checks whether the user explicitly asks to plan a new separate goal."""
    m = msg.lower().strip()
    return any(w in m for w in [
        "another plan", "new plan", "also plan", "second plan", "next plan", 
        "different plan", "plan a", "plan my", "plan for", "plan to", "give me a plan",
        "plan another", "one more plan", "make a plan"
    ])

def _is_new_plan_request(msg: str) -> bool:
    """Determines whether a message is requesting a new plan vs asking a conversational question or currency change."""
    m = msg.lower().strip()

    # If it's a currency change request on an existing plan, not a new plan
    if _detect_currency_change_intent(m) and not _is_explicit_new_goal(m):
        return False

    # Explicit indicators of a new plan
    if _is_explicit_new_goal(m):
        return True

    # Conversational questions
    question_starters = (
        "why ", "why?", "how come", "what does", "who will", "which ",
        "can you", "can we", "can i", "is it possible", "how much",
        "explain", "tell me", "what do you", "details of", "where can",
        "show me", "how to"
    )
    if m.startswith(question_starters):
        return False

    # Action + Subject for planning
    plan_action_words = ["plan", "build", "launch", "create", "organize", "prepare", "schedule"]
    has_action = any(w in m for w in plan_action_words)
    has_subject = any(w in m for w in ["trip", "tour", "travel", "vacation", "app", "software", "mvp", "bakery", "cafe", "business", "wedding", "conference", "party", "exam", "diet", "trek"])

    return has_action and has_subject

def _generate_followup_reply(query: str, plan: Dict[str, Any], all_plans: List[Dict[str, Any]], api_key: Optional[str]) -> str:
    """Generates intelligent conversational follow-ups using real-world LLM (Gemini or local models)."""
    curr = plan.get("currency", "USD")
    sym = CurrencyConverter.get_symbol(curr)

    # Multi-plan context overview
    plans_context = "\n".join([f"- Plan {i+1}: {p.get('title')} (Budget: {p.get('target_budget')} {p.get('currency')})" for i, p in enumerate(all_plans)])

    # 1. If Gemini API key is configured, use live LLM
    effective_key = api_key or os.environ.get("GEMINI_API_KEY")
    if effective_key:
        try:
            import google.genai as genai
            client = genai.Client(api_key=effective_key)
            prompt = f"""You are Chatbot Techvruk, an elite autonomous task planner assistant.
Plans in this chat:
{plans_context}

Active Plan Details:
Title: {plan.get('title')}
Summary: {plan.get('summary')}
Budget: {plan.get('target_budget')} {curr} ({sym})
Phases: {[p.get('phase_name') for p in plan.get('phases', [])]}

User Question: "{query}"

Answer concisely, helpfully, and practically. Important: The user's active plan is denominated in {curr} ({sym}). Ensure all financial references strictly use {curr}. Do not reveal code, schemas, or technical implementation details. Keep the tone warm, clear, and professional."""
            for g_model in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-flash-latest']:
                try:
                    resp = client.models.generate_content(
                        model=g_model,
                        contents=prompt
                    )
                    if resp and resp.text:
                        return resp.text.strip()
                except Exception:
                    continue
        except Exception as e:
            print(f"[Gemini Followup Notice] {e}")

    # 2. Use real-world local LLM (Qwen 2.5 7B or Gemma 3) via Ollama
    for model_name in ['qwen2.5:7b', 'gemma3:270m']:
        try:
            import ollama
            prompt = f"""You are Gemini Task Planner assistant powered by a real-world LLM.
Active Plan Context:
Title: {plan.get('title')}
Summary: {plan.get('summary')}
Budget: {plan.get('target_budget')} {curr}
Phases: {[p.get('phase_name') for p in plan.get('phases', [])]}

User Question: "{query}"

Answer helpfully, practically, and specifically in 2-3 concise paragraphs. Do not mention code or technical schemas."""
            resp = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.4})
            reply_text = resp['message']['content'].strip()
            if reply_text:
                return reply_text
        except Exception:
            continue

    # Fallback contextual reply
    q_lower = query.lower()
    if any(w in q_lower for w in ["reduce", "cut", "save", "lower", "cheap"]):
        reserve_str = CurrencyConverter.format(plan.get('contingency_reserve', 0), curr)
        return (
            f"Here is how you can optimize and reduce costs for your {plan.get('title')}:\n\n"
            f"1. **Leverage the Contingency Reserve:** You currently have {reserve_str} set aside as a buffer, which provides room for unexpected costs.\n"
            f"2. **Trim Optional Phase Items:** Shift non-essential activities in Phase 2/3 to self-guided or budget-friendly alternatives.\n"
            f"3. **Book in Advance:** Early booking typically yields 15-25% savings across transit, venue, or tool subscriptions."
        )
    elif any(w in q_lower for w in ["detail", "more", "explain", "how to"]):
        return (
            f"For your plan **{plan.get('title')}**, each task is organized in chronological order. "
            f"Start with **Phase 1: {plan.get('phases', [{}])[0].get('phase_name', '')}**. "
            f"Focus on completing the first subtask first, and use the interactive checkboxes in the plan to track your live progress."
        )
    elif any(w in q_lower for w in ["budget", "price", "cost", "money"]):
        total = CurrencyConverter.format(plan.get('target_budget', 0), curr)
        alloc = CurrencyConverter.format(plan.get('allocated_cost', 0), curr)
        res = CurrencyConverter.format(plan.get('contingency_reserve', 0), curr)
        return (
            f"**Budget Breakdown for {plan.get('title')}:**\n"
            f"• **Target Total:** {total} {curr}\n"
            f"• **Allocated Expenses:** {alloc} {curr}\n"
            f"• **Emergency Buffer (12%):** {res} {curr}\n\n"
            f"Every task has an individual cost attribution so you never exceed your ceiling."
        )
    else:
        return (
            f"Regarding your question about **{plan.get('title')}**: "
            f"The current roadmap spans {plan.get('duration_summary', 'the planned duration')} across {len(plan.get('phases', []))} structured phases. "
            f"Would you like me to adjust any specific phase, or would you like recommendations for specific resources?"
        )

@app.route("/api/export/<format_type>", methods=["POST"])
def export_plan(format_type: str):
    """Exports plan as Markdown or structured JSON."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    session = active_sessions.get(session_id)
    if not session or not session.get("current_plan"):
        return jsonify({"error": "Plan not found"}), 404

    plan = session["current_plan"]
    curr = plan.get("currency", "USD")

    if format_type.lower() == "json":
        return Response(
            json.dumps(plan, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=plan_{session_id}.json"}
        )

    # Markdown export
    lines = [
        f"# ✦ {plan.get('title', 'Task Plan')}",
        f"**Target Budget:** {CurrencyConverter.format(plan.get('target_budget', 0), curr)} | **Duration:** {plan.get('duration_summary', 'N/A')}",
        "",
        "## Overview",
        plan.get("summary", ""),
        "",
        "## Budget Breakdown",
        f"- **Total Budget:** {CurrencyConverter.format(plan.get('target_budget', 0), curr)}",
        f"- **Allocated Expenses:** {CurrencyConverter.format(plan.get('allocated_cost', 0), curr)}",
        f"- **Contingency Reserve (12%):** {CurrencyConverter.format(plan.get('contingency_reserve', 0), curr)}",
        "",
        "## Actionable Phases & Checklist",
        ""
    ]

    for p in plan.get("phases", []):
        lines.append(f"### {p.get('phase_name')} ({CurrencyConverter.format(p.get('phase_budget', 0), curr)})")
        lines.append(f"*{p.get('description', '')}*")
        lines.append("")
        for t in p.get("tasks", []):
            cost_str = CurrencyConverter.format(t.get('estimated_cost', 0), curr)
            lines.append(f"- [ ] **[{t.get('id')}] {t.get('title')}** — `{cost_str}` ({t.get('duration', 'N/A')})")
            lines.append(f"  {t.get('details', '')}")
        lines.append("")

    if plan.get("key_tips"):
        lines.append("## Practical Tips & Recommendations")
        for tip in plan.get("key_tips", []):
            lines.append(f"- {tip}")

    return Response(
        "\n".join(lines),
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment;filename=plan_{session_id}.md"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"* Gemini Task Planner Agent running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
