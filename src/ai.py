import json
import re
import requests
import streamlit as st


def _get_headers():
    return {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://founder-validation-copilot.streamlit.app",
        "X-Title": "Founder Validation Copilot",
    }


def _get_model():
    return st.secrets.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")


def chat(system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
    payload = {
        "model": _get_model(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": 4096,
    }
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=_get_headers(),
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def chat_json(system_prompt: str, user_message: str) -> dict:
    raw = chat(system_prompt, user_message, temperature=0.1)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    return json.loads(raw)


def classify_and_extract(user_input: str) -> dict:
    from src.prompts import CLASSIFY_AND_EXTRACT_PROMPT
    system = "You are an expert startup analyst. Always respond with valid JSON only."
    prompt = CLASSIFY_AND_EXTRACT_PROMPT.format(user_input=user_input)
    return chat_json(system, prompt)


def score_opportunity(product_name: str, product_category: str, core_problem: str,
                      target_audience: str, research_summary: str) -> dict:
    from src.prompts import SCORE_PROMPT
    system = "You are a startup advisor. Always respond with valid JSON only. Every string value must be one sentence."
    prompt = SCORE_PROMPT.format(
        product_name=product_name,
        product_category=product_category,
        core_problem=core_problem,
        target_audience=target_audience,
        research_summary=research_summary,
    )
    return chat_json(system, prompt)


def generate_report(input_type: str, product_name: str, product_category: str,
                    core_problem: str, target_audience: str, keywords: list,
                    research_data: str, score_data: dict) -> str:
    from src.prompts import VALIDATION_REPORT_PROMPT

    s = score_data

    # Conditional blocks pre-rendered so the template stays clean
    condition = s.get("would_you_build_it_condition", "")
    would_you_build_it_condition_block = (
        f"*What would change my mind: {condition}*" if condition else ""
    )

    fatal = str(s.get("why_not_fatal", "false")).lower() == "true"
    why_not_fatal_block = (
        "**This risk is likely fatal.** Proceed only if you have a specific plan to neutralise it."
        if fatal else
        "This risk is navigable with the right approach."
    )

    prompt = VALIDATION_REPORT_PROMPT.format(
        product_name=product_name,
        product_category=product_category,
        core_problem=core_problem,
        target_audience=target_audience,
        research_data=research_data,
        score=s.get("score", 0),
        decision=s.get("decision", "NO-GO"),
        confidence=s.get("confidence", "Low"),

        snapshot_problem=s.get("snapshot_problem", ""),
        snapshot_market=s.get("snapshot_market", ""),
        snapshot_competition=s.get("snapshot_competition", ""),
        snapshot_timing=s.get("snapshot_timing", ""),
        snapshot_monetization=s.get("snapshot_monetization", ""),

        score_market_demand=s.get("score_market_demand", 0),
        score_competition=s.get("score_competition", 0),
        score_timing=s.get("score_timing", 0),
        score_monetization=s.get("score_monetization", 0),
        score_distribution=s.get("score_distribution", 0),

        would_you_build_it=s.get("would_you_build_it", "Maybe"),
        would_you_build_it_reason=s.get("would_you_build_it_reason", ""),
        would_you_build_it_condition_block=would_you_build_it_condition_block,

        best_entry_point=s.get("best_entry_point", ""),
        entry_first_10_customers=s.get("entry_first_10_customers", ""),
        entry_unfair_advantage=s.get("entry_unfair_advantage", ""),

        founder_fit_archetype=s.get("founder_fit_archetype", ""),
        founder_fit_must_have=s.get("founder_fit_must_have", ""),
        founder_fit_nice_to_have=s.get("founder_fit_nice_to_have", ""),
        founder_fit_red_flag=s.get("founder_fit_red_flag", ""),

        distribution_difficulty=s.get("distribution_difficulty", "Medium"),
        distribution_best_channel=s.get("distribution_best_channel", ""),
        distribution_why=s.get("distribution_why", ""),
        distribution_biggest_risk=s.get("distribution_biggest_risk", ""),

        time_to_first_revenue=s.get("time_to_first_revenue", ""),
        time_to_revenue_driver=s.get("time_to_revenue_driver", ""),
        time_to_revenue_blocker=s.get("time_to_revenue_blocker", ""),

        why_now_signal=s.get("why_now_signal", ""),
        why_now_urgency=s.get("why_now_urgency", "Moderate"),
        why_now_expiry=s.get("why_now_expiry", ""),

        why_not_primary=s.get("why_not_primary", ""),
        why_not_secondary=s.get("why_not_secondary", ""),
        why_not_fatal_block=why_not_fatal_block,

        final_verdict=s.get("final_verdict", ""),
    )

    return chat(
        "You are a startup advisor writing a founder decision report. Be direct and specific. Write in second person.",
        prompt,
        temperature=0.3,
    )


def generate_brd(product_name: str, product_category: str, core_problem: str,
                 target_audience: str, score: int, decision: str, report_markdown: str) -> str:
    from src.prompts import BRD_PROMPT
    from datetime import datetime
    prompt = BRD_PROMPT.format(
        product_name=product_name,
        product_category=product_category,
        core_problem=core_problem,
        target_audience=target_audience,
        score=score,
        decision=decision,
        report_markdown=report_markdown,
        date=datetime.utcnow().strftime("%Y-%m-%d"),
    )
    return chat("You are a senior product manager writing a BRD.", prompt, temperature=0.3)
