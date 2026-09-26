"""
Command Line Interface (CLI) for Task Planner Agent.
Allows interactive or argument-based planning in any currency.
"""

import argparse
import sys
from agent.schemas import TaskPlanRequest
from agent.planner_agent import TaskPlannerAgent
from agent.tools import CurrencyConverter

def main():
    parser = argparse.ArgumentParser(description="✦ Chatbot Techvruk - Task Planner Agent CLI")
    parser.add_argument("--goal", "-g", type=str, help="Task or goal to plan")
    parser.add_argument("--budget", "-b", type=float, default=0.0, help="Target budget / price")
    parser.add_argument("--currency", "-c", type=str, default="USD", help="Currency code (e.g. USD, EUR, INR, GBP, JPY)")
    parser.add_argument("--depth", "-d", type=str, default="balanced", choices=["balanced", "deep"], help="Planning depth")
    parser.add_argument("--api-key", "-k", type=str, default=None, help="Optional Gemini API key")

    args = parser.parse_args()

    goal = args.goal
    budget = args.budget
    currency = args.currency

    if not goal:
        print("=" * 65)
        print("* CHATBOT TECHVRUK - TASK PLANNER AGENT (AUTONOMOUS REACT SYSTEM) *")
        print("=" * 65)
        goal = input("Enter your goal or task to plan: ").strip()
        if not goal:
            print("Error: Goal cannot be empty.")
            sys.exit(1)

        curr_in = input("Enter currency (default USD, e.g., INR, EUR, JPY, GBP): ").strip().upper()
        if curr_in:
            currency = curr_in

        budget_in = input(f"Enter target price/budget in {currency} (or 0 for automatic estimate): ").strip()
        if budget_in:
            try:
                budget = float(budget_in.replace(",", ""))
            except ValueError:
                budget = 0.0

    print(f"\n[+] Initializing Agentic ReAct Workflow for: '{goal}'")
    print(f"[+] Target Price: {currency} {budget:,.2f} | Depth: {args.depth}\n")

    agent = TaskPlannerAgent(default_api_key=args.api_key)
    req = TaskPlanRequest(
        goal=goal,
        budget=budget,
        currency=currency,
        depth=args.depth
    )

    def cli_stream_cb(step):
        s_type = step["step_type"]
        s_num = step["step_number"]
        s_title = step["title"]
        print(f"[{s_type:7}] Step {s_num}: {s_title}")
        print(f"          Reasoning: {step['thought']}")
        if step.get("tool_name"):
            print(f"          [TOOL] {step['tool_name']}")
        print()

    plan = agent.run_agentic_workflow(req, stream_callback=cli_stream_cb)

    print("=" * 65)
    print("* PLAN SYNTHESIS COMPLETE *")
    print("=" * 65)
    print(f"Plan ID:            {plan.plan_id}")
    print(f"Domain Category:    {plan.category.upper()}")
    print(f"Target Budget:      {CurrencyConverter.format(plan.target_budget, plan.currency)}")
    print(f"Planned Cost:       {CurrencyConverter.format(plan.budget_analysis.allocated_cost, plan.currency)}")
    print(f"Contingency Buffer: {CurrencyConverter.format(plan.contingency_reserve, plan.currency)}")
    print(f"Feasibility Score:  {plan.feasibility_score} / 100")
    print(f"Timeline Horizon:   {plan.duration_summary}\n")

    print("PHASES & SUBTASKS:")
    print("-" * 65)
    for p in plan.phases:
        print(f"\n[PHASE] {p.phase_name} ({p.duration_days} days | Budget: {CurrencyConverter.format(p.phase_budget, plan.currency)})")
        print(f"  {p.description}")
        for st in p.subtasks:
            tools_str = ", ".join(st.required_tools) if st.required_tools else "Standard"
            print(f"   [ ] [{st.id}] {st.title}")
            print(f"       Cost: {CurrencyConverter.format(st.estimated_cost, plan.currency)} | Duration: {st.estimated_duration} | Priority: {st.priority}")
            print(f"       Tools: {tools_str}")

    print("\n" + "=" * 65)
    print("Run 'python app.py' to explore the full Gemini Web Interface at http://localhost:5000")
    print("=" * 65)

if __name__ == "__main__":
    main()
