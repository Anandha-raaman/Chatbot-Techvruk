"""
Automated 5-Slide Presentation Generator for Techvruk AI Agentic System.
Generates 'Techvruk_Agentic_System_Presentation.pptx' using python-pptx with modern executive styling.
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

    # Color Palette
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
    p_badge.text = "TECHVRUK AI CONTEST SUBMISSION • AGENTIC SYSTEM"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = ACCENT_BLUE
    p_badge.space_after = Pt(14)

    p_main = tf1.add_paragraph()
    p_main.text = "Autonomous Customer Support &\nIntelligent Escalation Agent"
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_WHITE
    p_main.space_after = Pt(16)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Demonstrating the Complete ReAct Agentic Cycle: Plan → Act → Observe → Respond\nWith Dynamic Multi-Tool Execution & Tier-2 Human Escalation Protocol"
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
    add_header(slide2, "The Problem: Why Single-Call Chatbots Fail in Enterprise Support", "01 / Context & Problem")

    # Left Box: Traditional Chatbot Limitations
    box_l = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = CARD_BG
    box_l.line.color.rgb = RGBColor(239, 68, 68)
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p_lh = tf_l.paragraphs[0]
    p_lh.text = "❌ Traditional Support Chatbots"
    p_lh.font.size = Pt(18)
    p_lh.font.bold = True
    p_lh.font.color.rgb = RGBColor(248, 113, 113)
    p_lh.space_after = Pt(12)

    points_l = [
        "Brittle One-Shot Prompts: Output hallucinations without verifying actual database or live inventory records.",
        "Static Rule Trees: Inflexible decision trees frustrate customers when non-standard edge cases occur.",
        "No Autonomous Action: Incapable of calculating date deltas, checking policy constraints, or issuing refunds.",
        "Blinded to Customer Distress: Fails to detect escalating rage or legal risks that require human intervention."
    ]
    for pt in points_l:
        p = tf_l.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)

    # Right Box: Agentic ReAct Solution
    box_r = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = CARD_BG
    box_r.line.color.rgb = ACCENT_GREEN
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p_rh = tf_r.paragraphs[0]
    p_rh.text = "✅ Our Autonomous Agentic Solution"
    p_rh.font.size = Pt(18)
    p_rh.font.bold = True
    p_rh.font.color.rgb = ACCENT_GREEN
    p_rh.space_after = Pt(12)

    points_r = [
        "Decomposed Multi-Step Planning: Breaks complex user queries into an ordered sequence of discrete subtasks.",
        "Tool-Use & Grounded Execution: Queries live Knowledge Base, checks customer order database, and evaluates policies.",
        "State & Context Maintenance: Preserves full scratchpad history (Thoughts, Actions, Observations) across turns.",
        "Deterministic Escalation Protocols: Formulates Tier-2 tickets with urgency and SLA guarantees when human touch is vital."
    ]
    for pt in points_r:
        p = tf_r.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 3: System Architecture & Workflow Diagram
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide3)
    add_header(slide3, "System Architecture: Plan → Act → Observe → Respond", "02 / Architecture & Flow")

    steps_data = [
        ("1. PLAN", "Task Decomposition", "Extracts user intent, customer entities (Order ID, Email), and formulates ordered subtasks."),
        ("2. ACT", "Tool Dispatching", "Invokes specialized tools: search_knowledge_base, lookup_customer_order, check_eligibility."),
        ("3. OBSERVE", "Feedback Accumulation", "Captures raw tool results into structured Pydantic AgentState scratchpad memory."),
        ("4. RESPOND", "Resolution / Escalation", "Processes refund autonomously or triggers Tier-2 Human Escalation with SLA tracking.")
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
    # SLIDE 4: Tool Suite & Dynamic Escalation Protocol
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide4)
    add_header(slide4, "Autonomous Tool Suite & Multi-Tier Escalation Safeguards", "03 / Capabilities & Safety")

    # Left: Tool Ecosystem
    tool_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    tool_box.fill.solid()
    tool_box.fill.fore_color.rgb = CARD_BG
    tool_box.line.color.rgb = ACCENT_BLUE
    tf_t = tool_box.text_frame
    tf_t.word_wrap = True

    pt_h = tf_t.paragraphs[0]
    pt_h.text = "🛠️ The 6-Tool Autonomous Ecosystem"
    pt_h.font.size = Pt(18)
    pt_h.font.bold = True
    pt_h.font.color.rgb = ACCENT_BLUE
    pt_h.space_after = Pt(10)

    tools_list = [
        "search_knowledge_base: BM25 relevance ranking over return & warranty policies.",
        "lookup_customer_order: Fetches real-time status, courier tracking, and item details.",
        "check_refund_eligibility: Verifies delivery dates against 30-day return policy.",
        "process_refund: Autonomous ledger crediting with transaction reference generation.",
        "escalate_to_human: Routes priority incident packet to Tier-2 specialist.",
        "log_support_ticket: Persistent CRM interaction archiving."
    ]
    for tl in tools_list:
        p = tf_t.add_paragraph()
        p.text = f"• {tl}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Right: Human Escalation Safeguards
    esc_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    esc_box.fill.solid()
    esc_box.fill.fore_color.rgb = CARD_BG
    esc_box.line.color.rgb = RGBColor(245, 158, 11)
    tf_e = esc_box.text_frame
    tf_e.word_wrap = True

    pe_h = tf_e.paragraphs[0]
    pe_h.text = "🛡️ When Does The Agent Escalate?"
    pe_h.font.size = Pt(18)
    pe_h.font.bold = True
    pe_h.font.color.rgb = RGBColor(251, 191, 36)
    pe_h.space_after = Pt(10)

    esc_reasons = [
        "Sentiment & Tone Analysis: Detects angry, distressed, or legally aggressive language and bypasses bot loop.",
        "High-Value Financial Thresholds: Orders exceeding $500 with courier delays route to human supervisors.",
        "Policy Exceptions & Extenuating Grounds: Expired 30-day returns with claimed hospital/courier fault are queued with incident context.",
        "Zero Information Loss: Full transcript, tool observations, and order ID are packaged in the Tier-2 Ticket."
    ]
    for er in esc_reasons:
        p = tf_e.add_paragraph()
        p.text = f"• {er}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 5: Tech Stack, Benchmark Results & Conclusion
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_background(slide5)
    add_header(slide5, "Technology Stack, Test Coverage & Evaluation Summary", "04 / Benchmarks & Compliance")

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
        "100% Automated Test Coverage: 6 comprehensive unit tests validating policy lookup, order verification, 30-day delta calculations, autonomous refunding, and human escalation.",
        "Dual-Engine Flexibility: Connects to Google Gemini API (gemini-1.5-flash / gemini-2.5-flash) for live LLM reasoning, OR runs with built-in zero-key offline deterministic engine.",
        "Fairness & Free-Tier Adherence: Complies fully with contest guidelines prohibiting paid/restricted APIs — requires zero paid tokens for complete evaluation.",
        "Multi-Modal User Interfaces: Includes interactive CLI with rich trace visualization and a full Streamlit Web UI with live reasoning inspector and 1-click test scenarios.",
        "Audit Trail: Structured CRM logging in JSON guarantees all actions, refund transactions, and human escalations are fully traceable."
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
