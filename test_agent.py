from agent.schemas import TaskPlanRequest
from agent.planner_agent import TaskPlannerAgent

agent = TaskPlannerAgent()
req = TaskPlanRequest(
    goal="Plan a 5-day trip to Tokyo and Kyoto with cultural experiences",
    budget=250000.0,
    currency="JPY"
)

def stream_cb(step):
    print(f"[{step['step_type']}] Step {step['step_number']}: {step['title']}")

res = agent.run_agentic_workflow(req, stream_callback=stream_cb)
print("\n=== PLAN GENERATED SUCCESSFULLY ===")
print("Plan ID:", res.plan_id)
print("Target Budget:", res.currency, res.target_budget)
print("Allocated Total:", res.currency, res.estimated_total_cost)
print("Contingency Reserve:", res.currency, res.contingency_reserve)
print("Phases Count:", len(res.phases))
print("Total Tasks:", sum(len(p.subtasks) for p in res.phases))
print("Feasibility Score:", res.feasibility_score)
print("Timeline:", res.duration_summary)
print("First Subtask:", res.phases[0].subtasks[0].title, "| Cost:", res.phases[0].subtasks[0].currency, res.phases[0].subtasks[0].estimated_cost)
