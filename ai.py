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
    # Strip markdown code fences if present
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
    system = "You are an expert startup analyst. Always respond with valid JSON only."
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

    decision = score_data.get("decision", "NO-GO")
    score = score_data.get("score", 0)
    decision_line = {
        "GO": f"Score {score}/10 — This is worth building.",
        "NO-GO": f"Score {score}/10 — Don't build this.",
        "PIVOT": f"Score {score}/10 — The idea needs a different angle.",
    }.get(decision, f"Score {score}/10")

    features = "\n".join(f"- {f}" for f in score_data.get("mvp_features", []))
    mvp_section = f"""**Build this:**
{features}

**Scope:** {score_data.get('mvp_scope', '')}

**Launch channel:** {score_data.get('mvp_launch_channel', '')}"""

    prompt = VALIDATION_REPORT_PROMPT.format(
        product_name=product_name,
        product_category=product_category,
        core_problem=core_problem,
        target_audience=target_audience,
        keywords=", ".join(keywords),
        research_data=research_data,
        score=score,
        decision=decision,
        decision_line=decision_line,
        confidence=score_data.get("confidence", "Low"),
        why_now=score_data.get("why_now", ""),
        why_now_strength=score_data.get("why_now_strength", "Moderate"),
        why_this_market=score_data.get("why_this_market", ""),
        why_not=score_data.get("why_not", ""),
        best_entry_point=score_data.get("best_entry_point", ""),
        founder_fit_note=score_data.get("founder_fit_note", ""),
        distribution_difficulty=score_data.get("distribution_difficulty", "Medium"),
        distribution_note=score_data.get("distribution_note", ""),
        mvp_launch_channel=score_data.get("mvp_launch_channel", ""),
        time_to_first_revenue=score_data.get("time_to_first_revenue", ""),
        time_to_revenue_note=score_data.get("time_to_revenue_note", ""),
        would_you_build_it=score_data.get("would_you_build_it", "Maybe"),
        would_you_build_it_reason=score_data.get("would_you_build_it_reason", ""),
        mvp_section=mvp_section,
    )
    return chat("You are a brutally honest startup advisor helping a founder make a go/no-go decision.", prompt, temperature=0.4)


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
