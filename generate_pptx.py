"""
Automated 5-Slide Presentation Generator for Techvruk Task Planner Agent.
Generates 'Techvruk_Agentic_System_Presentation.pptx' using python-pptx with executive widescreen styling.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


def create_presentation(output_path: str = "Techvruk_Agentic_System_Presentation.pptx"):
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Executive Color Palette
    BG_DARK = RGBColor(15, 23, 42)        # Slate 900
    CARD_BG = RGBColor(30, 41, 59)        # Slate 800
    ACCENT_BLUE = RGBColor(56, 189, 248)  # Sky 400
    ACCENT_GREEN = RGBColor(74, 222, 128) # Emerald 400
    TEXT_WHITE = RGBColor(248, 250, 252)  # Slate 50
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400

    def add_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_tag):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = category_tag.upper()
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_BLUE

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 1: Title & Cover Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide1)

    tbox1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.0))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "TECHVRUK AI CONTEST SUBMISSION • TASK PLANNER AGENT"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = ACCENT_BLUE
    p_badge.space_after = Pt(14)

    p_main = tf1.add_paragraph()
    p_main.text = "Autonomous Task Planner Agent\nGoal Decomposition & Execution Architecture"
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_WHITE
    p_main.space_after = Pt(16)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Given an ambiguous goal (e.g. 'plan a 3-day trip'), autonomously decomposes it into phased sub-tasks,\ncomputes feasibility, critical path schedules, budget allocations, and contingency safeguards."
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_after = Pt(32)

    p_meta = tf1.add_paragraph()
    p_meta.text = "Candidate: Anandha Raaman S  |  Stack: Python, Pydantic, Gemini API / Offline Engine, Streamlit"
    p_meta.font.size = Pt(14)
    p_meta.font.bold = True
    p_meta.font.color.rgb = ACCENT_GREEN

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement & Agentic Value
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide2)
    add_header(slide2, "The Problem: Why Unstructured Goals Fail in Single-Call LLMs", "01 / Context & Problem")

    # Left Box: Traditional Single-Prompt LLM Failures
    box_l = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = CARD_BG
    box_l.line.color.rgb = RGBColor(239, 68, 68)
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p_lh = tf_l.paragraphs[0]
    p_lh.text = "❌ One-Shot LLM Text Generation"
    p_lh.font.size = Pt(18)
    p_lh.font.bold = True
    p_lh.font.color.rgb = RGBColor(248, 113, 113)
    p_lh.space_after = Pt(12)

    points_l = [
        "Unstructured Paragraph Dumps: Produces vague essays lacking sequential order, timestamps, or milestone checkpoints.",
        "Zero Constraint Verification: Never calculates whether a $1,200 budget or 3-day window can realistically cover the itinerary.",
        "Blind to Dependency Blockers: Schedules downstream actions before prerequisites are confirmed (e.g. touring before transit).",
        "No Operational Safeguards: Ignores weather contingencies, booking lead times, and failure points."
    ]
    for pt in points_l:
        p = tf_l.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)

    # Right Box: Agentic Solution
    box_r = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = CARD_BG
    box_r.line.color.rgb = ACCENT_GREEN
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p_rh = tf_r.paragraphs[0]
    p_rh.text = "✅ Autonomous Task Planner Solution"
    p_rh.font.size = Pt(18)
    p_rh.font.bold = True
    p_rh.font.color.rgb = ACCENT_GREEN
    p_rh.space_after = Pt(12)

    points_r = [
        "Decomposed Multi-Phase Breakdown: Generates discrete, numbered sub-tasks with duration estimates and explicit deliverables.",
        "Feasibility Auditing: Tests timeline and budget limits against domain benchmarks with feasibility scoring (0-100).",
        "Critical Path Analysis: Maps dependency chains (TASK-01 ➔ TASK-02) and highlights bottlenecks.",
        "Deterministic Risk Mitigation: Injects automated contingency protocols for each identified operational failure point."
    ]
    for pt in points_r:
        p = tf_r.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 3: System Architecture & ReAct Workflow
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide3)
    add_header(slide3, "System Architecture: Plan → Act → Observe → Respond", "02 / Architecture & Flow")

    steps_data = [
        ("1. PLAN", "Constraint Parsing", "Extracts primary goal, numerical duration, budget ceiling, and domain classification."),
        ("2. ACT", "Tool Invocations", "Calls specialized tools: blueprint search, feasibility auditor, subtask decomposer, critical path scheduler."),
        ("3. OBSERVE", "State Scratchpad", "Accumulates structured observations and constraint checks into Pydantic AgentState memory."),
        ("4. RESPOND", "Master Plan Synthesis", "Compiles phase matrix, milestone timeline, budget breakdown, and persists plan with Plan ID.")
    ]

    for i, (title, sub, desc) in enumerate(steps_data):
        x = Inches(0.8 + i * 2.95)
        step_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.8), Inches(4.8))
        step_box.fill.solid()
        step_box.fill.fore_color.rgb = CARD_BG
        step_box.line.color.rgb = ACCENT_BLUE if i < 3 else ACCENT_GREEN
        tf_s = step_box.text_frame
        tf_s.word_wrap = True

        ps1 = tf_s.paragraphs[0]
        ps1.text = title
        ps1.font.size = Pt(16)
        ps1.font.bold = True
        ps1.font.color.rgb = ACCENT_BLUE if i < 3 else ACCENT_GREEN
        ps1.space_after = Pt(6)

        ps2 = tf_s.add_paragraph()
        ps2.text = sub
        ps2.font.size = Pt(13)
        ps2.font.bold = True
        ps2.font.color.rgb = TEXT_WHITE
        ps2.space_after = Pt(10)

        ps3 = tf_s.add_paragraph()
        ps3.text = desc
        ps3.font.size = Pt(12)
        ps3.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: Tool Suite & 3-Day Trip Benchmark
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide4)
    add_header(slide4, "Autonomous Tool Suite & 3-Day Trip Execution Showcase", "03 / Tool Suite & Benchmarks")

    # Left: Tool Ecosystem
    tool_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tool_box.fill.solid()
    tool_box.fill.fore_color.rgb = CARD_BG
    tool_box.line.color.rgb = ACCENT_BLUE
    tf_t = tool_box.text_frame
    tf_t.word_wrap = True

    pt_h = tf_t.paragraphs[0]
    pt_h.text = "🛠️ Autonomous Planning Tools"
    pt_h.font.size = Pt(18)
    pt_h.font.bold = True
    pt_h.font.color.rgb = ACCENT_BLUE
    pt_h.space_after = Pt(10)

    tools_list = [
        "search_domain_blueprints: Retrieves domain blueprints and milestone phases.",
        "analyze_goal_feasibility: Tests timeline feasibility and resource limits.",
        "decompose_into_subtasks: Generates phase-aligned, numbered sub-tasks with deliverables.",
        "calculate_schedule_and_critical_path: Derives sequential critical path and milestone checkpoints.",
        "assess_risks_and_mitigations: Identifies failure modes and injects contingency safeguards.",
        "export_structured_plan: Persists compiled master plan into permanent JSON records."
    ]
    for tl in tools_list:
        p = tf_t.add_paragraph()
        p.text = f"• {tl}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Right: 3-Day Trip Case Study
    demo_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    demo_box.fill.solid()
    demo_box.fill.fore_color.rgb = CARD_BG
    demo_box.line.color.rgb = ACCENT_GREEN
    tf_d = demo_box.text_frame
    tf_d.word_wrap = True

    pd_h = tf_d.paragraphs[0]
    pd_h.text = "🌸 Benchmark: 'Plan a 3-Day Trip to Tokyo'"
    pd_h.font.size = Pt(18)
    pd_h.font.bold = True
    pd_h.font.color.rgb = ACCENT_GREEN
    pd_h.space_after = Pt(10)

    demo_pts = [
        "Input Goal: 'Plan a 3-day cultural & culinary trip to Tokyo for 2 people on a $1,200 budget.'",
        "Phase 1 Logistics: Lodging reservation, flight transfers, local eSIM data, and IC transit card pre-orders.",
        "Phase 2 Itinerary: Day 1 arrival & orientation walk; Day 2 Asakusa & culinary food tour; Day 3 Meiji Shrine & market shopping.",
        "Budget Optimization: Allocates 35% lodging ($420), 25% transit ($300), 20% dining ($240), 12% activities ($144), 8% buffer ($96).",
        "Risk Mitigation: Pre-downloads offline transit maps and schedules open-date vouchers for rainy weather."
    ]
    for dp in demo_pts:
        p = tf_d.add_paragraph()
        p.text = f"• {dp}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 5: Test Coverage, Tech Stack & Contest Compliance
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide5)
    add_header(slide5, "Test Coverage, Technology Stack & Contest Compliance", "04 / Benchmarks & Compliance")

    metrics_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    metrics_box.fill.solid()
    metrics_box.fill.fore_color.rgb = CARD_BG
    metrics_box.line.color.rgb = ACCENT_GREEN
    tf_m = metrics_box.text_frame
    tf_m.word_wrap = True

    pm_h = tf_m.paragraphs[0]
    pm_h.text = "🎯 Benchmark Verification & Compliance Matrix"
    pm_h.font.size = Pt(18)
    pm_h.font.bold = True
    pm_h.font.color.rgb = ACCENT_GREEN
    pm_h.space_after = Pt(12)

    specs = [
        "100% Automated Test Suite: 6 automated unit tests validating blueprint search, feasibility scoring, 3-day subtask decomposition, critical path derivation, risk assessment, and end-to-end plan generation.",
        "Strict Agentic Behavior: Demonstrates true Plan -> Act -> Observe -> Respond workflow with continuous scratchpad telemetry (no single-shot prompt hacks).",
        "Free-Tier & Zero-Key Compliance: Supports Google Gemini API (gemini-1.5-flash) and features a built-in offline simulator engine so judges can run it without API keys.",
        "Dual Operational Interfaces: Interactive Streamlit Web UI with live reasoning inspector and 1-click test scenarios + rich terminal CLI.",
        "Audit Trail: Structured plan export into JSON guarantees every generated plan has a unique Plan ID (PLAN-2026-...) for verifiable execution."
    ]
    for sp in specs:
        p = tf_m.add_paragraph()
        p.text = f"✔ {sp}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    prs.save(output_path)
    print(f"[SUCCESS] Successfully created 5-slide presentation at: {output_path}")


if __name__ == "__main__":
    create_presentation()
