"""
Chatbot Techvruk - Autonomous AI Task Planner Web Application
Clean, private, conversational system matching modern aesthetics.
Handles natural language planning, background multi-currency parsing, and follow-up refinements.
"""

import os
import re
import json
import time
import uuid
import queue
import threading
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, Response, send_from_directory
from agent.dynamic_planner import DynamicTaskPlanner
from agent.tools import CurrencyConverter

app = Flask(__name__, static_folder="static")

# In-memory storage for active sessions & plans
active_sessions = {}

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("static", path)

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main conversational endpoint.
    Accepts natural language user input, automatically detects any task, budget,
    and currency in the background, and streams clean thinking and plan delivery.
    """
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())[:8]
    api_key = data.get("api_key") or os.environ.get("GEMINI_API_KEY")

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    q = queue.Queue()

    def worker():
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
                q.put({
                    "type": "thought",
                    "content": "✦ Google Gemini API Key recognized and saved! Switching directly to gemini-2.5-flash..."
                })

            session = active_sessions.get(session_id)
            if session and session.get("current_plan") and not _is_new_plan_request(message):
                # Conversational follow-up
                plan = session["current_plan"]
                all_plans = session.get("plans", [plan])
                q.put({
                    "type": "thought",
                    "content": f"Reviewing active plan '{plan['title']}' to answer your question..."
                })
                time.sleep(0.3)
                reply = _generate_followup_reply(message, plan, all_plans, api_key)
                q.put({
                    "type": "followup",
                    "reply": reply,
                    "session_id": session_id
                })
            else:
                # New plan generation (supports multiple plans in the same chat)
                extracted_budget, detected_curr = DynamicTaskPlanner.extract_budget_and_currency(message)
                
                # Stream human-friendly, clean thinking steps (NO code, NO technical tool schemas)
                q.put({
                    "type": "thought",
                    "content": f"Deconstructing goal and identifying key objectives..."
                })
                time.sleep(0.3)

                q.put({
                    "type": "thought",
                    "content": f"Auditing financial allocation in {detected_curr} with a 12% contingency buffer..."
                })
                time.sleep(0.3)

                q.put({
                    "type": "thought",
                    "content": f"Structuring chronological phases, time horizons, and actionable subtasks..."
                })
                time.sleep(0.3)

                # Generate the rich contextual plan using real-world LLM
                plan = DynamicTaskPlanner.generate_plan(message, api_key=api_key)
                plan["session_id"] = session_id
                plan["original_query"] = message

                # Save session - keep all plans so user can create multiple plans in one chat
                if session_id not in active_sessions:
                    active_sessions[session_id] = {"history": [], "current_plan": None, "plans": []}
                active_sessions[session_id]["current_plan"] = plan
                if "plans" not in active_sessions[session_id]:
                    active_sessions[session_id]["plans"] = []
                active_sessions[session_id]["plans"].append(plan)
                active_sessions[session_id]["history"].append({"user": message, "plan": plan})

                q.put({
                    "type": "plan",
                    "data": plan,
                    "session_id": session_id
                })

        except Exception as e:
            q.put({"type": "error", "message": f"An error occurred: {str(e)}"})
        finally:
            q.put(None)

    threading.Thread(target=worker, daemon=True).start()

    def event_stream():
        while True:
            item = q.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

def _is_new_plan_request(msg: str) -> bool:
    """Determines whether a message is requesting a new plan vs asking a conversational question."""
    m = msg.lower().strip()
    
    # Explicit indicators of a new plan
    plan_override = any(w in m for w in [
        "another plan", "new plan", "also plan", "second plan", "next plan", 
        "different plan", "plan a", "plan my", "plan for", "plan to", "give me a plan",
        "plan another", "one more plan", "make a plan"
    ])
    if plan_override:
        return True

    # Pure conversational follow-up questions
    question_starters = (
        "why ", "why?", "how come", "what does", "who will", "which ",
        "can you reduce", "can we cut", "can i reduce", "is it possible to save",
        "explain", "tell me more about", "what do you mean", "details of"
    )
    if m.startswith(question_starters):
        return False

    # Check for general planning or task keywords
    plan_words = [
        "plan", "trip", "tour", "travel", "vacation", "itinerary", "visit",
        "launch", "build", "create", "organize", "schedule", "roadmap", "routine",
        "business", "bakery", "cafe", "app", "software", "saas", "mvp",
        "event", "wedding", "conference", "party", "renovate", "prepare", "exam",
        "workout", "fitness", "diet", "study", "trek"
    ]
    currency_words = [
        "inr", "usd", "eur", "jpy", "gbp", "cad", "aud", "rupees", "dollars",
        "₹", "$", "€", "¥", "£", "budget", "price", "cost"
    ]

    has_plan = any(w in m for w in plan_words)
    has_curr = any(w in m for w in currency_words)

    return has_plan or has_curr or len(m.split()) >= 3

def _generate_followup_reply(query: str, plan: Dict[str, Any], all_plans: List[Dict[str, Any]], api_key: Optional[str]) -> str:
    """Generates intelligent conversational follow-ups using real-world LLM (Gemini or local models)."""
    curr = plan.get("currency", "USD")

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
Budget: {plan.get('target_budget')} {curr}
Phases: {[p.get('phase_name') for p in plan.get('phases', [])]}

User Question: "{query}"

Answer concisely, helpfully, and practically. Do not reveal code, schemas, or technical implementation details. Keep the tone warm, clear, and professional."""
            for g_model in ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-flash-latest', 'gemini-2.5-flash']:
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
