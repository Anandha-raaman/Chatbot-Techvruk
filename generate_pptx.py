"""
Generate a world-class, clean, neat, and smart 5-slide presentation for Chatbot Techvruk.
Uses python-pptx with custom cards, precise geometric layout, and executive dark-mode styling.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="Techvruk_Agentic_System_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette - Sophisticated Slate / Dark Mode
    BG_COLOR = RGBColor(11, 15, 25)         # Deep slate/navy
    CARD_BG = RGBColor(19, 26, 42)          # Card container background
    CARD_BORDER = RGBColor(38, 51, 80)      # Subtle border
    ACCENT_BLUE = RGBColor(56, 140, 255)    # Gemini Blue
    ACCENT_CYAN = RGBColor(56, 189, 248)    # Cyan highlight
    ACCENT_GREEN = RGBColor(52, 211, 153)   # Mint / Success
    ACCENT_AMBER = RGBColor(251, 191, 36)   # Amber / Caution
    ACCENT_PURPLE = RGBColor(167, 139, 250) # Purple
    ACCENT_CORAL = RGBColor(248, 113, 113)  # Soft red / Alert

    TEXT_TITLE = RGBColor(248, 250, 252)    # Clean crisp white
    TEXT_BODY = RGBColor(226, 232, 240)     # Off-white / light slate
    TEXT_MUTED = RGBColor(148, 163, 184)    # Slate muted

    def set_slide_background(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

    def add_header(slide, tag_text, title_text, subtitle_text, slide_num):
        # Category Tag Badge
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(8.0), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.name = "Segoe UI"
        p_tag.font.size = Pt(10.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_BLUE

        # Slide Number at Top Right
        num_box = slide.shapes.add_textbox(Inches(9.5), Inches(0.45), Inches(3.0), Inches(0.35))
        tf_num = num_box.text_frame
        tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
        p_num = tf_num.paragraphs[0]
        p_num.text = f"CHATBOT TECHVRUK  |  SLIDE 0{slide_num} OF 05"
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(10)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MUTED

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = "Segoe UI"
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_TITLE

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.38), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(13)
        p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
        return shape

    # =========================================================================
    # SLIDE 1: Executive Overview & The Mission
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_header(s1, "PROJECT OVERVIEW & CORE MISSION", "Chatbot Techvruk: Autonomous AI Task Planner",
               "Universal agentic task decomposition with live multi-currency budget governance", 1)

    cards_s1 = [
        {
            "tag": "CAPABILITY 01",
            "tag_color": ACCENT_BLUE,
            "title": "Universal Task Planning",
            "sub": "Handles Any Objective",
            "body": "Moves far beyond narrow bots. Intelligently structures software launches, corporate events, travel itineraries, product marketing, home renovation, or academic research into logical phased milestones."
        },
        {
            "tag": "CAPABILITY 02",
            "tag_color": ACCENT_GREEN,
            "title": "Arbitrary Currency Engine",
            "sub": "35+ Currencies with Safety Reserve",
            "body": "Seamlessly detects user-specified currencies in natural language (USD, EUR, INR, GBP, JPY, etc.). Rigorously isolates a mandatory 12% contingency reserve to prevent overruns."
        },
        {
            "tag": "CAPABILITY 03",
            "tag_color": ACCENT_PURPLE,
            "title": "Gemini 3.5 Flash Lite Core",
            "sub": "Sub-2s Real-Time Inference",
            "body": "Powered by Google Gemini 3.5 Flash Lite paired with an autonomous ReAct loop. Delivers transparent reasoning logs, live execution streaming (SSE), and interactive task checklists."
        }
    ]

    c_width = Inches(3.72)
    c_gap = Inches(0.28)
    c_top = Inches(1.95)
    c_height = Inches(4.2)

    for i, c in enumerate(cards_s1):
        c_left = Inches(0.8) + i * (c_width + c_gap)
        add_card(s1, c_left, c_top, c_width, c_height)

        tb = s1.shapes.add_textbox(c_left + Inches(0.28), c_top + Inches(0.28), c_width - Inches(0.56), c_height - Inches(0.56))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = c["tag"]
        p0.font.name = "Segoe UI"
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = c["tag_color"]
        p0.space_after = Pt(8)

        p1 = tf.add_paragraph()
        p1.text = c["title"]
        p1.font.name = "Segoe UI"
        p1.font.size = Pt(19)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_TITLE
        p1.space_after = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = c["sub"]
        p2.font.name = "Segoe UI"
        p2.font.size = Pt(12)
        p2.font.color.rgb = ACCENT_CYAN
        p2.space_after = Pt(14)

        p3 = tf.add_paragraph()
        p3.text = c["body"]
        p3.font.name = "Segoe UI"
        p3.font.size = Pt(12.5)
        p3.font.color.rgb = TEXT_BODY
        p3.line_spacing = 1.25

    # Bottom Highlight Bar
    bar_s1 = add_card(s1, Inches(0.8), Inches(6.35), Inches(11.733), Inches(0.7), bg_color=RGBColor(16, 22, 36), border_color=RGBColor(45, 60, 92))
    tb_b1 = s1.shapes.add_textbox(Inches(1.0), Inches(6.45), Inches(11.3), Inches(0.5))
    tf_b1 = tb_b1.text_frame
    tf_b1.margin_left = tf_b1.margin_top = tf_b1.margin_right = tf_b1.margin_bottom = 0
    pb1 = tf_b1.paragraphs[0]
    pb1.text = "✦ Key Innovation: The user never touches manual currency dropdowns; the agent extracts context, verifies math with internal tools, and outputs ready-to-execute plans."
    pb1.font.name = "Segoe UI"
    pb1.font.size = Pt(11.5)
    pb1.font.color.rgb = RGBColor(190, 210, 240)

    # =========================================================================
    # SLIDE 2: Problem Statement & Agentic Value
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "CHALLENGE & BREAKTHROUGH", "Why Standard LLMs Fail vs. The Agentic Solution",
               "Overcoming superficial prompting with mathematical rigor and autonomous validation", 2)

    w_half = Inches(5.72)
    gap_half = Inches(0.29)
    top_half = Inches(1.95)
    h_half = Inches(5.1)

    # Left: Standard LLMs
    left_card = add_card(s2, Inches(0.8), top_half, w_half, h_half, border_color=RGBColor(70, 35, 45))
    tb_l = s2.shapes.add_textbox(Inches(1.1), top_half + Inches(0.3), w_half - Inches(0.6), h_half - Inches(0.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0

    pl_tag = tf_l.paragraphs[0]
    pl_tag.text = "THE PROBLEM: TRADITIONAL CHATBOTS"
    pl_tag.font.name = "Segoe UI"
    pl_tag.font.size = Pt(11)
    pl_tag.font.bold = True
    pl_tag.font.color.rgb = ACCENT_CORAL
    pl_tag.space_after = Pt(12)

    problems = [
        ("Hallucinated Financials", "Generates random numbers without verifying if line items exceed the user's budget ceiling or account for hidden costs."),
        ("Static & Brittle Output", "Provides generic, unchangeable text lists. Cannot dynamically recalculate when currencies, timelines, or scopes shift."),
        ("Zero Dependency Checking", "Lists tasks without sequencing prerequisites, causing bottlenecks and unviable project schedules."),
        ("No Risk Safeguards", "Fails to reserve contingency funds, leaving the plan vulnerable to price shocks and sudden delays.")
    ]
    for p_title, p_desc in problems:
        pt = tf_l.add_paragraph()
        pt.text = f"•  {p_title}"
        pt.font.name = "Segoe UI"
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_TITLE

        pd = tf_l.add_paragraph()
        pd.text = f"   {p_desc}"
        pd.font.name = "Segoe UI"
        pd.font.size = Pt(11.5)
        pd.font.color.rgb = TEXT_MUTED
        pd.space_after = Pt(10)

    # Right: Chatbot Techvruk
    right_card = add_card(s2, Inches(0.8) + w_half + gap_half, top_half, w_half, h_half, border_color=RGBColor(35, 75, 60))
    tb_r = s2.shapes.add_textbox(Inches(0.8) + w_half + gap_half + Inches(0.3), top_half + Inches(0.3), w_half - Inches(0.6), h_half - Inches(0.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    pr_tag = tf_r.paragraphs[0]
    pr_tag.text = "THE BREAKTHROUGH: CHATBOT TECHVRUK"
    pr_tag.font.name = "Segoe UI"
    pr_tag.font.size = Pt(11)
    pr_tag.font.bold = True
    pr_tag.font.color.rgb = ACCENT_GREEN
    pr_tag.space_after = Pt(12)

    solutions = [
        ("Audited Mathematical Accuracy", "Every single phase and milestone cost is audited via internal tools. Total expenditure is mathematically guaranteed ≤ user budget."),
        ("Dynamic ReAct Architecture", "Runs an autonomous Plan → Act → Observe loop that iteratively verifies feasibility and refines resource allocation."),
        ("12% Built-In Contingency", "Automatically partitions 12% of total capital into an emergency reserve before calculating deployable subtask funds."),
        ("Multi-Plan Interactive Session", "Generates unlimited distinct plans in a single chat with live interactive checklists and instant follow-up refinement.")
    ]
    for s_title, s_desc in solutions:
        st = tf_r.add_paragraph()
        st.text = f"✓  {s_title}"
        st.font.name = "Segoe UI"
        st.font.size = Pt(13)
        st.font.bold = True
        st.font.color.rgb = TEXT_TITLE

        sd = tf_r.add_paragraph()
        sd.text = f"   {s_desc}"
        sd.font.name = "Segoe UI"
        sd.font.size = Pt(11.5)
        sd.font.color.rgb = TEXT_BODY
        sd.space_after = Pt(10)

    # =========================================================================
    # SLIDE 3: System Architecture & 5-Step ReAct Loop
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "SYSTEM ARCHITECTURE", "The 5-Stage ReAct Execution Pipeline",
               "End-to-end autonomous flow connecting user intent to live-streamed actionable plans", 3)

    steps = [
        ("01", "PARSE & PLAN", ACCENT_BLUE, "User Input", "Deconstructs query, classifies domain (Tech, Travel, Event, etc.), and extracts budget amount & currency in background."),
        ("02", "ACT (TOOLS)", ACCENT_CYAN, "Tool Invocation", "Executes specialized tools: CurrencyConverter, BudgetCalculator, ScheduleEstimator, and RiskEvaluator."),
        ("03", "OBSERVE", ACCENT_GREEN, "Audit & Metrics", "Inspects tool results, calculates Feasibility Score (1-100), and validates financial ceiling & timeline constraints."),
        ("04", "ADJUST", ACCENT_AMBER, "Rebalancing", "Rebalances phase funds, establishes dependency sequences, locks 12% contingency, and tags task priorities."),
        ("05", "STREAM", ACCENT_PURPLE, "Client Delivery", "Streams execution steps via SSE, renders interactive UI checklist, and binds plan to the active session.")
    ]

    c5_w = Inches(2.18)
    c5_gap = Inches(0.20)
    c5_top = Inches(1.95)
    c5_h = Inches(4.2)

    for i, (num, title, color, tag, desc) in enumerate(steps):
        c5_left = Inches(0.8) + i * (c5_w + c5_gap)
        add_card(s3, c5_left, c5_top, c5_w, c5_h)

        tb = s3.shapes.add_textbox(c5_left + Inches(0.18), c5_top + Inches(0.22), c5_w - Inches(0.36), c5_h - Inches(0.44))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_num = tf.paragraphs[0]
        p_num.text = f"PHASE {num}"
        p_num.font.name = "Segoe UI"
        p_num.font.size = Pt(10.5)
        p_num.font.bold = True
        p_num.font.color.rgb = color
        p_num.space_after = Pt(6)

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_TITLE
        p_t.space_after = Pt(4)

        p_tag = tf.add_paragraph()
        p_tag.text = tag
        p_tag.font.name = "Segoe UI"
        p_tag.font.size = Pt(10.5)
        p_tag.font.color.rgb = color
        p_tag.space_after = Pt(12)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = TEXT_BODY
        p_d.line_spacing = 1.2

    # Bottom Architecture Summary
    bar_s3 = add_card(s3, Inches(0.8), Inches(6.35), Inches(11.733), Inches(0.7), bg_color=RGBColor(16, 22, 36), border_color=RGBColor(45, 60, 92))
    tb_b3 = s3.shapes.add_textbox(Inches(1.0), Inches(6.45), Inches(11.3), Inches(0.5))
    tf_b3 = tb_b3.text_frame
    tf_b3.margin_left = tf_b3.margin_top = tf_b3.margin_right = tf_b3.margin_bottom = 0
    pb3 = tf_b3.paragraphs[0]
    pb3.text = "⚡ Transparency by Design: Users watch the agent's real-time thought trace in the slide-out execution drawer, establishing 100% explainability."
    pb3.font.name = "Segoe UI"
    pb3.font.size = Pt(11.5)
    pb3.font.color.rgb = RGBColor(190, 210, 240)

    # =========================================================================
    # SLIDE 4: Financial Precision & Multi-Currency Engine
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "FINANCIAL PRECISION & MULTI-CURRENCY", "Zero-Debt Financial Architecture & Global Budgeting",
               "Deterministic budget enforcement and currency flexibility without UI friction", 4)

    # 3 Stat Cards on Top
    stats = [
        ("35+", "Global Currencies", "USD ($), EUR (€), INR (₹), GBP (£), JPY (¥), CAD, AUD, AED, CHF, SGD, etc. Automatically identified from natural language prompts."),
        ("12%", "Mandatory Safety Reserve", "Every plan isolates 12% upfront before line-item budgeting to safeguard against inflation, unexpected fees, and scope changes."),
        ("100%", "Zero-Debt Guarantee", "Mathematical validation ensures sum of milestones + contingency ≤ 100% of user budget. Overspending is impossible.")
    ]

    s_w = Inches(3.72)
    s_gap = Inches(0.28)
    s_top = Inches(1.95)
    s_h = Inches(2.2)

    for i, (metric, label, desc) in enumerate(stats):
        s_left = Inches(0.8) + i * (s_w + s_gap)
        add_card(s4, s_left, s_top, s_w, s_h)

        tb = s4.shapes.add_textbox(s_left + Inches(0.25), s_top + Inches(0.2), s_w - Inches(0.5), s_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        pm = tf.paragraphs[0]
        pm.text = metric
        pm.font.name = "Segoe UI"
        pm.font.size = Pt(32)
        pm.font.bold = True
        pm.font.color.rgb = ACCENT_CYAN if i == 0 else (ACCENT_GREEN if i == 1 else ACCENT_AMBER)

        pl = tf.add_paragraph()
        pl.text = label
        pl.font.name = "Segoe UI"
        pl.font.size = Pt(13)
        pl.font.bold = True
        pl.font.color.rgb = TEXT_TITLE
        pl.space_after = Pt(4)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = "Segoe UI"
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_BODY

    # 2 Feature Panels on Bottom
    f_w = Inches(5.72)
    f_gap = Inches(0.29)
    f_top = Inches(4.35)
    f_h = Inches(2.7)

    # Feature 1
    add_card(s4, Inches(0.8), f_top, f_w, f_h)
    tb_f1 = s4.shapes.add_textbox(Inches(1.05), f_top + Inches(0.25), f_w - Inches(0.5), f_h - Inches(0.5))
    tf_f1 = tb_f1.text_frame
    tf_f1.word_wrap = True
    tf_f1.margin_left = tf_f1.margin_top = tf_f1.margin_right = tf_f1.margin_bottom = 0

    p_f1_t = tf_f1.paragraphs[0]
    p_f1_t.text = "BACKGROUND CURRENCY EXTRACTION"
    p_f1_t.font.name = "Segoe UI"
    p_f1_t.font.size = Pt(12)
    p_f1_t.font.bold = True
    p_f1_t.font.color.rgb = ACCENT_BLUE
    p_f1_t.space_after = Pt(6)

    bullets_f1 = [
        "• Invisible Intelligence: The user writes 'budget 50,000 INR' or 'under €4000'. The engine extracts ISO code, symbol, and numeric ceiling seamlessly.",
        "• Multi-Symbol Recognition: Handles symbols ($ € ₹ £ ¥ C$ A$), ISO codes (INR, EUR, USD), and localized words ('rupees', 'euros', 'dollars', 'pounds').",
        "• Zero Clutter: Keeps the chat interface uncluttered and distraction-free."
    ]
    for b in bullets_f1:
        pb = tf_f1.add_paragraph()
        pb.text = b
        pb.font.name = "Segoe UI"
        pb.font.size = Pt(11)
        pb.font.color.rgb = TEXT_BODY
        pb.space_after = Pt(4)

    # Feature 2
    add_card(s4, Inches(0.8) + f_w + f_gap, f_top, f_w, f_h)
    tb_f2 = s4.shapes.add_textbox(Inches(0.8) + f_w + f_gap + Inches(0.25), f_top + Inches(0.25), f_w - Inches(0.5), f_h - Inches(0.5))
    tf_f2 = tb_f2.text_frame
    tf_f2.word_wrap = True
    tf_f2.margin_left = tf_f2.margin_top = tf_f2.margin_right = tf_f2.margin_bottom = 0

    p_f2_t = tf_f2.paragraphs[0]
    p_f2_t.text = "PHASED COST & TIMELINE ATTRIBUTION"
    p_f2_t.font.name = "Segoe UI"
    p_f2_t.font.size = Pt(12)
    p_f2_t.font.bold = True
    p_f2_t.font.color.rgb = ACCENT_GREEN
    p_f2_t.space_after = Pt(6)

    bullets_f2 = [
        "• Domain-Weighted Phasing: Allocates funds across phases (e.g. Discovery 20%, Execution 50%, Finalization 18%, Contingency 12%).",
        "• Line-Item Attribution: Every subtask specifies estimated cost, duration in days/hours, dependency prerequisites, and priority level.",
        "• Feasibility Index: Calculates a mathematical feasibility score (1-100) based on budget tightness, schedule risks, and scope depth."
    ]
    for b in bullets_f2:
        pb = tf_f2.add_paragraph()
        pb.text = b
        pb.font.name = "Segoe UI"
        pb.font.size = Pt(11)
        pb.font.color.rgb = TEXT_BODY
        pb.space_after = Pt(4)

    # =========================================================================
    # SLIDE 5: UX, Technology Stack & Production Impact
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "PRODUCTION IMPACT & IMPLEMENTATION", "User Experience, Tech Stack & Real-World Utility",
               "A complete, full-stack agentic solution ready for enterprise deployment", 5)

    q_w = Inches(5.72)
    q_gap = Inches(0.29)
    q_top1 = Inches(1.95)
    q_top2 = Inches(4.55)
    q_h = Inches(2.45)

    quads = [
        (Inches(0.8), q_top1, "GEMINI-INSPIRED AESTHETICS", ACCENT_BLUE, "Clean & Modern Frontend", [
            "• Sleek dark/light theme designed with Google Gemini design principles.",
            "• Floating pill composer, responsive suggestions, and smooth micro-interactions.",
            "• Multi-Plan Continuity: Generate multiple independent plans within a single continuous chat session."
        ]),
        (Inches(0.8) + q_w + q_gap, q_top1, "INTERACTIVE WORKSPACE", ACCENT_CYAN, "Actionable Task Tracking", [
            "• Interactive Checklists: Real-time checkboxes with completion progress counters.",
            "• Risk & Mitigation Drawer: Inspect contingency allocations and preemptive action plans.",
            "• Natural Follow-Up Queries: Dynamically request cost reductions, timeline shifts, or task expansions."
        ]),
        (Inches(0.8), q_top2, "MODERN FULL-STACK STACK", ACCENT_PURPLE, "Engineered for Reliability", [
            "• LLM Engine: Google Gemini 3.5 Flash Lite with automatic fallback to 3.8-flash and local Ollama.",
            "• Backend: Python Flask REST API with Server-Sent Events (SSE) for low-latency streaming.",
            "• Frontend: Zero-dependency Vanilla ES6+ JavaScript and hand-crafted CSS."
        ]),
        (Inches(0.8) + q_w + q_gap, q_top2, "ENTERPRISE UTILITY & EXPORTS", ACCENT_GREEN, "Ready for Deployment", [
            "• Multi-Format Exports: One-click export to Markdown (.md), structured JSON (.json), and print view.",
            "• 100% Zero-Leak Security: API credentials strictly protected in .env with automated exclusion.",
            "• High Impact: Transforms multi-hour manual planning into a 2-second verified execution roadmap."
        ])
    ]

    for q_left, q_top, tag, color, title, bullets in quads:
        add_card(s5, q_left, q_top, q_w, q_h)

        tb = s5.shapes.add_textbox(q_left + Inches(0.28), q_top + Inches(0.2), q_w - Inches(0.56), q_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        pt = tf.paragraphs[0]
        pt.text = tag
        pt.font.name = "Segoe UI"
        pt.font.size = Pt(10.5)
        pt.font.bold = True
        pt.font.color.rgb = color
        pt.space_after = Pt(4)

        ph = tf.add_paragraph()
        ph.text = title
        ph.font.name = "Segoe UI"
        ph.font.size = Pt(14.5)
        ph.font.bold = True
        ph.font.color.rgb = TEXT_TITLE
        ph.space_after = Pt(8)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = b
            pb.font.name = "Segoe UI"
            pb.font.size = Pt(11)
            pb.font.color.rgb = TEXT_BODY
            pb.space_after = Pt(3)

    prs.save(output_path)
    print(f"World-class presentation successfully generated at: {output_path}")

if __name__ == "__main__":
    create_deck()
