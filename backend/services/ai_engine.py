"""
SalesAI V2.0 — AI Analysis Engine
Gemini (primary) → Groq (fallback) → Rule Engine (offline fallback)
Maintains conversation context to prevent repeated questions.
Universal: Works across ALL industries — retail, real estate, insurance, finance, services, etc.
"""

import json
import logging
from typing import Optional

from google import genai
from groq import Groq

from config import settings

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SALES EXPERT SYSTEM PROMPT — Shared by Gemini & Groq
# Universal across ALL industries and domains.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SALES_EXPERT_PROMPT = """You are an EXPERT SALES & BUSINESS ADVISOR with 15+ years of experience across EVERY industry. You are a master at understanding customer needs and guiding sales professionals, agents, and service providers to close deals while keeping the customer genuinely satisfied.

## YOUR DOMAIN EXPERTISE (you adapt to whatever the conversation is about):

### Retail & Electronics:
- Consumer electronics: smartphones, laptops, TVs, appliances, cameras, audio, wearables
- Brands: Samsung, Apple, Sony, LG, OnePlus, Xiaomi, Dell, HP, Bosch, Whirlpool, etc.
- Features, specifications, pricing tiers, EMI, exchange offers

### Real Estate & Property:
- Residential: apartments, flats, villas, plots, houses, PG accommodations
- Commercial: offices, shops, showrooms, warehouses
- Factors: location, carpet area, amenities, RERA registration, builder reputation, loan eligibility, ROI

### Insurance & Financial Services (LIC, etc.):
- Life insurance, health insurance, vehicle insurance, term plans, endowment plans
- Premium calculation, claim process, maturity benefits, nominee details, riders
- Mutual funds, SIPs, fixed deposits, PPF, NPS

### Stock Market & Investments:
- Equities, mutual funds, bonds, ETFs, IPOs, derivatives
- Risk profiling, portfolio diversification, return expectations, investment horizon
- Demat accounts, brokerage, tax implications (LTCG, STCG)

### Groceries & FMCG:
- Daily essentials, branded vs unbranded, bulk buying, organic options
- Price comparison, quantity packs, subscription offers, seasonal availability

### Automotive:
- Cars, bikes, scooters — new and used
- Fuel type, mileage, service costs, resale value, financing, test drives

### Services:
- Salon, spa, fitness, travel, education, legal, healthcare, home services
- Packages, subscriptions, memberships, appointments, service quality

### B2B Sales:
- Software, SaaS, machinery, raw materials, wholesale
- Contracts, MOQ, payment terms, delivery schedules, after-sales support

## YOUR SALES STRATEGY:
1. **Listen First**: Understand what the customer actually needs before recommending anything.
2. **Ask Smart Questions**: Each question should uncover useful info — budget, preferences, timeline, requirements, past experience, specific concerns.
3. **One Topic at a Time**: If the customer has multiple needs, focus on one at a time. Finish one before moving to the next.
4. **Be Honest & Grounded**: NEVER make up facts, fabricate features, invent product connections, or claim things that aren't true.
5. **Win-Win Approach**: Recommend what genuinely matches the customer's needs AND fits their budget/expectations. The goal is customer satisfaction AND profit.
6. **Build Trust**: Be warm, professional, and knowledgeable. Speak like an expert who genuinely cares.
7. **Progress Toward Closing**: Each suggestion should move the conversation closer to a decision. Don't loop.
8. **Adapt to the Domain**: Automatically detect the industry/domain from the conversation and tailor your language, questions, and suggestions accordingly.

