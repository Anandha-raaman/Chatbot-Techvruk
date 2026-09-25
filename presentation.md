# Techvruk AI Agentic System — Short Presentation (5 Slides)

> **File:** `Techvruk_Agentic_System_Presentation.pptx` (Widescreen 16:9)  
> **Contest Rule:** Max 5 slides (Bonus Points Deliverable)  
> **Candidate:** Anandha Raaman S  
> **Topic:** Autonomous Customer Support & Escalation Agent  

---

## 🎯 Slide 1: Title & Overview
- **Header:** TECHVRUK AI CONTEST SUBMISSION • AGENTIC SYSTEM
- **Title:** Autonomous Customer Support & Intelligent Escalation Agent
- **Subtitle:** Demonstrating the Complete ReAct Agentic Cycle: `Plan → Act → Observe → Respond` with Dynamic Multi-Tool Execution & Tier-2 Human Escalation Protocol
- **Presenter Info:** Anandha Raaman S | Generative AI Engineer
- **Stack:** Python 3.14, Pydantic 2.x, Google Gemini API / Offline Simulator Engine, Streamlit UI

> **Speaker Notes:**  
> *"Good day evaluators. Today I am presenting an autonomous AI Agentic System designed for enterprise customer support and incident escalation. Rather than building a conventional one-shot chatbot, this system implements a strict ReAct workflow that autonomously breaks down user goals, coordinates 6 specialized tools against live knowledge bases and customer databases, and applies deterministic escalation logic when edge cases or customer distress are detected."*

---

## 🔍 Slide 2: Context & Problem Statement
- **Header:** 01 / Context & Problem
- **Title:** Why Single-Call Chatbots Fail in Enterprise Support
- **Left Column (Traditional Chatbot Failures):**
  - **Brittle One-Shot Prompts:** Prone to hallucinating fake policies without checking source-of-truth records.
  - **Rigid Decision Trees:** Leave customers trapped in loops when queries have multiple nuances.
  - **No Autonomous Action:** Cannot query order databases, compute date deltas against return windows, or issue refunds.
  - **Blinded to Customer Distress:** Misses indicators of rage or legal exposure that require human intervention.
- **Right Column (Our Agentic Solution):**
  - **Decomposed Multi-Step Planning:** Dynamically partitions ambiguous tasks into an actionable sequence of subtasks.
  - **Grounded Tool Execution:** Invokes live Knowledge Base search, order lookup, and refund authorization.
  - **State & Context Memory:** Maintains continuous telemetry of thoughts, actions, and observations across steps.
  - **Safeguarded Human Escalation:** Automatically generates Tier-2 incident packets with urgency ratings and SLA targets.

> **Speaker Notes:**  
> *"Traditional chatbots either answer with ungrounded text or get stuck in rigid decision trees. Our agent bridges this gap: it behaves as an autonomous operator that reasons about what policy applies, inspects real customer purchase telemetry, calculates whether an item is within the 30-day window, and either resolves the issue autonomously or escalates with full context."*

---

## 🏗️ Slide 3: System Architecture & The ReAct Workflow
- **Header:** 02 / Architecture & Flow
- **Title:** System Architecture: Plan → Act → Observe → Respond
- **4-Stage Pipeline:**
  1. **PLAN (Task Decomposition):**  
     Extracts customer entities (Order ID, Email, Item SKU) and formulates an ordered multi-step action plan.
  2. **ACT (Tool Execution):**  
     Selects and calls specialized tools (`search_knowledge_base`, `lookup_customer_order`, `check_refund_eligibility`).
  3. **OBSERVE (Feedback Accumulation):**  
     Captures tool feedback into a typed Pydantic `AgentState` scratchpad memory.
  4. **RESPOND (Resolution / Escalation):**  
     Autonomously issues refunds with transaction IDs or activates the Tier-2 Human Escalation protocol.

> **Speaker Notes:**  
> *"Here is the architectural backbone. The user query enters the Planner, which decomposes the goal into discrete steps. The ReAct engine iteratively executes each step: forming a Thought, executing an Action, and logging the Observation into the scratchpad. This feedback loop dictates whether to execute the next tool or finalize resolution."*

---

## 🛠️ Slide 4: Autonomous Tool Suite & Escalation Safeguards
- **Header:** 03 / Capabilities & Safety
- **Title:** Autonomous Tool Suite & Multi-Tier Escalation Safeguards
- **Left Column (The 6 Autonomous Tools):**
  - `search_knowledge_base`: Keyword-weighted search across return, refund, and shipping policies.
  - `lookup_customer_order`: Retrieves real-time delivery telemetry, carrier tracking, and purchase records.
  - `check_refund_eligibility`: Computes date deltas between delivery and current date (30-day limit).
  - `process_refund`: Autonomous financial ledger crediting with transaction ID generation.
  - `escalate_to_human`: Formulates priority incident packets with SLA tracking (<15 mins).
  - `log_support_ticket`: Permanent JSON-based CRM interaction logging.
- **Right Column (Deterministic Escalation Triggers):**
  - **Sentiment & Rage Detection:** Bypasses automated loops when angry, abusive, or legal threats are detected.
  - **High-Value Exposure:** Orders over $500 with courier delays route straight to human supervisors.
  - **Policy Exceptions:** Valid extenuating claims (hospitalization, courier error) receive priority human review.
  - **Zero Context Loss:** Human agents receive the exact transcript, tool logs, and customer metadata.

> **Speaker Notes:**  
> *"Autonomous systems must know their limits. Our agent has six focused tools, but more importantly, it has clear escalation guardrails. If a customer is furious or an order over $500 is lost, the agent doesn't give a generic response; it constructs a formal Tier-2 incident ticket with an assigned SLA and hands over the complete telemetry."*

---

## 📊 Slide 5: Benchmarks, Test Coverage & Contest Compliance
- **Header:** 04 / Benchmarks & Compliance
- **Title:** Technology Stack, Test Coverage & Evaluation Summary
- **Verification Matrix:**
  - **100% Automated Test Suite:** 6 passing unit tests covering policy retrieval, order parsing, refund authorization, expired return denial, and human escalation.
  - **Dual-Engine Architecture:** Operates with live **Google Gemini API** (`gemini-1.5-flash`), and includes a built-in **Offline ReAct Engine** allowing evaluators to run the system with zero API keys.
  - **Contest Compliance:** 100% free-tier and open-source compliant; no paid or restricted APIs used.
  - **Dual Interfaces:** Interactive terminal CLI with colored trace panels + full Streamlit Web UI with live reasoning inspector and 1-click test scenarios.
  - **Persistent Audit Logging:** Every ticket, transaction, and observation is persisted to disk for compliance review.

> **Speaker Notes:**  
> *"To ensure maximum fairness and immediate grading by the Techvruk judges, the project features a dual-engine design: it supports Gemini API free tier while also running flawlessly in offline mode without requiring any credentials. With 100% automated test coverage and both CLI and Streamlit interfaces, it offers a robust, production-ready demonstration of agentic AI."*
