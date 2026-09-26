# ✦ Chatbot Techvruk: Project Presentation (5 Slides)

---

## Slide 1: Title & Overview
### **Chatbot Techvruk - Task Planner Agent**
#### *Autonomous Multi-Currency AI Agent for General Task Orchestration*

* **Presenter:** Anandha-raaman
* **Focus Area:** Autonomous Agentic Systems & Workflow Orchestration
* **Architecture:** ReAct Pattern (Plan → Act → Observe → Adjust → Respond)
* **Key Innovation:** General-purpose goal decomposition with arbitrary world-currency budgeting and financial feasibility verification.

---

## Slide 2: Problem Statement & Why Simple LLMs Fail
### **The Limitation of Single-Shot Prompting**
* **The Pitfall:** Conventional LLMs generate static, ungrounded checklists. They cannot:
  * Validate monetary feasibility across different international currencies.
  * Guarantee that line-item totals strictly sum to the user's budget ceiling.
  * Dynamically allocate contingency reserves (12–15%) against unexpected spikes.
  * Compute critical paths, active working hours, and sequential dependencies.
* **Our Solution:** A ReAct Agentic Workflow where the agent uses specialized computational tools to plan, calculate, observe constraints, and iterate until the plan is mathematically and logistically sound.

---

## Slide 3: System Architecture & The 5-Stage Agentic Loop
```
[User Prompt & Budget in Any Currency]
                 │
                 ▼
       ┌───────────────────┐
       │   1. PLAN PHASE   │ ➔ Goal Decomposition & Domain Classification
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │   2. ACT PHASE    │ ➔ Invocations of 6 Specialized Agentic Tools:
       │  (Tool Execution) │    • CurrencyConverter (35+ Currencies)
       │                   │    • KnowledgeRetriever (Domain Blueprints)
       │                   │    • BudgetCalculator (Phase Allocations & Buffer)
       │                   │    • ScheduleEstimator (Critical Path & Days)
       │                   │    • RiskEvaluator & ResourceFinder
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │ 3. OBSERVE PHASE  │ ➔ Constraint Satisfaction & Feasibility Scoring
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │ 4. ADJUST PHASE   │ ➔ Line-Item Balancing, Dependency Sequencing
       └─────────┬─────────┘
                 │
                 ▼
       ┌───────────────────┐
       │ 5. RESPOND PHASE  │ ➔ Structured Plan Streamed to Gemini UI via SSE
       └───────────────────┘
```

---

## Slide 4: Multi-Currency & Financial Engine
### **Any Currency, Zero Debt Risk**
* **35+ Global Currencies Supported:** USD ($), EUR (€), INR (₹), GBP (£), JPY (¥), CAD (C$), AUD (A$), AED, CHF, SGD, and more.
* **Strict 12% Contingency Reserve:** Every generated plan automatically safeguards 12% of total funds into an emergency buffer.
* **Dynamic Feasibility Index:** Computes a 0–100 score evaluating whether the user's target price is sufficient for realistic execution.
* **Line-Item Currency Normalization:** Every single subtask is given an individual duration and cost tag in the user's specified currency.

---

## Slide 5: Results, Impact & Gemini User Experience
### **Production-Grade Delivery**
* **Rich Gemini UI:**
  * Clean, dark/light theme with Gemini iridescent gradients.
  * Floating pill prompt composer with currency and budget selectors.
  * Real-time Agent Execution Trace displaying thoughts, tool calls, and observations.
  * Interactive task checklist with functional completion toggles.
  * Follow-up refinement chat for interactive plan adjustments.
* **Multiple Export Formats:** Instant download as Markdown (`.md`), structured JSON (`.json`), or printable PDF.
* **100% Autonomous:** Operates completely out of the box without paid API keys, with optional Gemini API integration.
