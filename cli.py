"""
Interactive Command Line Interface for Techvruk Universal Task Planner Agent.
Accepts ANY task or goal, performing real-time ReAct decomposition into subtasks.
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
from agent.core import TaskPlannerAgent

console = Console()


def print_banner():
    console.print("\n" + "=" * 80, style="bold red")
    console.print("✨ TECHVRUK UNIVERSAL TASK PLANNER AGENT", style="bold red", justify="center")
    console.print("Autonomous Goal Decomposition for ANY Task | ReAct Architecture", style="dim white", justify="center")
    console.print("=" * 80 + "\n", style="bold red")


def display_agent_run(state):
    """Render full agent telemetry and structured plan using Rich."""
    p = state.structured_plan
    c = state.parsed_constraints

    console.print(f"\n[bold red]🎯 User Goal:[/bold red] [white bold]{state.user_goal}[/white bold]")
    console.print(f"[dim]Category: [red]{c.get('category')}[/red] | Duration: [red]{c.get('timeline_days')} Days[/red] | Complexity: [red]{c.get('complexity')}[/red][/dim]\n")

    # 1. ReAct Scratchpad Loop
    console.print("[bold red]⚡ Agentic ReAct Tool Execution Trace[/bold red]")
    for action in state.scratchpad:
        trace_table = Table(show_header=False, box=None, padding=(0, 1))
        trace_table.add_column("Key", style="bold red", width=16)
        trace_table.add_column("Value", style="white")

        trace_table.add_row("🧠 Thought:", action.thought)
        trace_table.add_row("🔧 Tool Action:", f"[bold white on red] {action.action_name} [/bold white on red] (Input: {json.dumps(action.action_input)})")

        obs_str = json.dumps(action.observation, indent=2) if isinstance(action.observation, (dict, list)) else str(action.observation)
        if len(obs_str) > 350:
            obs_str = obs_str[:350] + "... [truncated]"
        trace_table.add_row("👁️ Observation:", obs_str)

        console.print(Panel(trace_table, title=f"ReAct Step #{action.step_num}: {action.action_name}", border_style="red"))

    # 2. Decomposed Sub-Tasks Table
    if p and p.subtasks:
        task_table = Table(title=f"📋 Decomposed Sub-Task Matrix ({len(p.subtasks)} Subtasks)", border_style="red")
        task_table.add_column("ID", style="bold red", width=9)
        task_table.add_column("Phase", style="white", width=24)
        task_table.add_column("Sub-Task Title", style="white", width=42)
        task_table.add_column("Duration", style="yellow", width=14)
        task_table.add_column("Priority", style="bold red", width=10)
        task_table.add_column("Dependencies", style="dim", width=12)

        for t in p.subtasks:
            dep_str = ", ".join(t.dependencies) if t.dependencies else "None"
            p_style = "bold red" if t.priority == "High" else "yellow"
            task_table.add_row(t.task_id, t.phase, t.title, t.estimated_duration, f"[{p_style}]{t.priority}[/{p_style}]", dep_str)

        console.print(task_table)

    # 3. Final Master Response
    console.print("\n")
    console.print(Panel(Markdown(state.final_response), title=f"🌟 Master Execution Plan [ID: {p.plan_id if p else 'N/A'}]", border_style="red"))
    console.print("-" * 80 + "\n", style="dim")


def interactive_mode():
    agent = TaskPlannerAgent()
    print_banner()

    console.print("[dim]Enter ANY task, goal, project, or event. The agent will autonomously decompose it into a structured plan.[/dim]\n")
    console.print("[bold red]Sample goals you can test:[/bold red]")
    console.print("1. 'Plan a 3-day trip to Tokyo on a $1,200 budget for 2 people with cultural landmarks'")
    console.print("2. 'Build and launch a SaaS AI MVP in 4 weeks with authentication and billing'")
    console.print("3. 'Prepare for the AWS Solutions Architect exam in 30 days studying 2 hours daily'")
    console.print("4. 'Organize a 2-day technical AI hackathon for 100 participants in 3 weeks'")
    console.print("5. 'Renovate and furnish a 2-bedroom apartment with a $5,000 budget in 2 weeks'")
    console.print("-" * 80 + "\n")

    while True:
        try:
            query = console.input("[bold red]User Goal > [/bold red]").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Exiting Universal Task Planner Agent. Good luck with the contest![/yellow]")
                break

            with console.status("[bold red]Agent deconstructing goal, evaluating feasibility, and compiling schedule...[/bold red]"):
                state = agent.run(query)

            display_agent_run(state)

        except KeyboardInterrupt:
            console.print("\n[yellow]Session terminated by user.[/yellow]")
            break


if __name__ == "__main__":
    interactive_mode()
