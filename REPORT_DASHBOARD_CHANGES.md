# Candidate Report Dashboard — Change Log

## Overview

The candidate interview report has been upgraded from a flat text modal into a
four-widget interactive metrics dashboard powered by **Recharts**. The upgrade is
fully backward-compatible — no existing endpoints were removed or their signatures
changed; only one new field (`dashboard`) was added to the existing report response.

---

## Files Created

| File | Layer | Purpose |
|------|-------|---------|
| `backend/app/services/report_generator.py` | Service | Single LLM call generates all structured chart data (category scores, question scores, insights). Fully deterministic fallback fires on LLM failure so the dashboard always renders. |
| `frontend-react/src/components/CandidateReportDashboard.jsx` | Frontend | Four-widget Recharts dashboard modal (Donut · Bar · Radar · Overall). Per-widget "View Insights" toggle. Replaces the old flat `InterviewReportModal`. |
| `REPORT_DASHBOARD_CHANGES.md` | Docs | This file. |

---

## Files Modified

| File | Change | Lines touched |
|------|--------|---------------|
| `backend/app/api/interview.py` | Import `generate_candidate_report`; add `_dashboards` in-memory cache; append `"dashboard"` key to `GET /interview/report/{id}` response | ~8 |
| `frontend-react/src/pages/Candidates.jsx` | Import `CandidateReportDashboard`; replace `<InterviewReportModal>` with `<CandidateReportDashboard>` | 2 |
| `frontend-react/package.json` | `recharts` added as a runtime dependency via `npm install recharts` | 1 |

> The old `InterviewReportModal` component defined inside `Candidates.jsx` was intentionally left in place (unused) to avoid any risk of breaking the file.

---

## New API Response Schema

`GET /interview/report/{candidate_id}` now returns:

```jsonc
{
  // ── Existing fields (unchanged) ──────────────────────────────────────
  "candidate_id":     1,
  "name":             "Vinay Kumar",
  "interview_status": "Interview_Complete",
  "ai_summary":       "• Strong communication style…",
  "proctoring_logs":  ["[sid=1 turn=2] No anomalies detected.", "…"],
  "proctoring_score": 0.95,
  "recommendation":   { "verdict": "Hire", "reason": "Solid technical depth…" },

  // ── New field ────────────────────────────────────────────────────────
  "dashboard": {
    "resume_match": {
      "score":    85,               // candidate.match_score from DB (integer %)
      "insights": "Strong alignment in Python and FastAPI. AWS experience missing."
    },
    "assessment": {
      "categories": [
        { "name": "Technical Knowledge", "score": 82 },
        { "name": "Problem Solving",     "score": 74 },
        { "name": "Communication",       "score": 88 },
        { "name": "System Design",       "score": 70 }
      ],
      "insights": "Candidate excelled in communication but showed gaps in system design."
    },
    "interview_performance": {
      "questions": [
        { "q": "Background & Experience", "score": 9 },
        { "q": "Technical Depth",         "score": 8 },
        { "q": "Problem Solving",         "score": 7 },
        { "q": "Cultural Fit",            "score": 9 }
      ],
      "insights": "Excellent articulation. Slight hesitation on distributed systems questions."
    },
    "overall_score": 81
  }
}
```

### Score derivation

| Field | Source |
|-------|--------|
| `resume_match.score` | `candidate.match_score` (DB column) — never fabricated |
| `assessment.categories[*].score` | LLM-derived; must average ≈ `candidate.technical_score`; vary ±5–15 pts |
| `interview_performance.questions[*].score` | LLM-derived; consistent with overall performance level; scale 1–10 |
| `overall_score` | `match × 0.30 + tech × 0.40 + (avg_q × 10) × 0.30` |

---

## Dashboard Widgets

| Widget | Chart type | Data source |
|--------|-----------|-------------|
| Resume Match Score | Donut (`PieChart`) | `dashboard.resume_match` |
| Assessment Results | Horizontal Bar (`BarChart`) | `dashboard.assessment.categories` |
| Interview Q&A Performance | Radar (`RadarChart`) | `dashboard.interview_performance.questions` |
| Overall Evaluation | Numeric ring + hire verdict | `dashboard.overall_score` + `recommendation` |
| Behavioral Analysis Logs | Text list (below grid) | `proctoring_logs` |

Every widget has a **"View Insights"** toggle button that expands a qualitative text panel specific to that section.

---

## Running / Testing

### 1. Install the new npm dependency

```bash
cd frontend-react
npm install recharts
```

> Already done. Verify it appears in `package.json` under `dependencies`.

### 2. Start both servers

```bash
# Terminal 1 — backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend-react
npm run dev
```

### 3. Test the dashboard

1. Log in as HR (`admin` / `admin123`).
2. Navigate to **Candidates**.
3. Find any candidate whose **Interview Status** is `Interview_Complete`.
4. Click **View Report** — the new dashboard modal opens.
5. Verify four widgets render with charts.
6. Click **View Insights** on any widget to expand the text panel.

### 4. Test the API directly

```bash
curl http://localhost:8000/interview/report/<candidate_id>
```

Confirm the response contains a `"dashboard"` key with the structure documented above.

---

## Architecture Notes

- **No existing logic was rewritten.** `assessment_graph.py`, `llm_evaluator.py`, `interview_manager.py`, and all other service files are untouched.
- **`report_generator.py`** is the only new backend file. It is called exclusively from `interview.py` and has no side effects.
- **Caching**: `_dashboards[candidate_id]` (in-memory dict in `interview.py`) prevents repeated LLM calls on each modal open — identical pattern to the existing `_recommendations` cache.
- **Fallback safety**: If the LLM call in `report_generator.py` fails for any reason, `_fallback_data()` returns deterministic values derived from `candidate.match_score` and `candidate.technical_score`, so the dashboard always renders.
