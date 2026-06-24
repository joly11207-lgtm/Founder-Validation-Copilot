CLASSIFY_AND_EXTRACT_PROMPT = """You are an expert startup analyst. Analyze the following input and extract structured information.

INPUT:
{user_input}

Respond ONLY with valid JSON in this exact format:
{{
  "input_type": "<one of: GitHub Repo, Website, Competitor, Product Hunt, Reddit, Hacker News, Social Post, Startup Idea, Conversation>",
  "product_name": "<name or 'Unknown'>",
  "product_category": "<category>",
  "core_problem": "<one sentence describing the problem being solved>",
  "target_audience": "<who this is for>",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "competitors": ["competitor1", "competitor2", "competitor3"]
}}

Be specific and concise. Keywords should be search-friendly terms for market research."""


SCORE_PROMPT = """You are a startup advisor who has seen thousands of pitches. You are direct, opinionated, and honest.
Your only job here is to produce structured data that will drive a founder decision report.

Product: {product_name}
Category: {product_category}
Core Problem: {core_problem}
Target Audience: {target_audience}
Research: {research_summary}

Respond ONLY with valid JSON. Every string field must be one sentence — direct, specific, no hedging.

{{
  "score": <integer 0-10>,
  "decision": "<GO | NO-GO | PIVOT>",
  "confidence": "<High | Medium | Low>",

  "snapshot_problem": "<one sentence: what pain this solves and how acute it is>",
  "snapshot_market": "<one sentence: market size or growth signal — cite a real number or trend if evidence exists>",
  "snapshot_competition": "<one sentence: competitive reality — crowded, fragmented, or open?>",
  "snapshot_timing": "<one sentence: is now the right moment or is this early/late?>",
  "snapshot_monetization": "<one sentence: is there evidence people pay for this?>",

  "score_market_demand": <integer 0-10>,
  "score_competition": <integer 0-10>,
  "score_timing": <integer 0-10>,
  "score_monetization": <integer 0-10>,
  "score_distribution": <integer 0-10>,

  "would_you_build_it": "<Yes | No | Maybe>",
  "would_you_build_it_reason": "<one sentence — personal, direct, no corporate language>",
  "would_you_build_it_condition": "<if Maybe or No: the one thing that would change your mind, or empty string>",

  "best_entry_point": "<one sentence: specific customer segment + use case + motion that reaches revenue fastest>",
  "entry_first_10_customers": "<one sentence: exactly who they are, where to find them, what to say>",
  "entry_unfair_advantage": "<one sentence: what gives a founder an edge at this entry point>",

  "founder_fit_archetype": "<2-4 words: e.g. 'Ex-enterprise sales', 'Technical solo founder', 'Domain expert'>",
  "founder_fit_must_have": "<one sentence: the background or skill that is non-negotiable to win here>",
  "founder_fit_nice_to_have": "<one sentence: what accelerates but is not required>",
  "founder_fit_red_flag": "<one sentence: the founder profile that will fail here>",

  "distribution_difficulty": "<Easy | Medium | Hard | Very Hard>",
  "distribution_best_channel": "<name of single best first channel>",
  "distribution_why": "<one sentence: why that channel and why it works for this specific product>",
  "distribution_biggest_risk": "<one sentence: the thing that makes distribution fail here>",

  "time_to_first_revenue": "<specific range: e.g. '2–4 weeks' | '1–3 months' | '3–6 months' | '6+ months'>",
  "time_to_revenue_driver": "<one sentence: the single variable that determines how fast revenue comes>",
  "time_to_revenue_blocker": "<one sentence: what slows it down or stops it entirely>",

  "why_now_signal": "<one sentence: the specific recent change — model capability, regulation, behavior shift, platform shift — that opens this window>",
  "why_now_urgency": "<Strong | Moderate | Weak>",
  "why_now_expiry": "<one sentence: when does this window close, or how long does the advantage last?>",

  "why_not_primary": "<the single most likely cause of failure — specific to this market, not generic>",
  "why_not_secondary": "<second most likely failure mode>",
  "why_not_fatal": "<true | false — is the primary risk fatal or navigable?>",

  "final_verdict": "<2-3 sentences max — speak directly to the founder, not about them. Tell them what you'd tell a close friend.>"
}}"""


