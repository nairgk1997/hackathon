"""
dashboard_service.py
--------------------
Pure data-aggregation layer for the HR Pipeline Dashboard.
No FastAPI or HTTP concerns live here — only DB queries and math.
Called exclusively by backend/app/api/pipeline.py.
"""

from sqlalchemy.orm import Session
from app.models.candidate import Candidate
from app.models.job import Job


# ── Stage classifier ──────────────────────────────────────────────────────────

def _pipeline_stage(c: Candidate) -> str:
    """Map a Candidate's two status fields to a single display stage."""
    if c.status == "Rejected":
        return "rejected"
    if getattr(c, "interview_status", None) == "Interview_Complete":
        return "completed"
    if getattr(c, "interview_status", None) in ("Screening_Done", "Tech_Done"):
        return "interviewing"
    if c.status == "Assessed":
        return "assessed"
    if c.status == "Shortlisted":
        return "shortlisted"
    return "applied"


_STAGE_KEYS = ["applied", "shortlisted", "assessed", "interviewing", "completed", "rejected"]


# ── Main aggregation function ─────────────────────────────────────────────────

def get_pipeline_stats(db: Session) -> dict:
    """
    Returns the full pipeline payload consumed by GET /pipeline/stats.

    Schema:
    {
      "summary": {
        "total_jobs": int,
        "total_candidates": int,
        "total_shortlisted": int,   # shortlisted + further
        "total_assessed": int,      # assessed + further
        "total_interviewed": int,   # interviewing + completed
        "total_completed": int
      },
      "stage_distribution": [
        {"stage": "Applied", "count": int, "color": "#..."},
        ...
      ],
      "jobs": [
        {
          "job_id": int,
          "title": str,
          "experience_level": str,
          "required_skills": list[str],
          "total_candidates": int,
          "stages": {
            "applied": int, "shortlisted": int, "assessed": int,
            "interviewing": int, "completed": int, "rejected": int
          },
          "avg_match_score": float | null,
          "avg_tech_score":  float | null
        },
        ...
      ]
    }
    """
    jobs       = db.query(Job).order_by(Job.id.desc()).all()
    candidates = db.query(Candidate).all()

    # Group candidates by job_id
    by_job: dict[int, list[Candidate]] = {}
    for c in candidates:
        by_job.setdefault(c.job_id, []).append(c)

    # ── Per-job stats ──────────────────────────────────────────────────────────
    job_rows = []
    for job in jobs:
        cands = by_job.get(job.id, [])

        stages: dict[str, int] = {k: 0 for k in _STAGE_KEYS}
        for c in cands:
            stages[_pipeline_stage(c)] += 1

        match_scores = [c.match_score for c in cands if c.match_score is not None]
        tech_scores  = [c.technical_score for c in cands if c.technical_score is not None]

        job_rows.append({
            "job_id":           job.id,
            "title":            job.title or "Untitled Role",
            "experience_level": job.experience_level or "—",
            "required_skills":  job.required_skills or [],
            "total_candidates": len(cands),
            "stages":           stages,
            "avg_match_score":  round(sum(match_scores) / len(match_scores), 1) if match_scores else None,
            "avg_tech_score":   round(sum(tech_scores)  / len(tech_scores),  1) if tech_scores  else None,
        })

    # ── Aggregate totals ───────────────────────────────────────────────────────
    def total(key: str) -> int:
        return sum(row["stages"][key] for row in job_rows)

    t_applied      = total("applied")
    t_shortlisted  = total("shortlisted")
    t_assessed     = total("assessed")
    t_interviewing = total("interviewing")
    t_completed    = total("completed")
    t_rejected     = total("rejected")

    stage_distribution = [
        {"stage": "Applied",      "count": t_applied,      "color": "#38bdf8"},
        {"stage": "Shortlisted",  "count": t_shortlisted,  "color": "#3b82f6"},
        {"stage": "Assessed",     "count": t_assessed,     "color": "#8b5cf6"},
        {"stage": "Interviewing", "count": t_interviewing, "color": "#f59e0b"},
        {"stage": "Completed",    "count": t_completed,    "color": "#10b981"},
        {"stage": "Rejected",     "count": t_rejected,     "color": "#f87171"},
    ]

    return {
        "summary": {
            "total_jobs":        len(jobs),
            "total_candidates":  len(candidates),
            # cumulative: everyone who reached this stage or beyond
            "total_shortlisted": t_shortlisted + t_assessed + t_interviewing + t_completed,
            "total_assessed":    t_assessed + t_interviewing + t_completed,
            "total_interviewed": t_interviewing + t_completed,
            "total_completed":   t_completed,
        },
        "stage_distribution": stage_distribution,
        "jobs":                job_rows,
    }
