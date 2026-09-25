# Techvruk Contest — Demo Video Recording Script & Guide
### Duration: 2 to 4 Minutes | Format: Screen Recording with Voiceover

This guide provides an exact, step-by-step recording plan for capturing the required 2–5 minute demonstration video of the **Autonomous Customer Support & Escalation Agent**.

---

## 🎬 Pre-Recording Checklist
1. Open terminal and run:
   ```bash
   streamlit run app.py
   ```
2. Maximize the browser window showing `http://localhost:8501`.
3. Open a second terminal window side-by-side (or ready to switch) with:
   ```bash
   python main.py --cli
   ```
4. Have your microphone ready.

---

## ⏱️ Video Timeline (Total: ~3 Minutes 30 Seconds)

### 0:00 – 0:35 | Introduction & Problem Overview
- **Visual:** Show Slide 1 or the top of the Streamlit dashboard.
- **Voiceover:**
  > *"Hello evaluators. Today I am demonstrating our AI Agentic System submitted for the Techvruk contest: an Autonomous Customer Support and Intelligent Escalation Agent.*
  > *Traditional chatbots rely on brittle one-shot prompt-response mechanisms that hallucinate policies and cannot take action. In contrast, our system follows an explicit ReAct workflow: it breaks down user goals into multi-step plans, executes 6 specialized tools against real knowledge bases and order databases, and activates an automatic Tier-2 human escalation protocol when customer distress or complex exceptions occur."*

### 0:35 – 1:15 | Architecture & ReAct Plan-Act-Observe Loop
- **Visual:** Show the sidebar and the "Agentic Telemetry" panel in Streamlit.
- **Voiceover:**
  > *"Here is our Streamlit interface. On the right, you can observe the agent's real-time internal telemetry: the decomposed action plan and the sequential ReAct scratchpad recording each Thought, Action, and Tool Observation.*
  > *Let's test our first scenario: an automated return request within our 30-day policy."*

### 1:15 – 2:00 | Scenario 1: Autonomous Policy Verification & Refund
- **Visual:** Click the 3rd scenario button in the sidebar: *"Autonomous Refund (30-Day Window)"* and click **Execute Agent**.
- **Point out:**
  1. **Thought 1:** Checking Knowledge Base for return guidelines (`KB-001`).
  2. **Thought 2:** Looking up order `ORD-89421` in customer database (Sarah Jenkins).
  3. **Thought 3:** Computing date delta (delivered Sept 16, 9 days ago, well within the 30-day window).
  4. **Thought 4:** Executing `process_refund`, issuing transaction reference `TXN-REF-...` and crediting the card.
- **Voiceover:**
  > *"Notice how the agent doesn't just reply with generic text. It searched our policy, pulled Sarah's order from the database, calculated that 9 days had elapsed, confirmed eligibility, executed an autonomous refund, and issued a formal banking transaction ID."*

### 2:00 – 2:45 | Scenario 2: High-Value Risk & Tier-2 Human Escalation
- **Visual:** Click the 5th scenario: *"Critical Escalation (Human Tier-2)"* and click **Execute Agent**.
- **Point out:**
  1. The red **⚠️ HUMAN ESCALATION PROTOCOL ACTIVATED** banner.
  2. The generated Ticket ID (`ESC-...`), Urgency (`CRITICAL`), Sentiment (`ANGRY`), and assigned SLA (<10 minutes).
- **Voiceover:**
  > *"Now consider a critical enterprise situation: a customer with a delayed high-value shipment ($649) expressing extreme distress and legal threats.*
  > *Instead of getting stuck in a loop, the agent detects the critical urgency and angry sentiment, activates our Tier-2 Human Escalation Protocol, files an urgent incident ticket with an SLA target of under 10 minutes, and packages the complete order and dialogue context for the human specialist."*

### 2:45 – 3:15 | Automated Testing & Zero-Key Offline Compliance
- **Visual:** Switch to terminal and run:
  ```bash
  python test_agent.py
  ```
- **Voiceover:**
  > *"Our system includes a comprehensive automated test suite with 100% passing tests covering policy lookup, order verification, date math, refund transactions, and escalation logic.*
  > *Furthermore, to adhere strictly to the contest guidelines regarding free-tier and open-source models, the agent features a dual-engine architecture: it works with the Gemini API, and also includes a zero-key offline simulator so any evaluator can run and grade the project out-of-the-box without configuring credentials."*

### 3:15 – 3:30 | Conclusion & Wrap-up
- **Visual:** Show the repository README.md and the 5-slide presentation (`Techvruk_Agentic_System_Presentation.pptx`).
- **Voiceover:**
  > *"In summary, this project delivers full source code, comprehensive documentation, an automated test suite, and a 5-slide presentation deck. Thank you for your evaluation."*

---

## 💡 Quick Tips for High Scores
- **Speak with clarity and steady pacing.**
- **Use mouse movements to highlight** the Thought → Action → Observation panels in Streamlit.
- **Keep the recording between 2:30 and 4:00 minutes** to fit perfectly in the 2–5 minute contest requirement.
