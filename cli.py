"""
Interactive Command Line Interface for Techvruk Task Planner Agent.
Visualizes real-time task decomposition, ReAct tool execution traces, Gantt milestones, and risk audits.
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
    console.print("\n" + "=" * 80, style="bold cyan")
    console.print("🧭 TECHVRUK AI AGENTIC SYSTEM: AUTONOMOUS TASK PLANNER AGENT", style="bold green", justify="center")
    console.print("Agentic Workflow: Given a goal (e.g. 'plan a 3-day trip'), break into sub-tasks & structured plan", style="dim white", justify="center")
    console.print("ReAct Pattern: Plan -> Act -> Observe -> Respond", style="dim white", justify="center")
    console.print("=" * 80 + "\n", style="bold cyan")


def display_agent_run(state):
    """Render full agent telemetry and structured plan using Rich."""
    p = state.structured_plan
    c = state.parsed_constraints

    console.print(f"\n[bold yellow]🎯 Primary Goal:[/bold yellow] [white bold]{state.user_goal}[/white bold]")
    console.print(f"[dim]Detected Domain: [cyan]{c.get('domain', '').upper()}[/cyan] | Duration: [cyan]{c.get('timeline_days')} Days[/cyan] | Budget: [cyan]${c.get('budget', 0):,.2f}[/cyan][/dim]\n")

    # 1. ReAct Scratchpad Loop (Thought -> Action -> Observation)
    console.print("[bold magenta]⚡ Agentic ReAct Tool Execution Trace[/bold magenta]")
    for action in state.scratchpad:
        trace_table = Table(show_header=False, box=None, padding=(0, 1))
        trace_table.add_column("Key", style="bold blue", width=16)
        trace_table.add_column("Value", style="white")

        trace_table.add_row("🧠 Thought:", action.thought)
        trace_table.add_row("🔧 Tool Action:", f"[bold green]{action.action_name}[/bold green] (Input: {json.dumps(action.action_input)})")

        obs_str = json.dumps(action.observation, indent=2) if isinstance(action.observation, (dict, list)) else str(action.observation)
        if len(obs_str) > 350:
            obs_str = obs_str[:350] + "... [truncated]"
        trace_table.add_row("👁️ Observation:", obs_str)

        console.print(Panel(trace_table, title=f"ReAct Step #{action.step_num}: {action.action_name}", border_style="magenta"))

    # 2. Decomposed Sub-Tasks Table
    if p and p.subtasks:
        task_table = Table(title=f"📋 Decomposed Sub-Task Matrix ({len(p.subtasks)} Subtasks)", border_style="cyan")
        task_table.add_column("ID", style="bold cyan", width=9)
        task_table.add_column("Phase", style="blue", width=22)
        task_table.add_column("Sub-Task Title", style="white", width=40)
        task_table.add_column("Duration", style="yellow", width=12)
        task_table.add_column("Priority", style="bold red", width=10)
        task_table.add_column("Dependencies", style="dim", width=12)

        for t in p.subtasks:
            dep_str = ", ".join(t.dependencies) if t.dependencies else "None"
            p_style = "bold red" if t.priority == "High" else "yellow"
            task_table.add_row(t.task_id, t.phase, t.title, t.estimated_duration, f"[{p_style}]{t.priority}[/{p_style}]", dep_str)

        console.print(task_table)

    # 3. Final Master Response
    console.print("\n")
    console.print(Panel(Markdown(state.final_response), title=f"🌟 Master Execution Plan [ID: {p.plan_id if p else 'N/A'}]", border_style="green"))
    console.print("-" * 80 + "\n", style="dim")


def interactive_mode():
    agent = TaskPlannerAgent()
    print_banner()

    console.print("[dim]Enter any complex goal. The agent will autonomously break it down and build a structured roadmap.[/dim]\n")
    console.print("[bold cyan]Preset Contest Examples you can test:[/bold cyan]")
    console.print("1. 'Plan a 3-day trip to Tokyo on a $1,200 budget for 2 people with cultural activities and culinary experiences'")
    console.print("2. 'Plan a 4-day weekend getaway to Paris with museum visits and historic walking tours'")
    console.print("3. 'Build and launch a SaaS AI MVP in 4 weeks with a $2,000 budget'")
    console.print("4. 'Organize a 2-day AI hackathon for 100 developers in 3 weeks'")
    console.print("-" * 80 + "\n")

    while True:
        try:
            query = console.input("[bold green]User Goal > [/bold green]").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Exiting Task Planner Agent. Good luck with the Techvruk contest![/yellow]")
                break

            with console.status("[bold green]Agent deconstructing goal, querying templates, assessing risks & scheduling...[/bold green]"):
                state = agent.run(query)

            display_agent_run(state)

        except KeyboardInterrupt:
            console.print("\n[yellow]Session terminated by user.[/yellow]")
            break


if __name__ == "__main__":
    interactive_mode()
