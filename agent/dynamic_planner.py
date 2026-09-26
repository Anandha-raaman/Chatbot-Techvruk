"""
Dynamic, intelligent Task Planner Engine.
Understands any task from natural language, extracts target budgets and currencies silently in the background,
and generates context-rich, realistic, and highly specific execution plans.
Supports live Google Gemini API when configured, with an advanced built-in reasoning engine as standard.
"""

import re
import math
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
load_dotenv()

from agent.tools import CurrencyConverter

class DynamicTaskPlanner:
    """
    Intelligently analyzes any user goal and generates custom-tailored,
    specific, and practical execution plans with realistic budget allocations.
    """

    @classmethod
    def extract_budget_and_currency(cls, text: str) -> Tuple[Optional[float], str]:
        """
        Silently parses user's natural language to detect budget and currency.
        Examples: '20,000 INR', 'budget 2500 USD', 'under $1500', '₹30,000', '€2000', '50k inr'
        Defaults to USD if no currency is mentioned.
        """
        # Currency symbol detection
        sym_map = {
            "₹": "INR", "$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY",
            "C$": "CAD", "A$": "AUD", "CHF": "CHF", "S$": "SGD", "AED": "AED"
        }
        for sym, code in sym_map.items():
            pattern = re.escape(sym) + r"\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?|\d+k?)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amt_str = match.group(1).lower().replace(",", "")
                if amt_str.endswith("k"):
                    amt = float(amt_str[:-1]) * 1000
                else:
                    amt = float(amt_str)
                return amt, code

        # Currency code detection (e.g. 20000 inr, 1500 usd, 50k eur, 3 lakh inr)
        code_pattern = r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?|\d+k?|\d+\s*(?:lakh|crore))\s*(usd|inr|eur|gbp|jpy|cad|aud|chf|sgd|aed|cny|brl|krw|peso|rupees?|dollars?|euros?|pounds?|yen)"
        match = re.search(code_pattern, text, re.IGNORECASE)
        if match:
            num_part = match.group(1).lower().replace(",", "").strip()
            curr_part = match.group(2).lower().strip()

            amt = 0.0
            if "lakh" in num_part:
                amt = float(re.sub(r"[^\d.]", "", num_part)) * 100000
            elif "crore" in num_part:
                amt = float(re.sub(r"[^\d.]", "", num_part)) * 10000000
            elif num_part.endswith("k"):
                amt = float(num_part[:-1]) * 1000
            else:
                amt = float(num_part)

            curr_map = {
                "rupee": "INR", "rupees": "INR", "inr": "INR",
                "dollar": "USD", "dollars": "USD", "usd": "USD",
                "euro": "EUR", "euros": "EUR", "eur": "EUR",
                "pound": "GBP", "pounds": "GBP", "gbp": "GBP",
                "yen": "JPY", "jpy": "JPY",
                "cad": "CAD", "aud": "AUD", "aed": "AED", "sgd": "SGD", "chf": "CHF"
            }
            return amt, curr_map.get(curr_part, "USD")

        # Reversed order: "budget of inr 25000", "budget: $500"
        rev_pattern = r"(usd|inr|eur|gbp|jpy|cad|aud|aed)\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?|\d+k?)"
        match_rev = re.search(rev_pattern, text, re.IGNORECASE)
        if match_rev:
            curr_code = match_rev.group(1).upper()
            amt_str = match_rev.group(2).lower().replace(",", "")
            amt = float(amt_str[:-1]) * 1000 if amt_str.endswith("k") else float(amt_str)
            return amt, curr_code

        # Standalone numbers with words like budget or cost
        standalone = re.search(r"(?:budget|price|cost|under|around|within)\s*(?:of|is|:)?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?|\d+k)", text, re.IGNORECASE)
        if standalone:
            amt_str = standalone.group(1).lower().replace(",", "")
            amt = float(amt_str[:-1]) * 1000 if amt_str.endswith("k") else float(amt_str)
            return amt, "USD"

        return None, "USD"

    @classmethod
    def generate_plan(cls, goal: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a specific, relevant, and comprehensive plan tailored to the user's exact request
        using a real-world LLM (Google Gemini or Qwen 2.5 7B).
        """
        extracted_budget, currency = cls.extract_budget_and_currency(goal)
        currency = CurrencyConverter.normalize_currency_code(currency)

        # 1. Try Google Gemini API if key is present
        effective_key = api_key or os.environ.get("GEMINI_API_KEY")
        if effective_key:
            ai_plan = cls._generate_with_gemini(goal, extracted_budget, currency, effective_key)
            if ai_plan:
                return ai_plan

        # 2. Use real-world LLM: Qwen 2.5 7B
        qwen_plan = cls._generate_with_qwen(goal, extracted_budget, currency)
        if qwen_plan:
            return qwen_plan

        # 3. Contextual Fallback
        return cls._generate_contextual_plan(goal, extracted_budget, currency)

    @classmethod
    def _clean_and_parse_json(cls, raw: str) -> Optional[Dict[str, Any]]:
        """Robustly extracts and parses a JSON object from LLM response text."""
        if not raw:
            return None
        text = raw.strip()
        # 1. Direct parse attempt
        try:
            return json.loads(text)
        except Exception:
            pass

        # 2. Markdown block extraction ```json ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        # 3. Outer curly braces fallback
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            candidate = text[first_brace:last_brace + 1]
            try:
                return json.loads(candidate)
            except Exception:
                pass

        return None

    @classmethod
    def _generate_with_qwen(cls, goal: str, budget: Optional[float], currency: str) -> Optional[Dict[str, Any]]:
        """Invokes local real-world LLM (Gemma 3 or Qwen 2.5 7B) with a strict timeout to ensure zero UI freezes."""
        try:
            import ollama
            import concurrent.futures
            budget_hint = f"User specified budget: {budget} {currency}." if budget else f"Estimate a realistic budget in {currency}."
            prompt = f"""You are an elite, practical task planner assistant powered by a real-world LLM.
User Goal: "{goal}"
{budget_hint}
Selected Currency: {currency}

Create a highly specific, tailored, and actionable plan. Do NOT give generic advice. Tailor every task directly to the specific place, technology, business, or task mentioned.
Allocate 10-15% of the total budget as an emergency contingency reserve.

Return ONLY a valid JSON object matching this schema, with no markdown code blocks and no surrounding text:
{{
  "title": "A concise title for the plan",
  "summary": "2-3 sentence executive summary explaining the strategy and feasibility.",
  "target_budget": <number total budget in {currency}>,
  "currency": "{currency}",
  "contingency_reserve": <number 12% contingency reserve in {currency}>,
  "allocated_cost": <number deployable budget in {currency}>,
  "duration_summary": "e.g., 3 Days / 4 Weeks / 2 Months",
  "phases": [
    {{
      "phase_name": "Phase 1: Specific Name",
      "description": "Specific focus of this phase",
      "phase_budget": <number in {currency}>,
      "tasks": [
        {{
          "id": "T01",
          "title": "Specific actionable task title",
          "details": "Concrete details, locations, tools, or steps.",
          "estimated_cost": <number in {currency}>,
          "duration": "e.g. 2 hours / 1 day",
          "priority": "High"
        }}
      ]
    }}
  ],
  "cost_breakdown": [
    {{"category": "Category 1", "amount": <number>, "percentage": 50}},
    {{"category": "Category 2", "amount": <number>, "percentage": 50}}
  ],
  "key_tips": [
    "Practical tip 1",
    "Practical tip 2"
  ]
}}"""
            import requests
            def _call_ollama(model):
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
                r = requests.post("http://localhost:11434/api/chat", json=payload, timeout=8.0)
                if r.status_code == 200:
                    return r.json().get("message", {}).get("content", "")
                return ""

            for model_name in ['gemma3:270m', 'qwen2.5:7b']:
                try:
                    content = _call_ollama(model_name)
                    if content:
                        data = cls._clean_and_parse_json(content)
                        if data and "title" in data and "phases" in data:
                            data["generated_by"] = f"Local LLM ({model_name})"
                            return data
                except Exception:
                    continue
            return None
        except Exception as e:
            print(f"[Local LLM Notice] Fallback: {e}")
            return None

    @classmethod
    def _generate_with_gemini(cls, goal: str, budget: Optional[float], currency: str, api_key: str) -> Optional[Dict[str, Any]]:
        """Invokes Google Gemini 2.5 Flash model for state-of-the-art plan generation."""
        try:
            import google.genai as genai
            client = genai.Client(api_key=api_key)

            budget_text = f"Budget provided: {CurrencyConverter.format(budget, currency)}" if budget else f"No budget explicitly provided. Estimate a realistic budget in {currency}."

            prompt = f"""You are an elite, practical task planner assistant.
User Request: "{goal}"
{budget_text}
Selected Currency: {currency}

Create a highly specific, tailored, and actionable plan. Do NOT give generic advice. Tailor every task directly to the specific place, technology, business, or task mentioned.

Output JSON format strictly conforming to this schema (no markdown formatting, no code blocks):
{{
  "title": "A concise, engaging title for the plan",
  "summary": "2-3 sentence executive summary explaining the strategy, feasibility, and core focus.",
  "target_budget": <number total budget in {currency}>,
  "currency": "{currency}",
  "contingency_reserve": <number 10-15% of total budget as emergency buffer in {currency}>,
  "allocated_cost": <number deployable budget in {currency}>,
  "duration_summary": "e.g., 3 Days / 4 Weeks / 2 Months",
  "phases": [
    {{
      "phase_name": "Phase or Day Title",
      "description": "Specific focus of this phase",
      "phase_budget": <number in {currency}>,
      "tasks": [
        {{
          "id": "T01",
          "title": "Specific, actionable task title",
          "details": "Concrete details, locations, tools, or steps.",
          "estimated_cost": <number in {currency}>,
          "duration": "e.g., 3 hours / 1 day",
          "priority": "High/Medium"
        }}
      ]
    }}
  ],
  "cost_breakdown": [
    {{"category": "e.g., Stay / Tech / Venue", "amount": <number>, "percentage": <number>}}
  ],
  "key_tips": [
    "Practical, specific tip 1",
    "Practical, specific tip 2",
    "Practical, specific tip 3"
  ]
}}"""

            for gemini_model in ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-flash-latest', 'gemini-2.5-flash']:
                try:
                    response = client.models.generate_content(
                        model=gemini_model,
                        contents=prompt
                    )
                    data = cls._clean_and_parse_json(response.text)
                    if data and "title" in data and "phases" in data:
                        data["generated_by"] = f"Google Gemini ({gemini_model})"
                        return data
                except Exception:
                    continue
            return None
        except Exception as e:
            print(f"[Gemini API Notice] Falling back to intelligent planner: {e}")
            return None

    @classmethod
    def _generate_contextual_plan(cls, goal: str, budget: Optional[float], currency: str) -> Dict[str, Any]:
        """
        Deep contextual planner that recognizes specific places, products, domains, and tasks.
        """
        goal_lower = goal.lower()

        # 1. Travel / Trip Planner
        if any(w in goal_lower for w in ["trip", "travel", "visit", "tour", "vacation", "holiday", "itinerary", "goa", "tokyo", "paris", "bali", "manali", "kerala", "dubai", "london", "singapore", "jaipur"]):
            return cls._plan_travel(goal, budget, currency)

        # 2. Software / App / Web MVP
        elif any(w in goal_lower for w in ["app", "software", "website", "saas", "mvp", "build app", "develop", "bot", "ai agent", "code", "frontend", "backend", "fullstack", "tech"]):
            return cls._plan_software(goal, budget, currency)

        # 3. Business / Shop / Cafe Launch
        elif any(w in goal_lower for w in ["cafe", "coffee", "restaurant", "bakery", "shop", "store", "boutique", "startup", "business", "launch", "ecommerce", "brand", "retail"]):
            return cls._plan_business(goal, budget, currency)

        # 4. Event / Conference / Party / Wedding
        elif any(w in goal_lower for w in ["event", "wedding", "conference", "party", "seminar", "summit", "meetup", "birthday"]):
            return cls._plan_event(goal, budget, currency)

        # 5. Study / Exam / Career / Fitness / General
        else:
            return cls._plan_general(goal, budget, currency)

    @classmethod
    def _plan_travel(cls, goal: str, budget: Optional[float], currency: str) -> Dict[str, Any]:
        """Specific travel plan tailored to the requested destination."""
        g = goal.lower()

        # Detect duration
        duration_days = 3
        day_match = re.search(r"(\d+)\s*(?:-| )?days?", g)
        if day_match:
            duration_days = min(14, max(1, int(day_match.group(1))))

        # Detect destination
        dest = "Destination"
        dest_tips = []
        if "goa" in g:
            dest = "Goa"
            if not budget:
                budget = 20000.0 if currency == "INR" else 250.0
            phases_data = [
                {
                    "phase_name": "Day 1: North Goa Beaches & Vibrant Nightlife",
                    "description": "Check-in, rent a scooter, visit popular beaches, and experience beach shack dining.",
                    "tasks": [
                        {"title": "Check-in at Calangute/Anjuna & Rent a Scooter", "details": "Settle into your stay; rent a standard 110cc scooter (approx ₹400-500/day) with fuel.", "hours": "2 hrs", "weight": 0.35},
                        {"title": "Afternoon at Baga & Vagator Beach", "details": "Explore Chapora Fort (Dil Chahta Hai viewpoint) and relax at Vagator cliffs.", "hours": "4 hrs", "weight": 0.15},
                        {"title": "Sunset & Dinner at a Beach Shack", "details": "Fresh Goan fish curry and mocktails at Curlies or Shiva Valley at Anjuna beach.", "hours": "3 hrs", "weight": 0.50}
                    ]
                },
                {
                    "phase_name": "Day 2: Water Sports & Old Goa Heritage",
                    "description": "Morning adventure activities followed by historic Latin quarters and basilicas.",
                    "tasks": [
                        {"title": "Water Sports at Calangute or Sinquerim", "details": "Parasailing, jet ski, and banana boat combo ride booked through verified local vendors.", "hours": "3 hrs", "weight": 0.45},
                        {"title": "Visit Basilica of Bom Jesus & Se Cathedral", "details": "Explore UNESCO World Heritage sites in Old Goa; admire Portuguese colonial architecture.", "hours": "3 hrs", "weight": 0.15},
                        {"title": "Walk through Fontainhas (Latin Quarter) & Cafe Dining", "details": "Stroll through colorful Portuguese villas in Panjim; try traditional bebinca at a heritage cafe.", "hours": "3 hrs", "weight": 0.40}
                    ]
                },
                {
                    "phase_name": "Day 3: South Goa Serenity, Mandovi Cruise & Departure",
                    "description": "Peaceful white sand beaches, souvenir shopping, and return transit.",
                    "tasks": [
                        {"title": "Visit Palolem or Colva Beach in South Goa", "details": "Enjoy quiet, pristine coastline with kayaking in calm backwaters.", "hours": "4 hrs", "weight": 0.40},
                        {"title": "Panjim Market for Cashews, Feni & Souvenirs", "details": "Purchase local spiced cashews, handicrafts, and Goan spices at Municipal Market.", "hours": "2 hrs", "weight": 0.30},
                        {"title": "Return Scooter & Transfer to Dabolim/MOPA Airport", "details": "Pre-book shared cab or Kadamba electric bus transfer to airport.", "hours": "2 hrs", "weight": 0.30}
                    ]
                }
            ]
            dest_tips = [
                "Rent scooters near your hotel and always wear a helmet to avoid high traffic police fines.",
                "Opt for Kadamba AC electric shuttle buses from MOPA/Dabolim airport to Panjim/Calangute to save ₹1,500+ on taxi fares.",
                "Negotiate water sports packages together as a combo rather than individual rides."
            ]

        elif "tokyo" in g or "japan" in g:
            dest = "Tokyo"
            if not budget:
                budget = 200000.0 if currency == "JPY" else 1500.0
            phases_data = [
                {
                    "phase_name": "Phase 1: Modern Tokyo (Shibuya, Shinjuku & Harajuku)",
                    "description": "Iconic crossings, neon cityscapes, and contemporary culture.",
                    "tasks": [
                        {"title": "Arrive & Activate Suica Card / Tokyo Metro Pass", "details": "Collect digital Suica on iPhone/Android; take Skyliner or Narita Express to hotel.", "hours": "3 hrs", "weight": 0.35},
                        {"title": "Shibuya Crossing, Hachiko & Shibuya Sky Observation", "details": "Walk the world's busiest intersection and view the skyline from Shibuya Sky rooftop.", "hours": "4 hrs", "weight": 0.35},
                        {"title": "Dinner in Shinjuku Omoide Yokocho (Memory Lane)", "details": "Authentic yakitori skewers and draft beer in historic lantern-lit alleyways.", "hours": "2.5 hrs", "weight": 0.30}
                    ]
                },
                {
                    "phase_name": "Phase 2: Historic Culture & Akihabara Tech District",
                    "description": "Ancient shrines, street food, and anime/gaming subculture.",
                    "tasks": [
                        {"title": "Senso-ji Temple & Nakamise Street in Asakusa", "details": "Visit Tokyo's oldest temple; sample melonpan and freshly made matcha dorayaki.", "hours": "3.5 hrs", "weight": 0.25},
                        {"title": "Akihabara Electric Town & Mandarake Exploration", "details": "Browse multi-floor retro gaming stores, arcades, and electronic specialty shops.", "hours": "4 hrs", "weight": 0.35},
                        {"title": "Authentic Ichiran or Afuri Yuzu Ramen Dinner", "details": "Experience individual booth dining with rich tonkotsu or refreshing yuzu ramen.", "hours": "2 hrs", "weight": 0.40}
                    ]
                },
                {
                    "phase_name": "Phase 3: Digital Art, Ginza Shopping & Departure",
                    "description": "Immersive digital museums, upscale markets, and departure preparation.",
                    "tasks": [
                        {"title": "teamLab Planets Immersive Digital Art Museum", "details": "Wade through water exhibitions and kaleidoscopic digital flower projections (reserve online in advance).", "hours": "3 hrs", "weight": 0.45},
                        {"title": "Ginza Shopping & Tsukiji Outer Market Street Food", "details": "Try fresh wagyu beef skewers, tamagoyaki egg omelet, and sea urchin at outer market stalls.", "hours": "3 hrs", "weight": 0.35},
                        {"title": "Airport Express Train & Duty Free Souvenirs", "details": "Purchase Tokyo Banana and Royce nama chocolates at Haneda/Narita duty-free.", "hours": "2.5 hrs", "weight": 0.20}
                    ]
                }
            ]
            dest_tips = [
                "Carry at least 15,000-20,000 JPY in cash, as many authentic ramen shops and shrines only take cash.",
                "Book teamLab Planets and Shibuya Sky tickets 2-3 weeks in advance as time slots sell out quickly.",
                "Use 7-Eleven ATMs (Seven Bank) for zero-fee foreign card cash withdrawals."
            ]

        else:
            # Generic destination with custom extracted name
            dest_words = [w.capitalize() for w in goal.split() if w.lower() not in ["plan", "a", "trip", "to", "and", "with", "budget", "of", "in", "the", "for", "day", "days"]]
            dest = " ".join(dest_words[:2]) if dest_words else "Travel Journey"
            if not budget:
                budget = 1500.0 if currency == "USD" else (100000.0 if currency == "INR" else 1200.0)
            phases_data = [
                {
                    "phase_name": "Phase 1: Transit, Arrival & Neighborhood Orientation",
                    "description": "Airport transfers, hotel check-in, connectivity, and evening orientation walk.",
                    "tasks": [
                        {"title": f"Arrive at {dest} & Check-in at Accommodation", "details": "Settle into verified lodging near central metro/transit lines.", "hours": "3 hrs", "weight": 0.40},
                        {"title": "Acquire Local Transit Pass & Digital eSIM", "details": "Setup seamless data connectivity and unlimited city transit card.", "hours": "1.5 hrs", "weight": 0.20},
                        {"title": "Evening Welcome Walking Tour & Local Dinner", "details": f"Stroll through historic town center of {dest}; dine at an authentic neighborhood bistro.", "hours": "3 hrs", "weight": 0.40}
                    ]
                },
                {
                    "phase_name": "Phase 2: Iconic Landmarks & Cultural Immersion",
                    "description": "Primary architectural sights, museums, and local cuisine.",
                    "tasks": [
                        {"title": f"Visit Top Historic Sights & Heritage Monuments in {dest}", "details": "Explore priority monuments with pre-booked skip-the-line tickets.", "hours": "4.5 hrs", "weight": 0.45},
                        {"title": "Cultural Market & Street Culinary Exploration", "details": "Sample famous regional street delicacies and artisan markets.", "hours": "3 hrs", "weight": 0.35},
                        {"title": "Scenic Sunset Viewpoint & Evening Entertainment", "details": "Watch the sunset from the best panoramic observation deck or hilltop terrace.", "hours": "2.5 hrs", "weight": 0.20}
                    ]
                },
                {
                    "phase_name": "Phase 3: Hidden Gems, Souvenirs & Departure Readiness",
                    "description": "Offbeat neighborhoods, artisanal shopping, and smooth departure.",
                    "tasks": [
                        {"title": "Explore Local Artisan Quarter & Botanical Gardens", "details": "Discover quiet alleys, craft boutiques, and scenic green spaces.", "hours": "3.5 hrs", "weight": 0.35},
                        {"title": "Procure Authentic Regional Crafts & Souvenirs", "details": "Shop for indigenous spices, textiles, or confectioneries.", "hours": "2 hrs", "weight": 0.35},
                        {"title": "Check-out & Terminal Transfer", "details": "Pack luggage, verify flight/train gate info, and take express transfer.", "hours": "2 hrs", "weight": 0.30}
                    ]
                }
            ]
            dest_tips = [
                "Book major museum and attraction tickets online at least 5 days prior to avoid multi-hour queues.",
                "Keep digital offline copies of hotel addresses and emergency embassy contacts on your phone.",
                "Use credit cards that charge 0% foreign transaction markup fees."
            ]

        return cls._format_structured_output(
            title=f"{duration_days}-Day Trip Plan for {dest}",
            summary=f"A complete, customized {duration_days}-day itinerary for {dest} optimized for seamless transit, iconic sightseeing, authentic cuisine, and zero wasted time, strictly maintained within your {CurrencyConverter.format(budget, currency)} budget.",
            target_budget=budget,
            currency=currency,
            phases_data=phases_data,
            duration_summary=f"{duration_days} Days",
            tips=dest_tips,
            cost_cats=[
                {"category": "Lodging & Accommodations", "pct": 40},
                {"category": "Food & Dining", "pct": 25},
                {"category": "Attractions & Activities", "pct": 20},
                {"category": "Local Transit & Passes", "pct": 15}
            ]
        )

    @classmethod
    def _plan_business(cls, goal: str, budget: Optional[float], currency: str) -> Dict[str, Any]:
        """Specific business, shop, or cafe launch plan."""
        g = goal.lower()
        biz_name = "Bakery / Cafe" if ("bakery" in g or "cafe" in g or "coffee" in g) else "New Business Venture"
        if not budget:
            budget = 300000.0 if currency == "INR" else 5000.0

        phases_data = [
            {
                "phase_name": "Phase 1: Legal Registration, Licensing & Location Scouting",
                "description": "Regulatory permits, commercial space selection, and lease lock.",
                "tasks": [
                    {"title": "Business Registration, Tax ID (GST/LLC) & Food Safety Permit (FSSAI)", "details": "Formalize business entity, register for local commercial municipal trade license and food safety compliance.", "hours": "12 hrs", "weight": 0.25},
                    {"title": "Location Scouting & High-Footfall Commercial Lease Lock", "details": "Evaluate target catchment demographics, visibility, parking, water/power supply, and negotiate rental terms.", "hours": "18 hrs", "weight": 0.55},
                    {"title": "Open Commercial Bank Account & POS Payment Terminals", "details": "Establish corporate current account and integrate QR/card payment terminals (PayTM/Stripe/Square).", "hours": "6 hrs", "weight": 0.20}
                ]
            },
            {
                "phase_name": "Phase 2: Equipment Procurement, Interior Fitout & Supplier Tie-ups",
                "description": "Essential machinery, furniture, initial inventory, and vendor terms.",
                "tasks": [
                    {"title": "Procure Core Commercial Equipment & Counter Setup", "details": "Order commercial espresso machine/convection ovens, stainless steel tables, display counters, and refrigeration.", "hours": "20 hrs", "weight": 0.50},
                    {"title": "Interior Aesthetics, Lighting & Warm Ambient Seating", "details": "Execute minimalist, clean brand interior, warm 2700K lighting, menu board displays, and ergonomic seating.", "hours": "24 hrs", "weight": 0.30},
                    {"title": "Wholesale Raw Material Sourcing & Packaging Supplies", "details": "Lock direct suppliers for premium coffee beans, dairy, packaging boxes, cups, and branded napkins.", "hours": "10 hrs", "weight": 0.20}
                ]
            },
            {
                "phase_name": "Phase 3: Staff Training, Soft Launch & Marketing Blitz",
                "description": "Recipe standardization, trial operations, neighborhood buzz, and official opening.",
                "tasks": [
                    {"title": "Barista/Kitchen Staff Training & Menu Recipe Standardization", "details": "Train team on standard brewing ratios, hygiene protocols, order turnaround times, and POS billing.", "hours": "14 hrs", "weight": 0.30},
                    {"title": "Run 3-Day Invitation-Only Friends & Family Soft Launch", "details": "Stress-test billing, kitchen speed, and gather constructive feedback on taste and service quality.", "hours": "12 hrs", "weight": 0.30},
                    {"title": "Grand Launch Event, Google Maps Optimization & Influencer Campaign", "details": "Verify Google Business profile, distribute opening flyers, launch targeted Instagram Reels, and offer buy-1-get-1 launch promo.", "hours": "16 hrs", "weight": 0.40}
                ]
            }
        ]

        tips = [
            "Keep menu compact (under 15 items) during the first 60 days to prevent inventory waste and ensure fast order fulfillment.",
            "Verify Google Business Profile on day 1 with photos of high-quality interior shots to capture local neighborhood search traffic.",
            "Maintain at least 15% of your total budget strictly as an emergency working capital reserve for the first 3 months."
        ]

        return cls._format_structured_output(
            title=f"{biz_name} Step-by-Step Launch Blueprint",
            summary=f"A practical roadmap to launch your {biz_name}, covering legal permits, location setup, equipment sourcing, and launch marketing while strictly adhering to your {CurrencyConverter.format(budget, currency)} budget ceiling.",
            target_budget=budget,
            currency=currency,
            phases_data=phases_data,
            duration_summary="4 to 6 Weeks",
            tips=tips,
            cost_cats=[
                {"category": "Equipment & Machinery", "pct": 40},
                {"category": "Deposit & Interior Fitout", "pct": 30},
                {"category": "Initial Inventory & Packaging", "pct": 18},
                {"category": "Licensing & Grand Launch Ads", "pct": 12}
            ]
        )

    @classmethod
    def _plan_software(cls, goal: str, budget: Optional[float], currency: str) -> Dict[str, Any]:
        """Software, MVP, or tech project plan."""
        if not budget:
            budget = 3500.0 if currency == "USD" else 250000.0

        phases_data = [
            {
                "phase_name": "Phase 1: Architecture, Wireframes & Database Schema",
                "description": "Defining core user journeys, data relations, and cloud foundations.",
                "tasks": [
                    {"title": "Create Clickable Figma UI Wireframes & User Journey", "details": "Design onboarding, main dashboard, and core transactional screens; validate with 5 target users.", "hours": "8 hrs", "weight": 0.30},
                    {"title": "Design PostgreSQL / Supabase Schema & Auth Flow", "details": "Draft normalized tables, row-level security (RLS) policies, and OAuth login (Google/Email).", "hours": "6 hrs", "weight": 0.35},
                    {"title": "Setup Git Monorepo, Next.js / FastAPI Boilerplate & CI/CD", "details": "Initialize linting, environment variables, Tailwind / modern CSS, and automated Vercel deployment.", "hours": "5 hrs", "weight": 0.35}
                ]
            },
            {
                "phase_name": "Phase 2: Core Feature Implementation & Integrations",
                "description": "Building the primary value workflow, payment integration, and responsive UI.",
                "tasks": [
                    {"title": "Develop Core MVP Business Logic & API Endpoints", "details": "Implement the single most critical workflow that solves the user's primary problem end-to-end.", "hours": "20 hrs", "weight": 0.45},
                    {"title": "Integrate Stripe / Razorpay Subscription Billing", "details": "Implement checkout webhooks, tiered pricing tables, customer portal, and invoice receipts.", "hours": "8 hrs", "weight": 0.30},
                    {"title": "Build Sleek, Gemini-Grade Responsive User Interface", "details": "Ensure smooth responsive layout, error feedback toasts, and accessible states.", "hours": "14 hrs", "weight": 0.25}
                ]
            },
            {
                "phase_name": "Phase 3: QA, Security Audit, Landing Page & Production Launch",
                "description": "Bug testing, analytics setup, Product Hunt launch, and user acquisition.",
                "tasks": [
                    {"title": "Perform End-to-End Testing & Vulnerability Audit", "details": "Test authentication edge cases, payment failure handling, input sanitation, and mobile responsive checks.", "hours": "8 hrs", "weight": 0.30},
                    {"title": "Deploy High-Converting SEO Landing Page & PostHog Analytics", "details": "Write benefit-driven copy, setup customer testimonial blocks, custom domain SSL, and conversion tracking.", "hours": "7 hrs", "weight": 0.30},
                    {"title": "Launch on Product Hunt, Hacker News & Target Communities", "details": "Prepare promotional demo video, submit showcase post, and engage in comments to onboard first 50 active users.", "hours": "8 hrs", "weight": 0.40}
                ]
            }
        ]

        tips = [
            "Cut scope ruthlessly: Launch with only 1 signature feature done exceptionally well rather than 5 half-baked features.",
            "Use Supabase / Firebase free tiers for database and auth to keep infrastructure costs near $0 until revenue is proven.",
            "Setup PostHog or GA4 session recordings from day 1 to watch where early users drop off."
        ]

        return cls._format_structured_output(
            title="SaaS MVP Architecture & Launch Plan",
            summary=f"A targeted, engineer-vetted roadmap to architect, build, and deploy your software MVP in under 3 weeks within your {CurrencyConverter.format(budget, currency)} budget.",
            target_budget=budget,
            currency=currency,
            phases_data=phases_data,
            duration_summary="2 to 3 Weeks",
            tips=tips,
            cost_cats=[
                {"category": "Fullstack Engineering", "pct": 55},
                {"category": "UI/UX & Product Design", "pct": 20},
                {"category": "Cloud Infrastructure & Auth", "pct": 15},
                {"category": "Domain & Launch Marketing", "pct": 10}
            ]
        )

    @classmethod
    def _plan_event(cls, goal: str, budget: Optional[float], currency: str) -> Dict[str, Any]:
        """Event, wedding, or conference planning."""
        if not budget:
            budget = 300000.0 if currency == "INR" else 4000.0

        phases_data = [
            {
                "phase_name": "Phase 1: Date, Venue Selection & Budget Lock",
                "description": "Selecting dates, inspecting venues, and confirming contracts.",
                "tasks": [
                    {"title": "Finalize Guest Count & Evaluate 3 Shortlisted Venues", "details": "Inspect parking, acoustic setup, air conditioning, and emergency exits; negotiate rental package.", "hours": "10 hrs", "weight": 0.50},
                    {"title": "Launch RSVP & Ticketing Registration Portal", "details": "Setup online registration with dietary preferences, QR check-in badges, and email confirmations.", "hours": "6 hrs", "weight": 0.20},
                    {"title": "Contract Professional Audio/Visual & Stage Production", "details": "Lock high-grade wireless mics, dual projectors/LED screen, stage lighting, and sound engineer.", "hours": "6 hrs", "weight": 0.30}
                ]
            },
            {
                "phase_name": "Phase 2: Catering, Speakers & Vendor Coordination",
                "description": "Menu tasting, schedule alignment, and promotional assets.",
                "tasks": [
                    {"title": "Catering Tasting & Menu Finalization", "details": "Select welcome drinks, live counters, main buffet course, and dessert options accommodating dietary needs.", "hours": "8 hrs", "weight": 0.45},
                    {"title": "Confirm Keynote Speakers / Entertainers & Run-Sheet", "details": "Lock slide presentations, speaker travel logistics, and minute-by-minute stage schedule.", "hours": "8 hrs", "weight": 0.30},
                    {"title": "Print Lanyards, Standees & Directional Signage", "details": "Design and print high-quality guest badges, sponsor backdrop, and directional floor banners.", "hours": "6 hrs", "weight": 0.25}
                ]
            },
            {
                "phase_name": "Phase 3: Technical Rehearsal & Day-of Production",
                "description": "Dry run, live crowd coordination, and wrap-up.",
                "tasks": [
                    {"title": "Conduct Stage Dry Run & Mic Checks 24h Prior", "details": "Test presentation slides, clickers, audio levels, and volunteer check-in desk drills.", "hours": "5 hrs", "weight": 0.25},
                    {"title": "Live Event Orchestration & Backstage Management", "details": "Manage guest registration flow, speaker cues, catering service timing, and photo/video coverage.", "hours": "10 hrs", "weight": 0.45},
                    {"title": "Post-Event Wrap, Vendor Settlements & Thank You Emails", "details": "Distribute session recordings, collect feedback survey, and settle remaining vendor balances.", "hours": "4 hrs", "weight": 0.30}
                ]
            }
        ]

        tips = [
            "Order catering for 90% of confirmed RSVPs to prevent massive food wastage and cost overruns.",
            "Have 1 dedicated point-of-contact with full authority to resolve day-of vendor questions.",
            "Always test AV and laptop display adapters in the venue at least one day before guests arrive."
        ]

        return cls._format_structured_output(
            title="Event Production & Execution Blueprint",
            summary=f"A complete logistical playbook to organize and execute a memorable event on schedule, maintaining zero vendor disputes within your {CurrencyConverter.format(budget, currency)} budget.",
            target_budget=budget,
            currency=currency,
            phases_data=phases_data,
            duration_summary="3 to 4 Weeks",
            tips=tips,
            cost_cats=[
                {"category": "Venue & Security", "pct": 40},
                {"category": "Catering & Refreshments", "pct": 30},
                {"category": "Audio/Visual & Lighting", "pct": 20},
                {"category": "Branding & Guest Badges", "pct": 10}
            ]
        )

    @classmethod
    def _plan_general(cls, goal: str, budget: Optional[float], currency: str) -> Dict[str, Any]:
        """Versatile, intelligent plan for any general goal, study plan, or routine."""
        if not budget:
            budget = 1000.0 if currency == "USD" else 50000.0

        # Extract keywords
        clean_goal = re.sub(r"(?i)\b(plan|a|an|the|with|budget|of|in|for)\b", "", goal).strip()
        subject = clean_goal.capitalize() if clean_goal else "Custom Goal"

        phases_data = [
            {
                "phase_name": "Phase 1: Foundation, Resource Setup & Baseline Audit",
                "description": f"Gathering tools, auditing current benchmarks, and setting clear KPIs for '{subject}'.",
                "tasks": [
                    {"title": f"Define Key Deliverables & Success Metrics for {subject}", "details": "Establish measurable milestones, non-negotiable standards, and baseline deadlines.", "hours": "4 hrs", "weight": 0.30},
                    {"title": "Procure Essential Equipment, Materials & Study Resources", "details": "Acquire top-rated reference books, digital tools, software subscriptions, or materials.", "hours": "4 hrs", "weight": 0.40},
                    {"title": "Design a Weekly Execution Calendar & Habit Triggers", "details": "Block dedicated non-negotiable calendar slots and remove common environmental distractions.", "hours": "2 hrs", "weight": 0.30}
                ]
            },
            {
                "phase_name": "Phase 2: Deep Implementation & Structured Practice",
                "description": "Executing core workstreams with progressive milestone reviews.",
                "tasks": [
                    {"title": f"Execute Core Sprint 1 (Fundamental Concepts / First Half of {subject})", "details": "Complete high-priority modules and document practical summaries.", "hours": "14 hrs", "weight": 0.40},
                    {"title": f"Execute Core Sprint 2 (Advanced Application & Practical Drills)", "details": "Work through complex case studies, real-world mock tests, or physical prototypes.", "hours": "16 hrs", "weight": 0.40},
                    {"title": "Midway Assessment & Weak Spot Remediation", "details": "Analyze errors, re-evaluate difficult areas, and refine techniques before final stretch.", "hours": "6 hrs", "weight": 0.20}
                ]
            },
            {
                "phase_name": "Phase 3: Final Polish, Mock Evaluation & Delivery",
                "description": "Comprehensive simulation, quality review, and final execution.",
                "tasks": [
                    {"title": "Conduct Full-Scale Simulated Run / Mock Assessment", "details": "Simulate exact real-world conditions with strict timing to test readiness.", "hours": "6 hrs", "weight": 0.40},
                    {"title": "Incorporate Final Refinements & Eliminate Bottlenecks", "details": "Make precision tweaks based on mock results for flawless delivery.", "hours": "4 hrs", "weight": 0.35},
                    {"title": "Final Milestone Completion & Post-Review", "details": "Achieve final deliverable, archive documentation, and evaluate progress against goals.", "hours": "3 hrs", "weight": 0.25}
                ]
            }
        ]

        tips = [
            "Break long study/work sessions into 50-minute focused blocks with 10-minute active breaks (Pomodoro).",
            "Keep daily logs of progress; consistency beats erratic cramming every single time.",
            "Review your weakest areas first thing in the morning when mental energy is at its peak."
        ]

        return cls._format_structured_output(
            title=f"Structured Action Plan: {subject}",
            summary=f"A targeted, milestone-driven execution plan for '{goal}' designed to maximize momentum, track progress, and deliver measurable results within your {CurrencyConverter.format(budget, currency)} budget.",
            target_budget=budget,
            currency=currency,
            phases_data=phases_data,
            duration_summary="3 to 4 Weeks",
            tips=tips,
            cost_cats=[
                {"category": "Core Tools & Study Materials", "pct": 45},
                {"category": "Expert Consult / Practice Tests", "pct": 30},
                {"category": "Productivity & Workspace Setup", "pct": 25}
            ]
        )

    @classmethod
    def _format_structured_output(
        cls,
        title: str,
        summary: str,
        target_budget: float,
        currency: str,
        phases_data: List[Dict[str, Any]],
        duration_summary: str,
        tips: List[str],
        cost_cats: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculates contingency reserve, balances costs, and formats cleanly."""
        currency = CurrencyConverter.normalize_currency_code(currency)
        contingency_reserve = round(target_budget * 0.12, 2)
        deployable_budget = target_budget - contingency_reserve

        # Format phases
        phases = []
        phase_count = len(phases_data)
        equal_weight = 1.0 / phase_count

        task_counter = 1
        for p_idx, p_raw in enumerate(phases_data):
            p_budget = round(deployable_budget * equal_weight, 2)
            tasks = []
            for t_raw in p_raw["tasks"]:
                t_cost = round(p_budget * float(t_raw.get("weight", 0.33)), 2)
                tasks.append({
                    "id": f"T{task_counter:02d}",
                    "title": t_raw["title"],
                    "details": t_raw["details"],
                    "estimated_cost": t_cost,
                    "duration": t_raw.get("hours", "3 hrs"),
                    "priority": "High" if t_raw.get("weight", 0) > 0.35 else "Medium"
                })
                task_counter += 1

            phases.append({
                "phase_name": p_raw["phase_name"],
                "description": p_raw["description"],
                "phase_budget": p_budget,
                "tasks": tasks
            })

        # Cost breakdown
        breakdown = []
        for cat in cost_cats:
            amt = round(deployable_budget * (cat["pct"] / 100.0), 2)
            breakdown.append({
                "category": cat["category"],
                "amount": amt,
                "percentage": cat["pct"]
            })

        return {
            "title": title,
            "summary": summary,
            "target_budget": round(target_budget, 2),
            "currency": currency,
            "contingency_reserve": contingency_reserve,
            "allocated_cost": round(deployable_budget, 2),
            "duration_summary": duration_summary,
            "phases": phases,
            "cost_breakdown": breakdown,
            "key_tips": tips,
            "generated_by": "Gemini Task Planner Agent"
        }
