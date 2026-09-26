"""
Generate 5-Slide Presentation Deck for Gemini Task Planner Agent.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    DARK_BG = RGBColor(19, 19, 20)
    WHITE = RGBColor(240, 244, 249)
    BLUE = RGBColor(66, 133, 244)
    PURPLE = RGBColor(155, 114, 203)
    GRAY = RGBColor(142, 145, 143)

    slides_data = [
        {
            "title": "✦ Chatbot Techvruk",
            "subtitle": "Autonomous Multi-Currency AI Agent for General Task Orchestration",
            "bullets": [
                "• Autonomous ReAct Workflow: Plan -> Act -> Observe -> Adjust -> Respond",
                "• General-Purpose: Plans ANY task (Travel, Software MVP, Events, Marketing, Renovation, etc.)",
                "• Arbitrary Multi-Currency Budgeting: 35+ Global Currencies with 12% Contingency Reserve",
                "• Production-Grade Gemini UI: Real-time execution streaming, interactive checklist, and exports"
            ]
        },
        {
            "title": "Problem Statement & Why One-Shot LLMs Fail",
            "subtitle": "Moving from Superficial Prompting to True Autonomous Agentic Behavior",
            "bullets": [
                "• The Failure of Single-Shot LLMs: Generates static bullet lists without budget verification or currency checks.",
                "• Zero Financial Constraints: Traditional LLMs cannot guarantee that line items stay within budget caps.",
                "• The Solution: Multi-step ReAct pattern where the agent uses computational tools to verify every number.",
                "• Feasibility Index: Calculates mathematical feasibility and safeguards contingency funds against unexpected spikes."
            ]
        },
        {
            "title": "System Architecture & The 5-Stage ReAct Loop",
            "subtitle": "Transparent Execution Pipeline with Real-Time Server-Sent Events (SSE)",
            "bullets": [
                "• 1. PLAN: Deconstructs user intent, classifies domain, and extracts budget & currency parameters.",
                "• 2. ACT: Executes 6 specialized tools (CurrencyConverter, BudgetCalculator, ScheduleEstimator, RiskEvaluator, ResourceFinder, KnowledgeRetriever).",
                "• 3. OBSERVE: Validates financial feasibility, checks constraints, and assesses risk probability/impact.",
                "• 4. ADJUST: Rebalances phase allocations, resolves dependency sequencing, and tags priorities.",
                "• 5. RESPOND: Synthesizes final actionable plan and streams execution steps live to the client."
            ]
        },
        {
            "title": "Multi-Currency & Financial Feasibility Engine",
            "subtitle": "Strict Budget Control in Any Currency with Zero Debt Risk",
            "bullets": [
                "• 35+ World Currencies Supported: USD ($), EUR (€), INR (₹), GBP (£), JPY (¥), CAD (C$), AUD (A$), AED, CHF, SGD, etc.",
                "• Dedicated 12% Contingency Buffer: Automatically set aside to protect against price volatility and fees.",
                "• Phased Fund Allocation: Distributes deployable funds proportionally based on domain benchmarks.",
                "• Granular Cost & Time Attribution: Every single subtask receives localized cost, duration, and tool tags."
            ]
        },
        {
            "title": "Key Deliverables, UI Excellence & Impact",
            "subtitle": "Complete Full-Stack Implementation Ready for Production",
            "bullets": [
                "• Google Gemini Aesthetics: Clean dark/light theme, floating pill composer, and real-time execution trace drawer.",
                "• Interactive Task Workspace: Check off completed subtasks, view dependencies, and inspect risk mitigations.",
                "• Follow-Up Chat Refinement: Ask the agent to reduce expenses, shorten timelines, or explain tasks dynamically.",
                "• Multi-Format Exports: Instant export to Markdown (.md), structured JSON (.json), and printable views.",
                "• 100% Autonomous Out-of-the-Box: Zero paid API key dependency, with optional Google Gemini 2.5 Flash integration."
            ]
        }
    ]

    for s_idx, s_info in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)

        # Background fill
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = DARK_BG

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(1.2))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = s_info["title"]
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = BLUE if s_idx > 0 else PURPLE

        # Subtitle
        p2 = tf.add_paragraph()
        p2.text = s_info["subtitle"]
        p2.font.size = Pt(18)
        p2.font.color.rgb = GRAY

        # Content Box
        body_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.7), Inches(4.5))
        btf = body_box.text_frame
        btf.word_wrap = True

        for b_text in s_info["bullets"]:
            bp = btf.add_paragraph()
            bp.text = b_text
            bp.font.size = Pt(20)
            bp.font.color.rgb = WHITE
            bp.space_after = Pt(18)

    prs.save("Techvruk_Agentic_System_Presentation.pptx")
    print("Presentation saved as Techvruk_Agentic_System_Presentation.pptx")

if __name__ == "__main__":
    create_deck()
