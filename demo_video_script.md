# Techvruk Contest — Task Planner Demo Video Recording Script
### Duration: 2 to 4 Minutes | Format: Screen Recording with Voiceover

This guide provides an exact, step-by-step recording plan for capturing the required 2–5 minute demonstration video of the **Autonomous Task Planner Agent**.

---

## 🎬 Pre-Recording Checklist
1. Open terminal and run:
   ```bash
   python main.py --web
   ```
2. Maximize the browser window showing `http://localhost:8501`.
3. Open a second terminal window side-by-side with:
   ```bash
   python main.py --cli
   ```
4. Have your microphone ready.

---

## ⏱️ Video Timeline (Total: ~3 Minutes 20 Seconds)

### 0:00 – 0:40 | Introduction & Contest Prompt Focus
- **Visual:** Show Slide 1 of the PowerPoint deck or top of the Streamlit dashboard.
- **Voiceover:**
  > *"Hello evaluators. Today I am demonstrating our AI Agentic System submitted for the Techvruk contest: an Autonomous Task Planner Agent.*
  > *This directly solves the contest challenge: 'Given a goal (such as planning a 3-day trip), break it into sub-tasks and generate a structured plan.'*
  > *While typical LLMs return vague unstructured paragraphs without verifying constraints, our agent implements a formal ReAct workflow: deconstructing goals, testing timeline feasibility, calculating critical path schedules, allocating budgets, and assigning operational risk mitigations."*

### 0:40 – 1:30 | Live Demonstration: Planning a 3-Day Trip to Tokyo
- **Visual:** On the Streamlit UI, select the 1st preset: *"🌸 3-Day Tokyo Trip ($1,200)"* and click **Generate Master Plan**.
- **Point out:**
  1. **Top Metric Ribbon:** Master Plan ID (`PLAN-...`), Timeline (3 Days), Total Budget ($1,200).
  2. **Decomposed Sub-Task Roadmap:**
     - Phase 1: Pre-Departure Logistics (transit passes, eSIM, central hotel booking).
     - Phase 2: Daily Itineraries (Day 1 arrival/orientation walk; Day 2 Asakusa & food tour; Day 3 Meiji Shrine & markets).
     - Phase 3: Departure Wrap-Up.
  3. **Critical Path & Milestones:** Highlighting `TASK-01 ➔ TASK-03 ➔ TASK-04 ➔ TASK-05`.
  4. **Budget Allocation Table:** Showing 35% lodging ($420), 25% transit ($300), 20% dining ($240), 12% activities ($144), 8% buffer ($96).
  5. **Risk Matrix:** Weather backup vouchers and landmark booking lead times.
- **Voiceover:**
  > *"Here is our primary benchmark. The agent parsed the user's intent, identified the 3-day constraint and $1,200 budget ceiling, and broke down the trip into chronological sub-tasks with deliverables. It calculated the critical sequential path, created a mathematical budget allocation, and injected weather contingency safeguards."*

### 1:30 – 2:15 | Inspecting the ReAct Thought-Action-Observation Telemetry
- **Visual:** Scroll down on the right column to show the **ReAct Scratchpad**.
- **Voiceover:**
  > *"On the right side of the screen, we can inspect the agent's internal telemetry. Notice the explicit ReAct cycle:*
  > *- In Step 1, it queries domain blueprints to establish milestone phases.*
  > *- In Step 2, it audits feasibility, returning a 90/100 feasibility score.*
  > *- In Step 3, it decomposes the goal into discrete subtasks.*
  > *- In Step 4, it computes the critical path schedule.*
  > *- And in Step 6, it persists the master plan object with a unique Plan ID into permanent records."*

### 2:15 – 2:50 | Testing Across Domains (Software MVP Launch or Hackathon)
- **Visual:** Click the 4th scenario: *"🚀 4-Week SaaS MVP Launch ($2,000)"* and click **Generate Master Plan**.
- **Voiceover:**
  > *"The agent's planning intelligence extends across domains. Here it deconstructs a software launch goal across 4 weeks: Phase 1 architecture and PRD, Phase 2 payment integration and testing, and Phase 3 deployment and beta telemetry, with technical risk mitigation strategies."*

### 2:50 – 3:20 | Automated Tests, Tech Stack & Free-Tier Compliance
- **Visual:** Switch to terminal and run:
  ```bash
  python test_agent.py
  ```
- **Voiceover:**
  > *"Our system includes an automated test suite with 6 passing unit tests validating blueprint retrieval, feasibility scoring, subtask decomposition, and schedule derivation.*
  > *In accordance with contest guidelines encouraging fairness and free-tier models, the agent runs seamlessly with Gemini API and includes an offline simulator engine that requires zero paid API keys.*
  > *Thank you for your evaluation."*

---

## 💡 Quick Tips for High Scores
- Keep your tone confident and enthusiastic.
- Use your cursor to highlight the **Sub-Task Matrix**, **Budget Allocation**, and **ReAct Telemetry**.
- Aim for a duration between 2:30 and 3:30 minutes.
