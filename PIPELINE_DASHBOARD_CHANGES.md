# Overall Pipeline View — Change Log

## Overview

A new **Overall Pipeline View** has been added to the HR admin portal. It provides a
real-time bird's-eye view of the hiring funnel across all open roles — summary KPI
cards, a stacked bar chart per role, and a per-role breakdown table with average scores.

This feature is **purely additive**: no existing endpoint, model, component, or route
was removed or had its signature changed.

---

## Files Created

| File | Layer | Purpose |
|------|-------|---------|
| `backend/app/services/dashboard_service.py` | Service | Pure aggregation — DB queries + math, no FastAPI concerns. Returns summary, stage distribution, and per-job stats. |
| `backend/app/api/pipeline.py` | Router | Single `GET /pipeline/stats` endpoint. Delegates 100% to the service. |
| `frontend-react/src/pages/PipelineDashboard.jsx` | Frontend | Summary cards · stacked BarChart · per-job table with colored stage badges and score pills. |
| `PIPELINE_DASHBOARD_CHANGES.md` | Docs | This file. |

---

## Files Modified

| File | Change |
|------|--------|
| `backend/app/main.py` | Import `pipeline` router; register at prefix `/pipeline` |
| `frontend-react/src/App.jsx` | Import `PipelineDashboard`; add `/pipeline` route inside the `PrivateRoute` Layout |
| `frontend-react/src/components/Sidebar.jsx` | Import `BarChart2` from lucide-react; add Pipeline nav item |

---

## New API Endpoint

### `GET /pipeline/stats`

No authentication header required beyond the existing CORS policy (mirrors other HR routes).

```jsonc
{
  "summary": {
    "total_jobs":        4,
    "total_candidates":  31,
    "total_shortlisted": 18,   // cumulative: shortlisted + assessed + interviewing + completed
    "total_assessed":    12,   // cumulative: assessed + interviewing + completed
    "total_interviewed": 7,    // cumulative: interviewing + completed
    "total_completed":   3
  },
  "stage_distribution": [
    { "stage": "Applied",      "count": 13, "color": "#38bdf8" },
    { "stage": "Shortlisted",  "count": 6,  "color": "#3b82f6" },
    { "stage": "Assessed",     "count": 5,  "color": "#8b5cf6" },
    { "stage": "Interviewing", "count": 4,  "color": "#f59e0b" },
    { "stage": "Completed",    "count": 3,  "color": "#10b981" },
    { "stage": "Rejected",     "count": 0,  "color": "#f87171" }
  ],
  "jobs": [
    {
      "job_id":           1,
      "title":            "Backend Engineer",
      "experience_level": "Mid",
      "required_skills":  ["Python", "FastAPI", "PostgreSQL"],
      "total_candidates": 10,
      "stages": {
        "applied": 3, "shortlisted": 2, "assessed": 2,
        "interviewing": 2, "completed": 1, "rejected": 0
      },
      "avg_match_score": 74.2,
      "avg_tech_score":  68.5
    }
  ]
}
```

### Stage classification logic (`dashboard_service._pipeline_stage`)

| Priority | Condition | Stage |
|----------|-----------|-------|
| 1 | `candidate.status == "Rejected"` | `rejected` |
| 2 | `interview_status == "Interview_Complete"` | `completed` |
| 3 | `interview_status in ("Screening_Done", "Tech_Done")` | `interviewing` |
| 4 | `candidate.status == "Assessed"` | `assessed` |
| 5 | `candidate.status == "Shortlisted"` | `shortlisted` |
| 6 | _(default)_ | `applied` |

---

## Dashboard Widgets

| Widget | Type | Data source |
|--------|------|-------------|
| Summary KPI cards (6) | Stat cards | `summary.*` |
| Candidates by Stage & Role | Stacked `BarChart` (Recharts) | `jobs[*].stages` |
| Per-Role Breakdown | HTML table | `jobs[*]` |

### Stage colors

| Stage | Color |
|-------|-------|
| Applied | `#38bdf8` |
| Shortlisted | `#3b82f6` |
| Assessed | `#8b5cf6` |
| Interviewing | `#f59e0b` |
| Completed | `#10b981` |
| Rejected | `#f87171` |

---

## Running / Testing

### 1. Start both servers

```bash
# Terminal 1 — backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend-react
npm run dev
```

### 2. Test the page

1. Log in as HR (`admin` / `admin123`).
2. Click **Pipeline** in the left sidebar (expands on hover).
3. Verify six summary KPI cards render at the top.
4. Verify the stacked bar chart shows one bar group per job.
5. Verify the per-role table shows stage counts as colored badges.

### 3. Test the API directly

```bash
curl http://localhost:8000/pipeline/stats
```

Confirm the response contains `summary`, `stage_distribution`, and `jobs` arrays.

---

## Architecture Notes

- **No existing logic was touched.** `assessment.py`, `interview.py`, `candidates.py`,
  and all other routers are untouched.
- **`dashboard_service.py`** is the only new backend service file. It is called
  exclusively from `pipeline.py` and has no side effects.
- **Recharts** was already installed as a dependency (added during the Candidate Report
  Dashboard task) — no new `npm install` is required.
- **Sidebar nav** is filtered with `isAdmin` — the Pipeline item only appears for
  `hr_manager` role users, consistent with the three existing nav items.
