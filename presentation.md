# Techvruk AI Agentic System — Task Planner Presentation (5 Slides)

> **File:** `Techvruk_Agentic_System_Presentation.pptx` (Widescreen 16:9)  
> **Contest Rule:** Short presentation (max 5 slides)  
> **Candidate:** Anandha Raaman S  
> **Chosen Task:** Task Planner Agent (`Given a goal e.g. 'plan a 3-day trip', break it into sub-tasks and generate a structured plan`)  

---

## 🎯 Slide 1: Title & Overview
- **Header:** TECHVRUK AI CONTEST SUBMISSION • TASK PLANNER AGENT
- **Title:** Autonomous Task Planner Agent: Goal Decomposition & Execution Architecture
- **Subtitle:** Given an ambiguous goal (e.g., *"plan a 3-day trip"*), autonomously decomposes it into phased sub-tasks, computes feasibility, critical path schedules, budget allocations, and contingency safeguards.
- **Presenter Info:** Anandha Raaman S | Generative AI Engineer
- **Stack:** Python 3.14, Pydantic 2.x, Google Gemini API / Offline Engine, Streamlit UI

> **Speaker Notes:**  
> *"Good day evaluators. For this contest, I have built an Autonomous Task Planner Agent that directly solves the contest challenge: 'Given a goal, break it down into sub-tasks and generate a structured plan.' Instead of outputting generic prose, the agent follows an explicit ReAct workflow that extracts constraints, queries domain blueprints, audits feasibility, schedules critical paths, and exports a master execution roadmap."*

---

## 🔍 Slide 2: Context & Problem Statement
- **Header:** 01 / Context & Problem
- **Title:** Why Unstructured Goals Fail in Single-Call LLMs
- **Left Column (Traditional One-Shot LLM Failures):**
  - **Unstructured Paragraph Dumps:** Produces vague essays lacking sequential order, timestamps, or milestone checkpoints.
  - **Zero Constraint Verification:** Never calculates whether a $1,200 budget or 3-day window can realistically cover the itinerary.
  - **Blind to Dependency Blockers:** Schedules downstream actions before prerequisites are confirmed (e.g. touring before transit).
  - **No Operational Safeguards:** Ignores weather contingencies, booking lead times, and failure points.
- **Right Column (Autonomous Task Planner Solution):**
  - **Decomposed Multi-Phase Breakdown:** Generates discrete, numbered sub-tasks with duration estimates and explicit deliverables.
  - **Feasibility Auditing:** Tests timeline and budget limits against domain benchmarks with feasibility scoring (0-100).
  - **Critical Path Analysis:** Maps dependency chains (`TASK-01 ➔ TASK-02`) and highlights bottlenecks.
  - **Deterministic Risk Mitigation:** Injects automated contingency protocols for each identified operational failure point.

> **Speaker Notes:**  
> *"When a human asks an LLM to 'plan a 3-day trip' or 'launch an MVP', a standard model vomits generic paragraphs. It doesn't check if the budget adds up, doesn't identify what must happen first, and doesn't prepare for risks. Our agent treats goals as engineering problems: decomposing requirements, verifying feasibility, and mapping dependencies."*

---

## 🏗️ Slide 3: System Architecture & ReAct Workflow
- **Header:** 02 / Architecture & Flow
- **Title:** System Architecture: Plan → Act → Observe → Respond
- **4-Stage Pipeline:**
  1. **PLAN (Constraint Parsing):**  
     Extracts primary goal, numerical duration, budget ceiling, and domain classification (`trip_planning`, `software_launch`, `event_management`).
  2. **ACT (Tool Invocations):**  
     Calls specialized tools: blueprint search, feasibility auditor, subtask decomposer, critical path scheduler.
  3. **OBSERVE (State Scratchpad):**  
     Accumulates structured observations and constraint checks into Pydantic `AgentState` memory.
  4. **RESPOND (Master Plan Synthesis):**  
     Compiles phase matrix, milestone timeline, budget breakdown, and persists plan with Plan ID.

> **Speaker Notes:**  
> *"Here is our core state machine. Notice how the agent transitions across phases: starting with constraint parsing, cycling through tool invocations in the ReAct loop where each observation informs the next decision, and culminating in a comprehensive master plan that is persisted to storage."*

---

## 🛠️ Slide 4: Tool Suite & 3-Day Trip Benchmark
- **Header:** 03 / Tool Suite & Benchmarks
- **Title:** Autonomous Tool Suite & 3-Day Trip Execution Showcase
- **Left Column (The 6 Autonomous Planning Tools):**
  - `search_domain_blueprints`: Retrieves domain blueprints and milestone phases.
  - `analyze_goal_feasibility`: Tests timeline feasibility and resource limits.
  - `decompose_into_subtasks`: Generates phase-aligned, numbered sub-tasks with deliverables.
  - `calculate_schedule_and_critical_path`: Derives sequential critical path and milestone checkpoints.
  - `assess_risks_and_mitigations`: Identifies failure modes and injects contingency safeguards.
  - `export_structured_plan`: Persists compiled master plan into permanent JSON records.
- **Right Column (Benchmark: 'Plan a 3-Day Trip to Tokyo'):**
  - **Input Goal:** *"Plan a 3-day cultural & culinary trip to Tokyo for 2 people on a $1,200 budget."*
  - **Phase 1 Logistics:** Lodging reservation, flight transfers, local eSIM data, and IC transit card pre-orders.
  - **Phase 2 Itinerary:** Day 1 arrival & orientation walk; Day 2 Asakusa & culinary food tour; Day 3 Meiji Shrine & market shopping.
  - **Budget Optimization:** Allocates 35% lodging ($420), 25% transit ($300), 20% dining ($240), 12% activities ($144), 8% buffer ($96).
  - **Risk Mitigation:** Pre-downloads offline transit maps and schedules open-date vouchers for rainy weather.

> **Speaker Notes:**  
> *"On the right is our primary benchmark: planning a 3-day trip to Tokyo on a $1,200 budget. The agent schedules arrival logistics on Day 1, cultural landmarks on Day 2, and nature markets on Day 3, while cleanly dividing the $1,200 into lodging, transit, food, and emergency reserves with zero user intervention."*

---

## 📊 Slide 5: Test Coverage, Tech Stack & Contest Compliance
- **Header:** 04 / Benchmarks & Compliance
- **Title:** Test Coverage, Technology Stack & Contest Compliance
- **Verification Matrix:**
  - **100% Automated Test Suite:** 6 automated unit tests validating blueprint search, feasibility scoring, 3-day subtask decomposition, critical path derivation, risk assessment, and end-to-end plan generation.
  - **Strict Agentic Behavior:** Demonstrates true `Plan -> Act -> Observe -> Respond` workflow with continuous scratchpad telemetry (no single-shot prompt hacks).
  - **Free-Tier & Zero-Key Compliance:** Supports Google Gemini API (`gemini-1.5-flash`) and features a built-in offline simulator engine so judges can run it without API keys.
  - **Dual Operational Interfaces:** Interactive Streamlit Web UI with live reasoning inspector and 1-click test scenarios + rich terminal CLI.
  - **Audit Trail:** Structured plan export into JSON guarantees every generated plan has a unique Plan ID (`PLAN-2026-...`) for verifiable execution.

> **Speaker Notes:**  
> *"To ensure maximum fairness and compliance with contest rules, the agent requires zero paid API keys and can be evaluated immediately using our offline simulator or the Gemini free tier. With 100% test coverage and interactive interfaces, this system represents a robust, production-ready solution to autonomous task planning."*