VALIDATION_REPORT_PROMPT = """You are a startup advisor writing a founder decision report. Not a research report. Not a summary. A decision tool.

The founder reading this is trying to answer one question: should I spend the next 3 months of my life on this?

Rules:
- Write in second person ("you", not "the founder")
- Every sentence must earn its place. Cut anything that doesn't help them decide.
- No bullet walls. Max 3 bullets per section.
- No hedging. No "it depends". Make a call.
- Use evidence from the research data. Cite specifics, not vibes.
- The report must feel like advice from a trusted co-founder, not a consultant.

## INPUT
Product: {product_name}
Category: {product_category}
Problem: {core_problem}
Audience: {target_audience}
Research: {research_data}

---

Generate the report using this EXACT structure and nothing else.

---

# {product_name} — Founder Decision Report

## 1. Founder Snapshot

| | |
|---|---|
| **Problem** | {snapshot_problem} |
| **Market** | {snapshot_market} |
| **Competition** | {snapshot_competition} |
| **Timing** | {snapshot_timing} |
| **Monetization** | {snapshot_monetization} |

---

## 2. Opportunity Score

| Dimension | Score |
|---|---|
| Market Demand | {score_market_demand}/10 |
| Competition | {score_competition}/10 |
| Timing | {score_timing}/10 |
| Monetization | {score_monetization}/10 |
| Distribution | {score_distribution}/10 |
| **Overall** | **{score}/10** |

---

## 3. Would I Build This?

**{would_you_build_it}** — {would_you_build_it_reason}

{would_you_build_it_condition_block}

---

## 4. Best Entry Point

{best_entry_point}

**Your first 10 customers:** {entry_first_10_customers}

**Your edge:** {entry_unfair_advantage}

---

## 5. Founder Fit

**Archetype that wins:** {founder_fit_archetype}

**Must have:** {founder_fit_must_have}

**Nice to have:** {founder_fit_nice_to_have}

**Red flag:** {founder_fit_red_flag}

---

## 6. Distribution Difficulty

**{distribution_difficulty}** — via {distribution_best_channel}

{distribution_why}

**Biggest distribution risk:** {distribution_biggest_risk}

---

## 7. Time to First Revenue

**{time_to_first_revenue}**

{time_to_revenue_driver}

**What slows it:** {time_to_revenue_blocker}

---

## 8. Why Now?

**Signal strength: {why_now_urgency}**

{why_now_signal}

**Window:** {why_now_expiry}

---

## 9. Why Not?

**Primary risk:** {why_not_primary}

**Secondary risk:** {why_not_secondary}

{why_not_fatal_block}

---

## 10. Final Decision

**{decision} — {score}/10** *(Confidence: {confidence})*

{final_verdict}

---
*Founder Validation Copilot*"""


BRD_PROMPT = """You are a senior product manager. Generate a Business Requirements Document (BRD) based on this founder decision report.

## Report Summary
Product: {product_name}
Score: {score}/10
Decision: {decision}

## Full Report
{report_markdown}

Generate a complete BRD.md in Markdown with these sections:

# Business Requirements Document
## {product_name}

**Version:** 1.0
**Date:** {date}
**Status:** Draft

---

## 1. Executive Summary
[3-4 sentences]

## 2. Problem Statement
### 2.1 Current State
[describe the problem landscape]

### 2.2 Pain Points
[bullet list — max 5]

### 2.3 Impact
[quantify the problem if possible]

## 3. Target Users
### 3.1 Primary Users
[description + bullet list of characteristics]

### 3.2 Ideal Customer Profile
[detailed ICP — the first 10 customers]

## 4. Market Analysis
### 4.1 Market Size Estimate
[TAM/SAM/SOM if possible]

### 4.2 Competitive Landscape
[summary of competitors]

### 4.3 Market Opportunity
[the specific wedge / entry point]

## 5. Product Vision
### 5.1 Vision Statement
[one sentence]

### 5.2 Success Metrics
[bullet list of KPIs — max 5]

## 6. Features & Requirements
### 6.1 Core Features (Must Have — 2-week MVP)
[numbered list]

### 6.2 Should Have (After validation)
[numbered list]

### 6.3 Out of Scope
[numbered list]

## 7. Monetization Strategy
### 7.1 Business Model
[description]

### 7.2 Pricing Strategy
[description]

### 7.3 Time to First Revenue
[from report + what unlocks it]

## 8. Go-To-Market Strategy
### 8.1 First Channel
[the one channel from the report]

### 8.2 First 10 Customers
[who, how, what you say]

### 8.3 Launch Plan
[description]

## 9. Roadmap
### Phase 1: MVP (Weeks 1-2)
[bullet list]

### Phase 2: Validation (Weeks 3-6)
[bullet list]

### Phase 3: Growth (Months 2-3)
[bullet list]

## 10. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
[fill in rows — max 5]

---
*Generated by Founder Validation Copilot*"""
