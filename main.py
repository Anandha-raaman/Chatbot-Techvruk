"""
Main Entry Point for Techvruk Task Planner Agent.
Usage:
    python main.py             # Run automated demo benchmark scenarios
    python main.py --cli       # Start interactive CLI mode
    python main.py --web       # Launch Streamlit web dashboard
    python main.py --test      # Execute test suite
"""

import sys
import os
import subprocess

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import TaskPlannerAgent
from cli import display_agent_run, print_banner


def run_demo():
    """Run benchmark demonstration scenarios highlighting autonomous task breakdown."""
    print_banner()
    agent = TaskPlannerAgent()

    scenarios = [
        (
            "Benchmark 1: 3-Day Cultural & Culinary Trip to Tokyo (Contest Prompt Example)",
            "Plan a 3-day trip to Tokyo for 2 people with cultural heritage landmarks and food markets on a $1,200 budget"
        ),
        (
            "Benchmark 2: 4-Day Weekend Getaway to Paris",
            "Plan a 4-day weekend trip to Paris with museum visits, art galleries, and scenic dining on an $1,800 budget"
        ),
        (
            "Benchmark 3: SaaS AI MVP Product Launch in 4 Weeks",
            "Build and launch a SaaS AI MVP in 4 weeks with user authentication and payment billing on a $2,000 budget"
        ),
        (
            "Benchmark 4: Organizing a 2-Day AI Hackathon Event",
            "Organize a 2-day technical AI hackathon for 100 participants in 3 weeks with a $1,500 prize pool"
        )
    ]

    print("\n🚀 EXECUTING 4 BENCHMARK TASK PLANNING SCENARIOS...\n")

    for title, query in scenarios:
        print(f"\n{'='*80}\n📌 {title}\n{'='*80}")
        state = agent.run(query)
        display_agent_run(state)

    print("\n✅ All 4 benchmark scenarios completed successfully!\n")
    print("💡 To interact live with the Task Planner Agent, run:")
    print("   python main.py --cli")
    print("   python main.py --web")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--cli" in args:
        from cli import interactive_mode
        interactive_mode()
    elif "--web" in args:
        print("Launching Streamlit Web Dashboard at http://localhost:8501...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"])
    elif "--test" in args:
        subprocess.run([sys.executable, "-m", "unittest", "test_agent.py"])
    else:
        run_demo()
