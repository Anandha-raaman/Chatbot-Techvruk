"""
Task Planner Agent: Autonomous ReAct and Plan-and-Execute Agent.
Implements the core agentic workflow:
Plan -> Act (Tool Invocations) -> Observe -> Adjust -> Respond.
Works on ANY general task with arbitrary budget and currency constraints.
"""

from typing import Dict, Any, List, Optional, Generator
import json
import uuid
import datetime
import os
import re
import math

from agent.schemas import (
    TaskPlanRequest, PlanOutput, PhasePlan, SubTask,
    BudgetAnalysis, RiskItem, ResourceItem, AgenticStepLog
)
from agent.tools import (
    CurrencyConverter, BudgetCalculator, ScheduleEstimator,
    RiskEvaluator, ResourceFinder, KnowledgeRetriever
)

class TaskPlannerAgent:
    """
    Autonomous Task Planner Agent capable of deconstructing any task,
    budgeted in any world currency, using multi-step tool execution.
    """

    def __init__(self, default_api_key: Optional[str] = None):
        self.default_api_key = default_api_key or os.environ.get("GEMINI_API_KEY")

    def run_agentic_workflow(
        self,
        request: TaskPlanRequest,
        stream_callback: Optional[callable] = None
    ) -> PlanOutput:
        """
        Executes the ReAct loop:
        1. PLAN: Deconstruct goal & identify target parameters.
        2. ACT (Tool 1: Currency Normalization): Validate currency & exchange rates.
        3. ACT (Tool 2: Knowledge Retrieval): Extract domain blueprints & task patterns.
        4. ACT (Tool 3: Budget Calculator): Allocate funds & contingency buffer.
        5. ACT (Tool 4: Schedule Estimator): Compute critical path & timelines.
        6. ACT (Tool 5: Resource & Risk Tools): Map tooling, dependencies & mitigations.
        7. OBSERVE: Verify constraint satisfaction & budget alignment.
        8. ADJUST: Rebalance subtasks & financial allocations.
        9. RESPOND: Synthesize comprehensive plan.
        """
        plan_id = str(uuid.uuid4())[:8]
        execution_steps: List[AgenticStepLog] = []

        def log_step(
            step_num: int,
            step_type: str,
            title: str,
            thought: str,
            tool_name: Optional[str] = None,
            tool_input: Optional[Dict[str, Any]] = None,
            tool_output: Optional[Dict[str, Any]] = None
        ):
            step = AgenticStepLog(
                step_number=step_num,
                step_type=step_type,
                title=title,
                thought=thought,
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=tool_output,
                timestamp=datetime.datetime.now().strftime("%H:%M:%S")
            )
            execution_steps.append(step)
            if stream_callback:
                stream_callback(step.model_dump())

        # =========================================================================
        # STEP 1: [PLAN] - Goal Decomposition & Intent Understanding
        # =========================================================================
        goal = request.goal.strip()
        category = KnowledgeRetriever.match_category(goal)
        
        # Check if user mentioned currency or budget inside goal text as well
        extracted_budget, extracted_currency = self._extract_price_and_currency(goal)
        user_currency = request.currency if request.currency and request.currency != "USD" else (extracted_currency or request.currency or "USD")
        user_currency = CurrencyConverter.normalize_currency_code(user_currency)
        
        target_budget = request.budget if request.budget > 0 else (extracted_budget or 0.0)

        log_step(
            step_num=1,
            step_type="PLAN",
            title="Goal Decomposition & Scope Analysis",
            thought=(
                f"Analyzing user goal: '{goal}'. Domain classified as '{category.upper()}'. "
                f"Target price/budget constraint detected: {CurrencyConverter.get_symbol(user_currency)}{target_budget:,.2f} "
                f"in currency '{user_currency}'. Initiating agentic decomposition into milestones and workstreams."
            )
        )

        # =========================================================================
        # STEP 2: [ACT - Tool: Currency Converter]
        # =========================================================================
        conv_result = CurrencyConverter.convert(target_budget, user_currency, "USD")
        user_symbol = CurrencyConverter.get_symbol(user_currency)

        log_step(
            step_num=2,
            step_type="ACT",
            title="Currency Normalization & Exchange Rate Audit",
            thought=f"Invoking CurrencyConverter to establish conversion metrics and baseline purchasing power.",
            tool_name="currency_converter",
            tool_input={"amount": target_budget, "from_currency": user_currency, "to_currency": "USD"},
            tool_output=conv_result
        )

        # =========================================================================
        # STEP 3: [ACT - Tool: Knowledge Retriever]
        # =========================================================================
        template = KnowledgeRetriever.get_template(category)
        
        log_step(
            step_num=3,
            step_type="ACT",
            title="Domain Blueprint & Workflow Retrieval",
            thought=(
                f"Retrieving proven industry execution blueprints for '{category}' tasks. "
                f"Extracting standard phase sequences, dependency chains, and effort distributions."
            ),
            tool_name="knowledge_retriever",
            tool_input={"domain": category, "goal": goal},
            tool_output={"phases_found": len(template["phases"]), "blueprint_category": category}
        )

        # =========================================================================
        # STEP 4: [ACT - Tool: Budget Calculator]
        # =========================================================================
        raw_budget_calc = BudgetCalculator.calculate_plan_budget(
            target_budget=target_budget,
            currency=user_currency,
            category=category,
            phase_count=len(template["phases"]),
            complexity="medium" if request.depth == "balanced" else "high"
        )

        log_step(
            step_num=4,
            step_type="ACT",
            title="Multi-Currency Budget & Contingency Allocation",
            thought=(
                f"Calculating financial feasibility in {user_currency}. Establishing 12% contingency reserve "
                f"({user_symbol}{raw_budget_calc['contingency_reserve']:,.2f}) to safeguard against price spikes. "
                f"Deployable budget: {user_symbol}{raw_budget_calc['deployable_budget']:,.2f}."
            ),
            tool_name="budget_calculator",
            tool_input={"target_budget": target_budget, "currency": user_currency, "category": category},
            tool_output=raw_budget_calc
        )

        # =========================================================================
        # STEP 5: [ACT - Tool: Resource Finder & Risk Evaluator]
        # =========================================================================
        resources_list = ResourceFinder.find_resources(
            category=category,
            currency=user_currency,
            budget=raw_budget_calc["deployable_budget"]
        )
        risks_list = RiskEvaluator.evaluate_risks(
            goal=goal,
            category=category,
            budget=target_budget,
            currency=user_currency
        )

        log_step(
            step_num=5,
            step_type="ACT",
            title="Resource Mapping & Risk Assessment",
            thought=(
                f"Evaluating critical dependencies, software tools, equipment, and team requirements. "
                f"Conducting probability/impact risk matrix evaluation with mitigations."
            ),
            tool_name="risk_evaluator_and_resource_finder",
            tool_input={"category": category, "currency": user_currency, "budget": target_budget},
            tool_output={"resources_count": len(resources_list), "risks_identified": len(risks_list)}
        )

        # =========================================================================
        # STEP 6: [OBSERVE] - Validation & Feasibility Check
        # =========================================================================
        feasibility_status = "Optimal" if raw_budget_calc["is_within_budget"] else "Over-budget constraint detected"
        observation_thought = (
            f"Constraint validation results: Target {user_symbol}{target_budget:,.2f} {user_currency}. "
            f"Planned Total (with emergency reserve): {user_symbol}{(raw_budget_calc['allocated_total'] + raw_budget_calc['contingency_reserve']):,.2f}. "
            f"Feasibility Score: {raw_budget_calc['feasibility_score']}/100. Status: {feasibility_status}. "
            f"Identified {len(risks_list)} key risk vectors and {len(resources_list)} resource prerequisites."
        )

        log_step(
            step_num=6,
            step_type="OBSERVE",
            title="Constraint Satisfaction & Feasibility Audit",
            thought=observation_thought
        )

        # =========================================================================
        # STEP 7: [ADJUST] - Construct Granular Tasks & Normalize Line Items
        # =========================================================================
        constructed_phases: List[PhasePlan] = []
        all_flattened_tasks: List[Dict[str, Any]] = []
        task_counter = 1

        # Check if Gemini API key is available for AI-enhanced personalization
        gemini_key = request.gemini_api_key or self.default_api_key
        gemini_enrichment = None
        if gemini_key:
            gemini_enrichment = self._call_gemini_api(goal, user_currency, target_budget, category, gemini_key)

        for p_idx, phase_blueprint in enumerate(template["phases"]):
            phase_num = p_idx + 1
            phase_id = f"P{phase_num}"
            phase_name = phase_blueprint["name"]
            phase_desc = phase_blueprint["description"]
            
            phase_budget_alloc = raw_budget_calc["phase_allocations"].get(f"Phase {phase_num}", 0.0)
            phase_subtasks: List[SubTask] = []
            
            raw_tasks = phase_blueprint["tasks"]
            # If Gemini gave us enriched tasks, we can blend them
            if gemini_enrichment and phase_num <= len(gemini_enrichment.get("phases", [])):
                g_phase = gemini_enrichment["phases"][phase_num - 1]
                phase_name = g_phase.get("name", phase_name)
                phase_desc = g_phase.get("description", phase_desc)
                if g_phase.get("tasks"):
                    raw_tasks = [
                        (t["title"], t["description"], float(t.get("hours", 4.0)), float(t.get("cost_weight", 0.33)))
                        for t in g_phase["tasks"]
                    ]

            # Distribute phase budget across tasks
            for t_idx, task_tuple in enumerate(raw_tasks):
                task_title, task_desc, hours, cost_ratio = task_tuple
                
                # Contextualize task title with the specific user goal
                task_title_contextualized = self._contextualize_task(task_title, goal, category)
                task_desc_contextualized = self._contextualize_desc(task_desc, goal, category)

                task_cost = round(phase_budget_alloc * cost_ratio, 2)
                subtask_id = f"T{task_counter:02d}"
                task_counter += 1

                req_tools = self._assign_tools(task_title_contextualized, category)
                priority = "High" if t_idx == 0 or task_cost > (phase_budget_alloc * 0.4) else "Medium"
                
                deps = [f"T{task_counter-2:02d}"] if task_counter > 2 and t_idx > 0 else []

                st = SubTask(
                    id=subtask_id,
                    title=task_title_contextualized,
                    description=task_desc_contextualized,
                    phase=phase_name,
                    estimated_duration=f"{hours:.1f} hours",
                    duration_hours=hours,
                    estimated_cost=task_cost,
                    currency=user_currency,
                    required_tools=req_tools,
                    dependencies=deps,
                    priority=priority,
                    completed=False
                )
                phase_subtasks.append(st)
                all_flattened_tasks.append(st.model_dump())

            constructed_phases.append(PhasePlan(
                phase_id=phase_id,
                phase_name=phase_name,
                description=phase_desc,
                duration_days=max(2, math.ceil(sum(t.duration_hours for t in phase_subtasks) / 6.0)),
                phase_budget=phase_budget_alloc,
                currency=user_currency,
                subtasks=phase_subtasks
            ))

        # Re-run Schedule Estimator with final tasks
        schedule_calc = ScheduleEstimator.estimate_schedule(all_flattened_tasks, request.target_duration)

        log_step(
            step_num=7,
            step_type="ADJUST",
            title="Plan Optimization & Dependency Sequencing",
            thought=(
                f"Generated {len(all_flattened_tasks)} actionable subtasks across {len(constructed_phases)} phases. "
                f"Sequenced dependencies and calculated critical path duration: {schedule_calc['timeline_summary']}. "
                f"Normalized all task costs strictly to {user_currency}."
            )
        )

        # =========================================================================
        # STEP 8: [RESPOND] - Final Plan Synthesis
        # =========================================================================
        budget_analysis = BudgetAnalysis(
            total_budget=target_budget,
            currency=user_currency,
            allocated_cost=raw_budget_calc["allocated_total"],
            contingency_reserve=raw_budget_calc["contingency_reserve"],
            remaining_buffer=raw_budget_calc["remaining_buffer"],
            feasibility_score=raw_budget_calc["feasibility_score"],
            is_within_budget=raw_budget_calc["is_within_budget"],
            currency_rate_to_usd=conv_result["effective_rate"],
            breakdown_by_phase=raw_budget_calc["phase_allocations"],
            recommendations=raw_budget_calc["recommendations"]
        )

        risks_obj = [RiskItem(**r) for r in risks_list]
        resources_obj = [ResourceItem(**res) for res in resources_list]

        summary_text = (
            f"Autonomous Agent Plan for '{goal}'. "
            f"The workflow is structured into {len(constructed_phases)} phases comprising {len(all_flattened_tasks)} sequential sub-tasks. "
            f"Total budget allocated: {CurrencyConverter.format(raw_budget_calc['allocated_total'], user_currency)} "
            f"with a dedicated {CurrencyConverter.format(raw_budget_calc['contingency_reserve'], user_currency)} contingency reserve "
            f"in {user_currency}. Estimated project delivery: {schedule_calc['timeline_summary']}."
        )

        log_step(
            step_num=8,
            step_type="RESPOND",
            title="Final Agent Response & Plan Delivery",
            thought="Complete structured plan assembled with financial metrics, timeline, and task checklist. Delivering response."
        )

        return PlanOutput(
            plan_id=plan_id,
            goal=goal,
            summary=summary_text,
            category=category,
            currency=user_currency,
            target_budget=target_budget,
            estimated_total_cost=round(raw_budget_calc["allocated_total"] + raw_budget_calc["contingency_reserve"], 2),
            contingency_reserve=raw_budget_calc["contingency_reserve"],
            duration_summary=schedule_calc["timeline_summary"],
            feasibility_score=raw_budget_calc["feasibility_score"],
            phases=constructed_phases,
            budget_analysis=budget_analysis,
            risks=risks_obj,
            resources=resources_obj,
            execution_steps=execution_steps,
            created_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def _extract_price_and_currency(self, text: str) -> (Optional[float], Optional[str]):
        """Detects currency amounts like '$2500', '€4000', '₹50,000', '1500 USD', etc."""
        # Pattern 1: Symbol before number (e.g. $2500, ₹50,000, €4,000)
        sym_match = re.search(r'([$€£₹¥])\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)', text)
        if sym_match:
            symbol = sym_match.group(1)
            amt_str = sym_match.group(2).replace(',', '')
            return float(amt_str), symbol

        # Pattern 2: Number before or after currency code (e.g. 2500 USD, 50000 INR, EUR 3000)
        code_match = re.search(r'([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(USD|EUR|INR|GBP|JPY|CAD|AUD|CHF|CNY|SGD|AED|NZD|BRL)', text, re.IGNORECASE)
        if code_match:
            amt_str = code_match.group(1).replace(',', '')
            return float(amt_str), code_match.group(2).upper()

        code_match_rev = re.search(r'(USD|EUR|INR|GBP|JPY|CAD|AUD|CHF|CNY|SGD|AED|NZD|BRL)\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)', text, re.IGNORECASE)
        if code_match_rev:
            amt_str = code_match_rev.group(2).replace(',', '')
            return float(amt_str), code_match_rev.group(1).upper()

        return None, None

    def _contextualize_task(self, template_title: str, goal: str, category: str) -> str:
        # Enhances generic blueprint titles with user's specific context
        words = [w for w in goal.split() if len(w) > 3 and w.lower() not in ["plan", "with", "make", "create", "need", "want"]]
        target_name = " ".join(words[:4]) if words else goal
        
        if "travel" in category:
            return template_title.replace("City Center", target_name.title())
        elif "software" in category:
            return template_title.replace("MVP", f"'{target_name}' MVP")
        elif "event" in category:
            return template_title.replace("Event", f"'{target_name}'")
        return template_title

    def _contextualize_desc(self, template_desc: str, goal: str, category: str) -> str:
        return f"{template_desc} Aligned specifically with target objective: '{goal}'."

    def _assign_tools(self, task_title: str, category: str) -> List[str]:
        t_lower = task_title.lower()
        if "reserve" in t_lower or "flight" in t_lower or "lodging" in t_lower:
            return ["Booking API", "Google Flights", "Airbnb/Hotel Portal"]
        elif "schema" in t_lower or "database" in t_lower or "backend" in t_lower:
            return ["PostgreSQL", "Prisma/SQLAlchemy", "Docker"]
        elif "frontend" in t_lower or "ui" in t_lower:
            return ["Figma", "HTML5/CSS3", "JavaScript/React"]
        elif "ad" in t_lower or "marketing" in t_lower:
            return ["Google Ads", "Meta Ads Manager", "GA4"]
        elif "venue" in t_lower or "speaker" in t_lower:
            return ["Eventbrite", "Contracts CRM", "Zoom/A/V Equipment"]
        elif "insurance" in t_lower or "esim" in t_lower:
            return ["Airalo eSIM", "WorldNomads"]
        elif "testing" in t_lower or "qa" in t_lower:
            return ["PyTest", "Jest", "Postman"]
        return ["Workspace", "Task Tracker", "Spreadsheet"]

    def _call_gemini_api(self, goal: str, currency: str, budget: float, category: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Optional call to Google Gemini API when API key is provided."""
        try:
            import google.genai as genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are an expert AI Task Planner Agent.
Goal: {goal}
Category: {category}
User Budget: {budget} {currency}

Provide a JSON object with 3 phases. Each phase has:
- name: Phase title
- description: Brief description
- tasks: List of 3 tasks, each with title, description, hours (float), cost_weight (float between 0.1 and 0.5, sum of phase tasks should equal ~1.0).

Return ONLY valid JSON matching this schema, no markdown code fence."""
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            text = response.text.strip()
            # Clean markdown codeblocks if any
            if text.startswith("```"):
                text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
                text = re.sub(r"\n?```$", "", text)
            return json.loads(text)
        except Exception as e:
            # Fallback smoothly to deterministic agentic reasoning
            print(f"Gemini API invocation fallback: {e}")
            return None