## CRITICAL RULES:
- NEVER repeat a question that was already asked or answered in the conversation history.
- NEVER invent connections between unrelated products or services.
- NEVER fabricate specifications, features, prices, interest rates, or any factual information.
- Treat each product/service as a SEPARATE discussion with its own requirements.
- Keep your suggested question SHORT and NATURAL — like a real professional talking face-to-face.
- If a customer mentions a budget or constraint, respect it. Don't push things outside their range.
- If a customer gives a short answer like "yes" or "okay", ask a relevant follow-up on the NEXT logical topic.
- Match the industry's language — say "premium" for insurance, "carpet area" for real estate, "mileage" for cars, "RAM" for phones, etc."""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Rule-Based Fallback Engine (Universal)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def legacy_rule_engine(text: str) -> dict:
    """Offline fallback if both APIs fail. Covers all industries."""
    text_l = text.lower()
    intent = "General Inquiry"
    sugg = "How can I help you today?"
    entities = []

    # ─── Intent Detection ───
    if any(w in text_l for w in ["price", "cost", "much", "expensive", "cheap", "budget", "premium", "emi", "rate"]):
        intent = "Pricing"
        sugg = "Could you share your budget range so I can suggest the best options?"
        entities.append({"entity": "Topic", "value": "Price"})
    elif any(w in text_l for w in ["buy", "want", "need", "purchase", "looking for", "interested", "book", "invest"]):
        intent = "Purchase"
        sugg = "Great! Could you tell me more about what exactly you're looking for?"
    elif any(w in text_l for w in ["problem", "issue", "broken", "not working", "complaint", "delay", "refund"]):
        intent = "Complaint"
        sugg = "I'm sorry to hear that. Could you describe the issue in detail so I can help?"
    elif any(w in text_l for w in ["feature", "spec", "compare", "difference", "better", "vs"]):
        intent = "Comparison"
        sugg = "What are the key factors you're comparing? Budget, features, or brand?"
    elif any(w in text_l for w in ["hello", "hi", "hey", "good morning", "good evening"]):
        intent = "Greeting"
        sugg = "Welcome! What brings you in today? How can I assist you?"
    elif any(w in text_l for w in ["thank", "bye", "okay", "fine", "done", "that's all"]):
        intent = "Closing"
        sugg = "Thank you! Is there anything else I can help you with?"

    # ─── Universal Entity Extraction ───
    # Brands (Electronics)
    electronics_brands = ["samsung", "apple", "iphone", "google", "pixel", "oneplus", "sony", "lg",
                          "xiaomi", "realme", "oppo", "vivo", "dell", "hp", "lenovo", "asus", "bosch", "whirlpool"]
    # Products (Electronics)
    electronics_products = ["phone", "laptop", "tablet", "watch", "earbuds", "tv", "camera",
                           "microwave", "refrigerator", "washing machine", "ac", "air conditioner"]
    # Real Estate
    real_estate = ["flat", "apartment", "villa", "plot", "house", "property", "bhk", "office", "shop"]
    # Insurance / Finance
    finance = ["insurance", "lic", "policy", "mutual fund", "sip", "fd", "fixed deposit",
               "term plan", "health plan", "premium", "claim", "stock", "share", "investment",
               "demat", "portfolio", "ipo", "bond"]
    # Automotive
    automotive = ["car", "bike", "scooter", "suv", "sedan", "hatchback"]
    # Services
    services = ["salon", "spa", "gym", "fitness", "travel", "hotel", "flight", "course", "tuition"]

    for brand in electronics_brands:
        if brand in text_l:
            entities.append({"entity": "Brand", "value": brand.capitalize()})

    for product in electronics_products:
        if product in text_l:
            entities.append({"entity": "Product", "value": product.capitalize()})

    for item in real_estate:
        if item in text_l:
            entities.append({"entity": "Property", "value": item.capitalize()})

    for item in finance:
        if item in text_l:
            entities.append({"entity": "Financial Product", "value": item.capitalize()})

    for item in automotive:
        if item in text_l:
            entities.append({"entity": "Vehicle", "value": item.capitalize()})

    for item in services:
        if item in text_l:
            entities.append({"entity": "Service", "value": item.capitalize()})

    return {
        "sentiment": {"label": "Neutral", "score": 0.5},
        "intent": {"label": intent, "score": 1.0},
        "entities": entities,
        "suggestion": sugg,
        "reasoning": "Rule-based fallback (API keys not configured or API error).",
        "engine_used": "rule_engine"
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Build User Prompt with Conversation History
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _build_analysis_prompt(text: str, history: list[dict]) -> str:
    """Build a user prompt that includes conversation history."""

    history_block = ""
    if history:
        history_lines = []
        for entry in history[-10:]:
            history_lines.append(f"  Customer: \"{entry.get('text', '')}\"")
            if entry.get("suggestion"):
                history_lines.append(f"  Agent suggested: \"{entry['suggestion']}\"")
        history_block = "CONVERSATION SO FAR:\n" + "\n".join(history_lines) + "\n\n"

    return f"""{history_block}LATEST CUSTOMER MESSAGE: "{text}"

Analyze the customer's message and suggest the best next question for the sales agent / service provider.

Return ONLY valid JSON in this exact format:
{{
    "sentiment": {{ "label": "Positive/Neutral/Negative", "score": 0.0 to 1.0 }},
    "intent": {{ "label": "Buy/Inquire/Complain/Compare/Budget/Negotiate/Greet/Confirm/Invest/Book", "score": 0.0 to 1.0 }},
    "entities": [ {{ "entity": "Brand/Product/Budget/Feature/Location/Service/Property/Policy/Vehicle", "value": "Extracted Value" }} ],
    "suggestion": "Your suggested next question for the sales agent (short, natural, practical, domain-appropriate)",
    "reasoning": "Brief 1-2 sentence strategy explanation"
}}"""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Gemini Analysis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_with_gemini(text: str, history: list[dict]) -> Optional[dict]:
    """Analyze with Google Gemini 2.5 Flash (primary engine)."""
    if not settings.GEMINI_API_KEY:
        logger.warning("Gemini API key not configured")
        return None

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Combine system prompt + user prompt for Gemini
        full_prompt = SALES_EXPERT_PROMPT + "\n\n---\n\n" + _build_analysis_prompt(text, history)

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=full_prompt,
        )

        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        data["engine_used"] = "gemini"
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Groq Analysis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_with_groq(text: str, history: list[dict]) -> Optional[dict]:
    """Analyze with Groq Llama 3.3 (secondary engine)."""
    if not settings.GROQ_API_KEY:
        logger.warning("Groq API key not configured")
        return None

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)

        user_prompt = _build_analysis_prompt(text, history)

        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SALES_EXPERT_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        data = json.loads(completion.choices[0].message.content)
        data["engine_used"] = "groq"
        return data

    except json.JSONDecodeError as e:
        logger.error(f"Groq returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Unified Dispatcher
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze(text: str, history: list[dict] | None = None, speed_first: bool = False, preferred_engine: str = "auto") -> dict:
    """
    Analyze customer text with cascading fallback.
    preferred_engine='gemini': Gemini first → Groq fallback → Rule Engine
    preferred_engine='groq':   Groq first → Gemini fallback → Rule Engine
    preferred_engine='auto':   Uses speed_first flag to decide order
    """
    if history is None:
        history = []

    # Determine engine order based on preference
    if preferred_engine == "gemini":
        primary, secondary = analyze_with_gemini, analyze_with_groq
    elif preferred_engine == "groq":
        primary, secondary = analyze_with_groq, analyze_with_gemini
    elif speed_first:
        primary, secondary = analyze_with_groq, analyze_with_gemini
    else:
        primary, secondary = analyze_with_gemini, analyze_with_groq

    result = primary(text, history)
    if result:
        return result

    result = secondary(text, history)
    if result:
        return result

    # Final fallback: rule engine
    logger.info("Both APIs failed, using rule-based fallback")
    return legacy_rule_engine(text)



