"""
Interactive Command Line Interface for Techvruk AI Support Agent.
Displays rich real-time agent telemetry (Planning, Tool Invocations, Observations, and Final Output).
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.tree import Tree
from agent.core import SupportAgent

console = Console()


def print_banner():
    console.print("\n" + "=" * 80, style="bold cyan")
    console.print("🤖 TECHVRUK AI AGENTIC SYSTEM: CUSTOMER SUPPORT & ESCALATION AGENT", style="bold green", justify="center")
    console.print("Autonomous ReAct Workflow: Plan -> Act -> Observe -> Respond", style="dim white", justify="center")
    console.print("=" * 80 + "\n", style="bold cyan")


def display_agent_run(state):
    """Render full agent telemetry using Rich."""
    console.print(f"\n[bold yellow]🎯 User Goal/Task:[/bold yellow] [white]{state.user_query}[/white]")

    # 1. Plan View
    plan_tree = Tree("[bold cyan]📋 Decomposed Action Plan[/bold cyan]")
    for step in state.plan:
        status_icon = "✅" if step.status == "completed" else ("⏳" if step.status == "in_progress" else "⚪")
        plan_tree.add(f"{status_icon} [bold]Step {step.step_id}:[/bold] {step.description} [dim]({step.tool_hint})[/dim]")
    console.print(Panel(plan_tree, title="Execution Plan", border_style="cyan"))

    # 2. ReAct Scratchpad Loop (Thought -> Action -> Observation)
    console.print("\n[bold magenta]⚡ Agentic ReAct Execution Trace[/bold magenta]")
    for action in state.scratchpad:
        trace_table = Table(show_header=False, box=None, padding=(0, 1))
        trace_table.add_column("Key", style="bold blue", width=14)
        trace_table.add_column("Value", style="white")

        trace_table.add_row("🧠 Thought:", action.thought)
        trace_table.add_row("🔧 Tool Action:", f"[bold green]{action.action_name}[/bold green] (Input: {json.dumps(action.action_input)})")
        
        # Format observation
        obs_str = json.dumps(action.observation, indent=2) if isinstance(action.observation, (dict, list)) else str(action.observation)
        trace_table.add_row("👁️ Observation:", obs_str)

        console.print(Panel(trace_table, title=f"ReAct Step #{action.step_num}", border_style="magenta"))

    # 3. Escalation Banner (if triggered)
    if state.escalation.is_escalated:
        esc = state.escalation
        esc_panel = Panel(
            f"[bold red]⚠️ HUMAN ESCALATION PROTOCOL ACTIVATED[/bold red]\n"
            f"• Ticket ID: [bold]{esc.ticket_id}[/bold]\n"
            f"• Urgency: [bold]{esc.urgency.upper()}[/bold] | Sentiment: [bold]{esc.sentiment.upper()}[/bold]\n"
            f"• Target SLA: Under {esc.sla_minutes} Minutes | Queue: {esc.assigned_tier}",
            border_style="red"
        )
        console.print(esc_panel)

    # 4. Final Response
    console.print(Panel(Markdown(state.final_response), title="🌟 Final Coherent Agent Response", border_style="green"))
    console.print("-" * 80 + "\n", style="dim")


def interactive_mode():
    agent = SupportAgent()
    print_banner()

    console.print("[dim]Type your inquiry or scenario below. Enter 'exit' or 'quit' to quit.[/dim]\n")
    console.print("[bold cyan]Quick Test Examples you can copy & paste:[/bold cyan]")
    console.print("1. 'I want to know your return policy for electronics.'")
    console.print("2. 'What is the tracking status of my order ORD-89421?'")
    console.print("3. 'I ordered ORD-89421 and need a full refund because it arrived with scratches.'")
    console.print("4. 'This is UNACCEPTABLE! My order ORD-90214 was supposed to arrive days ago, cost me $649, and your courier lost it! Get me a manager immediately or I contact my lawyer!'")
    console.print("-" * 80 + "\n")

    while True:
        try:
            query = console.input("[bold green]User Input > [/bold green]").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Exiting Techvruk Support Agent. Good luck with the contest![/yellow]")
                break

            with console.status("[bold green]Agent planning and executing actions...[/bold green]"):
                state = agent.run(query)

            display_agent_run(state)

        except KeyboardInterrupt:
            console.print("\n[yellow]Session aborted by user.[/yellow]")
            break


if __name__ == "__main__":
    interactive_mode()
