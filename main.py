"""
Main Entry Point for Techvruk AI Agentic System.
Usage:
    python main.py             # Run automated demo test scenarios
    python main.py --cli       # Start interactive CLI mode
    python main.py --web       # Launch Streamlit web dashboard
    python main.py --test      # Execute test suite
"""

import sys
import os
import subprocess

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.core import SupportAgent
from cli import display_agent_run, print_banner


def run_demo():
    """Run predefined realistic demonstration scenarios."""
    print_banner()
    agent = SupportAgent()

    scenarios = [
        (
            "Scenario 1: Knowledge Base Policy Inquiry",
            "What is your standard return and refund policy for retail goods?"
        ),
        (
            "Scenario 2: Real-time Order & Delivery Tracking",
            "Can you check the tracking status of my order ORD-89421?"
        ),
        (
            "Scenario 3: Autonomous Refund Processing (30-Day Window)",
            "I received order ORD-89421 on September 16, but the headphones have severe distortion. Please refund my payment."
        ),
        (
            "Scenario 4: High-Value Emergency & Human Escalation",
            "This is UNACCEPTABLE! My order ORD-90214 was over $640, it is severely delayed, and your carrier won't respond. Escalate this to a human manager immediately or I contact my attorney!"
        )
    ]

    print("\n🚀 EXECUTING 4 BENCHMARK AGENTIC WORKFLOW SCENARIOS...\n")

    for title, query in scenarios:
        print(f"\n{'='*75}\n📌 {title}\n{'='*75}")
        state = agent.run(query)
        display_agent_run(state)

    print("\n✅ All 4 benchmark scenarios completed successfully!\n")
    print("💡 To interact live with the agent, run:")
    print("   python main.py --cli")
    print("   streamlit run app.py")


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--cli" in args:
        from cli import interactive_mode
        interactive_mode()
    elif "--web" in args:
        print("Launching Streamlit Web Dashboard at http://localhost:8501...")
        subprocess.run(["streamlit", "run", "app.py"])
    elif "--test" in args:
        subprocess.run(["python", "-m", "unittest", "test_agent.py"])
    else:
        run_demo()
