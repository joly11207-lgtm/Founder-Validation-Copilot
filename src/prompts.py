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


SCORE_PROMPT = """You are a brutally honest startup advisor with pattern recognition across thousands of companies.

Product: {product_name}
Category: {product_category}
Core Problem: {core_problem}
Target Audience: {target_audience}
Research Summary: {research_summary}

Respond ONLY with valid JSON:
{{
  "score": <integer 0-10>,
  "decision": "<GO | NO-GO | PIVOT>",
  "confidence": "<High | Medium | Low>",
  "would_you_build_it": "<Yes | No | Maybe>",
  "would_you_build_it_reason": "<one direct sentence — no hedging>",
  "why_now": "<one sentence: what changed recently that makes this viable now>",
  "why_now_strength": "<Strong | Moderate | Weak>",
  "why_this_market": "<one sentence: the single best reason this market is worth entering>",
  "why_not": "<the single biggest reason NOT to build this — be specific, not generic>",
  "best_entry_point": "<one sentence: the most defensible, fastest-to-revenue wedge>",
  "founder_fit_note": "<one sentence: what kind of founder wins here and why>",
  "distribution_difficulty": "<Easy | Medium | Hard | Very Hard>",
  "distribution_note": "<one sentence on why>",
  "time_to_first_revenue": "<e.g. 2-4 weeks | 1-3 months | 6+ months>",
  "time_to_revenue_note": "<one sentence on what drives that timeline>",
  "mvp_features": ["feature1", "feature2", "feature3"],
  "mvp_scope": "<one sentence: what you actually build in 2 weeks>",
  "mvp_launch_channel": "<the single best launch channel for first 100 users>"
}}"""


VALIDATION_REPORT_PROMPT = """You are a brutally honest startup advisor. Your job is not to summarize research — it is to help a founder decide whether to spend the next 2 years of their life on this.

Be direct. Be specific. Use evidence from the research. No hedging. No filler sentences. No "it depends."

Every section should feel like advice from a trusted co-founder who has seen this exact market before.

## CONTEXT
Product: {product_name}
Category: {product_category}
Problem: {core_problem}
Audience: {target_audience}
Keywords: {keywords}

## RESEARCH DATA
{research_data}

## SCORING
Score: {score}/10
Decision: {decision}
Confidence: {confidence}

---

Generate the founder decision report using this EXACT structure. Write in plain, direct English. No corporate language. No bullet-point walls. Max 3 bullets per section where bullets are used.

---

# {product_name}

**{decision_line}**

---

## ⏰ Why Now?
*What has changed recently that makes this the right moment — or why timing is working against you.*

{why_now}

**Timing signal:** {why_now_strength}

---

## 📈 Why This Market?
*The single most compelling reason this market is worth a founder's time.*

{why_this_market}

---

## ⚠️ Why Not?
*The real reason this might fail. Not generic risk. The specific thing that kills companies in this space.*

{why_not}

---

## 🎯 Best Entry Point
*The wedge. The specific customer, use case, and motion that gets you to revenue fastest with the least competition.*

{best_entry_point}

**First 10 customers:** [Who exactly, how to reach them, what you say]

---

## 🧠 Founder Fit
*What kind of founder wins here. What unfair advantages matter. What background is table stakes.*

{founder_fit_note}

**Ask yourself:** [One honest question the founder needs to answer about themselves]

---

## 📣 Distribution Difficulty
**{distribution_difficulty}**

{distribution_note}

**Best first channel:** {mvp_launch_channel}

---

## 💵 Time to Revenue
**{time_to_first_revenue}**

{time_to_revenue_note}

**What unlocks it:** [The one thing that has to be true before someone pays]

---

## 🤔 Would You Build It?
**{would_you_build_it}** — {would_you_build_it_reason}

---

## 🏗️ If You GO: Build This in 2 Weeks

{mvp_section}

---

## 🎯 Decision

**Score: {score}/10 — {decision}**
Confidence: {confidence}

[2-3 sentences. Final verdict. Speak directly to the founder. Tell them what you'd tell a friend.]

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
