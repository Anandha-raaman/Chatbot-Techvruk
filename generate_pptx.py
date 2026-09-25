"""
Automated 5-Slide Presentation Generator for Universal Task Planner Agent.
Generates 'Techvruk_Agentic_System_Presentation.pptx' with executive Red & White aesthetic.
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

    # Red & White Gemini-Style Palette
    BG_WHITE = RGBColor(250, 250, 252)       # Soft Off-White
    CARD_WHITE = RGBColor(255, 255, 255)     # Pure White
    CARD_BORDER = RGBColor(226, 232, 240)    # Slate 200
    ACCENT_RED = RGBColor(220, 38, 38)       # Crimson Red #DC2626
    ACCENT_DARK_RED = RGBColor(153, 27, 27)  # Dark Red #991B1B
    TEXT_DARK = RGBColor(15, 23, 42)         # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139)     # Slate 500

    def add_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_WHITE
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_tag):
        # Category Tag in Red
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = category_tag.upper()
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_RED

        # Title in Dark Slate
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_DARK

    # -------------------------------------------------------------
    # SLIDE 1: Title & Cover Slide (Red & White Theme)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide1)

    # Accent decorative bar
    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.5), Inches(0.8), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_RED
    bar.line.fill.background()

    tbox1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.5))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "TECHVRUK AI CONTEST SUBMISSION • UNIVERSAL AGENTIC SYSTEM"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = ACCENT_RED
    p_badge.space_after = Pt(14)

    p_main = tf1.add_paragraph()
    p_main.text = "Universal Task Planner Agent\nAutonomous Goal Decomposition for ANY Task"
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_DARK
    p_main.space_after = Pt(16)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Accepts any arbitrary goal (e.g. travel, software development, exam prep, event planning)\nand autonomously deconstructs it into phased subtasks, critical path schedules, and risk safeguards."
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_after = Pt(32)

    p_meta = tf1.add_paragraph()
    p_meta.text = "Candidate: Anandha Raaman S  |  Stack: Python, Pydantic, Gemini API / Offline Engine, Streamlit (Red & White Theme)"
    p_meta.font.size = Pt(14)
    p_meta.font.bold = True
    p_meta.font.color.rgb = ACCENT_DARK_RED

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement & Agentic Value
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide2)
    add_header(slide2, "The Problem: Why Unstructured Goals Fail in One-Shot Prompting", "01 / Context & Problem")

    # Left Box: Traditional Single-Prompt LLM Failures
    box_l = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = CARD_WHITE
    box_l.line.color.rgb = ACCENT_RED
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p_lh = tf_l.paragraphs[0]
    p_lh.text = "❌ One-Shot LLM Text Generation"
    p_lh.font.size = Pt(18)
    p_lh.font.bold = True
    p_lh.font.color.rgb = ACCENT_RED
    p_lh.space_after = Pt(12)

    points_l = [
        "Unstructured Paragraph Dumps: Produces vague essays lacking sequential order, timestamps, or milestone checkpoints.",
        "Zero Constraint Verification: Never calculates whether a stated budget or timeline can realistically cover execution.",
        "Blind to Dependency Blockers: Schedules downstream actions before prerequisites are confirmed (e.g. touring before transit).",
        "Rigid Static Templates: Brittle bots fail when user input diverges from hardcoded topics."
    ]
    for pt in points_l:
        p = tf_l.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(10)

    # Right Box: Universal Agentic Solution
    box_r = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = CARD_WHITE
    box_r.line.color.rgb = CARD_BORDER
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p_rh = tf_r.paragraphs[0]
    p_rh.text = "✅ Universal Task Planner Solution"
    p_rh.font.size = Pt(18)
    p_rh.font.bold = True
    p_rh.font.color.rgb = ACCENT_DARK_RED
    p_rh.space_after = Pt(12)

    points_r = [
        "Universal Goal Deconstruction: Dynamically analyzes ANY task or prompt without being restricted to pre-baked plans.",
        "Phased Sub-Task Matrix: Generates discrete, numbered subtasks with duration estimates and explicit deliverables.",
        "Feasibility Auditing: Tests timeline and budget limits against operational benchmarks with feasibility scoring (0-100).",
        "Critical Path & Risk Guardrails: Maps sequential bottleneck chains and injects automated contingency safeguards."
    ]
    for pt in points_r:
        p = tf_r.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 3: System Architecture & ReAct Workflow
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide3)
    add_header(slide3, "System Architecture: Plan → Act → Observe → Respond", "02 / Architecture & Flow")

    steps_data = [
        ("1. PLAN", "Task Intent Parsing", "Extracts primary objective, numerical timeline, budget ceiling, and complexity tier for ANY goal."),
        ("2. ACT", "Universal Tool Invocations", "Calls specialized tools: intent analyzer, feasibility auditor, subtask decomposer, critical path scheduler."),
        ("3. OBSERVE", "Telemetry Scratchpad", "Accumulates structured observations and constraint checks into Pydantic AgentState memory."),
        ("4. RESPOND", "Master Plan Synthesis", "Compiles phase matrix, milestone timeline, risk safeguards, and persists plan with unique Plan ID.")
    ]

    for i, (title, sub, desc) in enumerate(steps_data):
        x = Inches(0.8 + i * 2.95)
        step_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), Inches(2.8), Inches(4.8))
        step_box.fill.solid()
        step_box.fill.fore_color.rgb = CARD_WHITE
        step_box.line.color.rgb = ACCENT_RED if i == 0 or i == 3 else CARD_BORDER
        tf_s = step_box.text_frame
        tf_s.word_wrap = True

        ps1 = tf_s.paragraphs[0]
        ps1.text = title
        ps1.font.size = Pt(16)
        ps1.font.bold = True
        ps1.font.color.rgb = ACCENT_RED
        ps1.space_after = Pt(6)

        ps2 = tf_s.add_paragraph()
        ps2.text = sub
        ps2.font.size = Pt(13)
        ps2.font.bold = True
        ps2.font.color.rgb = TEXT_DARK
        ps2.space_after = Pt(10)

        ps3 = tf_s.add_paragraph()
        ps3.text = desc
        ps3.font.size = Pt(12)
        ps3.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: Tool Suite & Multi-Domain Benchmarks
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide4)
    add_header(slide4, "Universal Tool Suite & Multi-Domain Planning Capabilities", "03 / Tool Suite & Benchmarks")

    # Left: Tool Ecosystem
    tool_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tool_box.fill.solid()
    tool_box.fill.fore_color.rgb = CARD_WHITE
    tool_box.line.color.rgb = CARD_BORDER
    tf_t = tool_box.text_frame
    tf_t.word_wrap = True

    pt_h = tf_t.paragraphs[0]
    pt_h.text = "🛠️ Autonomous Planning Tools"
    pt_h.font.size = Pt(18)
    pt_h.font.bold = True
    pt_h.font.color.rgb = ACCENT_RED
    pt_h.space_after = Pt(10)

    tools_list = [
        "analyze_task_intent: Extracts goal intent, domain category, timeline constraints & complexity.",
        "audit_feasibility_and_effort: Computes workload hours, feasibility scores (0-100) & bottlenecks.",
        "decompose_any_task: Universally breaks down any task into 4 phased, chronological deliverables.",
        "derive_critical_path_and_milestones: Calculates sequential critical paths & 3 progress gates.",
        "audit_failure_modes_and_safeguards: Identifies operational risks & automated mitigations.",
        "persist_master_plan: Archives compiled master plans into permanent JSON storage."
    ]
    for tl in tools_list:
        p = tf_t.add_paragraph()
        p.text = f"• {tl}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # Right: Multi-Domain Benchmarks
    demo_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    demo_box.fill.solid()
    demo_box.fill.fore_color.rgb = CARD_WHITE
    demo_box.line.color.rgb = ACCENT_RED
    tf_d = demo_box.text_frame
    tf_d.word_wrap = True

    pd_h = tf_d.paragraphs[0]
    pd_h.text = "🌐 Tested Across Diverse Domains"
    pd_h.font.size = Pt(18)
    pd_h.font.bold = True
    pd_h.font.color.rgb = ACCENT_DARK_RED
    pd_h.space_after = Pt(10)

    demo_pts = [
        "Travel & Trips: 'Plan a 3-day trip to Tokyo for 2 people on a $1,200 budget.' (Phased daily itinerary, transit & lodging).",
        "Software Engineering: 'Build and launch a SaaS AI MVP in 4 weeks with authentication and billing.' (PRD, backend, frontend, testing).",
        "Exam Prep & Certifications: 'Prepare for AWS Solutions Architect in 30 days.' (Study milestones, practice labs, revision).",
        "Events & Hackathons: 'Organize a 2-day technical hackathon for 100 participants in 3 weeks.' (Venue, prizes, mentorship).",
        "Domestic & Lifestyle: 'Renovate apartment with $5,000 budget' or 'Train for a half marathon in 10 weeks.'"
    ]
    for dp in demo_pts:
        p = tf_d.add_paragraph()
        p.text = f"• {dp}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 5: Test Coverage, Tech Stack & Contest Compliance
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide5)
    add_header(slide5, "Test Coverage, Technology Stack & Contest Compliance", "04 / Benchmarks & Compliance")

    metrics_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    metrics_box.fill.solid()
    metrics_box.fill.fore_color.rgb = CARD_WHITE
    metrics_box.line.color.rgb = CARD_BORDER
    tf_m = metrics_box.text_frame
    tf_m.word_wrap = True

    pm_h = tf_m.paragraphs[0]
    pm_h.text = "🎯 Benchmark Verification & Compliance Matrix"
    pm_h.font.size = Pt(18)
    pm_h.font.bold = True
    pm_h.font.color.rgb = ACCENT_RED
    pm_h.space_after = Pt(12)

    specs = [
        "100% Automated Test Suite: 6 automated unit tests validating intent extraction, feasibility scoring, arbitrary task decomposition, critical path derivation, risk safeguards, and end-to-end plan generation.",
        "Strict Agentic Behavior: Demonstrates true Plan -> Act -> Observe -> Respond workflow with continuous scratchpad telemetry (no single-shot prompt hacks).",
        "Free-Tier & Zero-Key Compliance: Supports Google Gemini API (gemini-1.5-flash) and features a built-in offline simulator engine so judges can run it without API keys.",
        "Ultra-Smooth Red & White Gemini UI: Minimalist, clean user interface styled with crimson red accents and floating suggestion chips.",
        "Audit Trail: Structured plan export into JSON guarantees every generated plan has a unique Plan ID (PLAN-2026-...) for verifiable execution."
    ]
    for sp in specs:
        p = tf_m.add_paragraph()
        p.text = f"✔ {sp}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    prs.save(output_path)
    print(f"[SUCCESS] Successfully created 5-slide presentation at: {output_path}")


if __name__ == "__main__":
    create_presentation()
