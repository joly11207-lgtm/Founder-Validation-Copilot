import requests
import streamlit as st
from typing import Optional


def _brave_search(query: str, count: int = 10) -> list[dict]:
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": st.secrets["BRAVE_SEARCH_API_KEY"],
    }
    params = {"q": query, "count": count, "search_lang": "en", "safesearch": "moderate"}
    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers=headers,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("web", {}).get("results", [])
    return [{"title": r.get("title", ""), "url": r.get("url", ""), "description": r.get("description", "")}
            for r in results]


def _format_results(results: list[dict]) -> str:
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r['title']}**")
        lines.append(f"   URL: {r['url']}")
        lines.append(f"   {r['description']}")
        lines.append("")
    return "\n".join(lines)


def research_market(product_name: str, product_category: str, core_problem: str,
                    target_audience: str, keywords: list, competitors: list) -> str:
    queries = [
        f"{product_name} alternatives competitors pricing",
        f"{product_category} market size demand 2024 2025",
        f'"{core_problem}" site:reddit.com OR site:news.ycombinator.com',
        f"{' '.join(keywords[:3])} pain points user complaints",
        f"{product_category} startups funding business model",
    ]
    if competitors:
        queries.append(f"{competitors[0]} pricing revenue business model")

    all_results = {}
    for q in queries:
        try:
            results = _brave_search(q, count=5)
            all_results[q] = results
        except Exception as e:
            all_results[q] = [{"title": "Search failed", "url": "", "description": str(e)}]

    sections = []
    labels = [
        "Competitor & Pricing Research",
        "Market Size & Demand",
        "Community Discussions",
        "User Pain Points",
        "Business Models & Funding",
        "Lead Competitor Details",
    ]
    for i, (query, results) in enumerate(all_results.items()):
        label = labels[i] if i < len(labels) else f"Search {i+1}"
        sections.append(f"### {label}\nQuery: `{query}`\n\n{_format_results(results)}")

    return "\n\n---\n\n".join(sections)
