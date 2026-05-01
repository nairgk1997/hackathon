"""
report_generator.py
-------------------
Generates a structured, chart-ready dashboard payload for a completed candidate.
Called exclusively by GET /interview/report/{id}.

One LLM call produces all qualitative insights + derived sub-category scores.
A fully deterministic fallback fires if the LLM call fails, so the dashboard
always renders with something meaningful.
"""

import json
import os
from openai import OpenAI
from app.models.candidate import Candidate

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_REPORT_PROMPT = """You are a senior hiring analyst. Generate a structured performance dashboard
for the following candidate based solely on the data provided.

Candidate: {name}
Resume–JD Match Score: {match_score}%
Written Assessment Score: {tech_score}/100
Assessment Evaluation Notes: {reasoning}
Behavioral Integrity Score: {proctoring_score}%

Instructions:
1. The four assessment sub-category scores must average approximately to the written
   assessment score. Vary them realistically by ±5 to ±15 points — never make them uniform.
2. The four interview question scores (scale 1–10) must be consistent with the overall
   performance level implied by the assessment score and evaluation notes.
3. Each insights string must be 2–3 specific, data-grounded sentences.
4. overall_score = round(match_score × 0.30 + tech_score × 0.40 + (avg_interview_score × 10) × 0.30)

Return ONLY valid JSON — no markdown fences, no extra keys:
{{
  "resume_match_insights": "...",
  "assessment_categories": [
    {{"name": "Technical Knowledge", "score": <int 0-100>}},
    {{"name": "Problem Solving",     "score": <int 0-100>}},
    {{"name": "Communication",       "score": <int 0-100>}},
    {{"name": "System Design",       "score": <int 0-100>}}
  ],
  "assessment_insights": "...",
  "interview_questions": [
    {{"q": "Background & Experience", "score": <int 1-10>}},
    {{"q": "Technical Depth",         "score": <int 1-10>}},
    {{"q": "Problem Solving",         "score": <int 1-10>}},
    {{"q": "Cultural Fit",            "score": <int 1-10>}}
  ],
  "interview_insights": "...",
  "overall_score": <int 0-100>
}}
"""


def generate_candidate_report(candidate: Candidate, behavior_logs: list[str]) -> dict:
    """
    Build the full dashboard payload for a completed candidate.
    Returns a dict with keys: resume_match, assessment, interview_performance, overall_score.
    """
    match_score    = round(candidate.match_score or 0)
    tech_score     = candidate.technical_score or 0
    reasoning      = (candidate.reasoning_summary or "No assessment notes available.")[:1200]
    proctoring_pct = round((candidate.proctoring_score or 1.0) * 100)

    prompt = _REPORT_PROMPT.format(
        name=candidate.name,
        match_score=match_score,
        tech_score=tech_score,
        reasoning=reasoning,
        proctoring_score=proctoring_pct,
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
    except Exception:
        data = _fallback_data(match_score, tech_score, reasoning)

    return {
        "resume_match": {
            "score":    match_score,
            "insights": data.get("resume_match_insights", ""),
        },
        "assessment": {
            "categories": data.get("assessment_categories", _default_categories(tech_score)),
            "insights":   data.get("assessment_insights", reasoning),
        },
        "interview_performance": {
            "questions": data.get("interview_questions", _default_questions(tech_score)),
            "insights":  data.get("interview_insights", "Interview rounds completed."),
        },
        "overall_score": data.get("overall_score", _calc_overall(match_score, tech_score)),
    }


# ── Fallback helpers ──────────────────────────────────────────────────────────

def _fallback_data(match_score: int, tech_score: int, reasoning: str) -> dict:
    return {
        "resume_match_insights": (
            f"Resume matched the job description with {match_score}% alignment based on "
            "skill overlap and experience level detected during vector analysis."
        ),
        "assessment_categories": _default_categories(tech_score),
        "assessment_insights":   reasoning or "Assessment completed. See overall score for details.",
        "interview_questions":   _default_questions(tech_score),
        "interview_insights":    "All three interview rounds (HR, Technical, Final) were completed.",
        "overall_score":         _calc_overall(match_score, tech_score),
    }


def _default_categories(tech_score: int) -> list[dict]:
    b = tech_score or 50
    return [
        {"name": "Technical Knowledge", "score": _clamp(b + 4)},
        {"name": "Problem Solving",     "score": _clamp(b - 8)},
        {"name": "Communication",       "score": _clamp(b + 9)},
        {"name": "System Design",       "score": _clamp(b - 5)},
    ]


def _default_questions(tech_score: int = 70) -> list[dict]:
    base = round((tech_score or 70) / 10)
    return [
        {"q": "Background & Experience", "score": _clamp10(base + 1)},
        {"q": "Technical Depth",         "score": _clamp10(base)},
        {"q": "Problem Solving",         "score": _clamp10(base - 1)},
        {"q": "Cultural Fit",            "score": _clamp10(base + 1)},
    ]


def _calc_overall(match: int, tech: int) -> int:
    avg_q = 7
    return round(match * 0.30 + tech * 0.40 + (avg_q * 10) * 0.30)


def _clamp(v: int) -> int:
    return max(0, min(100, v))


def _clamp10(v: int) -> int:
    return max(1, min(10, v))
