# Accessible Interview Mode — Implementation Guide

## Overview

This update adds a fully parallel **Accessible Interview Mode** for candidates who rely
on screen readers, refreshable Braille displays, or other assistive technology. The mode
provides a text-to-speech–driven, keyboard-only assessment flow with no time limits and
LLM prompts that never reference visual content.

The implementation is **strictly additive** — no existing business logic was rewritten.
All new functionality lives in dedicated files.

---

## New Files Created

### Backend

| File | Purpose |
|------|---------|
| `backend/app/dao/__init__.py` | Package marker for the new DAO layer |
| `backend/app/dao/candidate_dao.py` | Data-access functions: `get_by_id`, `set_accessibility_mode`, `save_assessment_result` |
| `backend/app/services/accessible_prompts.py` | LLM system prompts for the accessible flow. Rules: no visual references, MCQ options spelled "Option A:", equitable STT evaluation rubric |
| `backend/app/services/accessible_assessment_graph.py` | Separate LangGraph state machine (`accessible_assessment_app`). Uses its own SQLite checkpoint file (`assessment_checkpoints_accessible.db`) and thread-ID prefix `accessible_<id>` to avoid colliding with the standard graph |
| `backend/app/api/accessible_assessment.py` | FastAPI router mounted at `/accessible-assessment`. Exposes: `GET /start`, `POST /submit`, `PATCH /candidates/{id}/accessibility` |

### Frontend

| File | Purpose |
|------|---------|
| `frontend-react/src/pages/AccessibleAssessment.jsx` | Accessible React component. One-question-at-a-time flow, Web Speech API TTS, `AudioRecorder` STT integration, full WAI-ARIA markup, keyboard-only navigation, ARIA live regions for all state changes |

---

## Existing Files Modified

| File | Change | Lines touched |
|------|--------|---------------|
| `backend/app/models/candidate.py` | Added `Boolean` to SQLAlchemy imports; added `accessibility_mode = Column(Boolean, default=False)` to `Candidate` | 2 |
| `backend/app/main.py` | Import and register `accessible_assessment` router at prefix `/accessible-assessment` | 2 |
| `backend/app/api/assessment.py` | Added `accessibility_mode` field to `POST /assessment/login` response | 1 |
| `frontend-react/src/App.jsx` | Import `AccessibleAssessment`; add `/accessible-assessment` route inside `CandidateRoute` | 3 |
| `frontend-react/src/pages/CandidateLogin.jsx` | Destructure `accessibility_mode` from login response; persist to `localStorage` as `candidate_accessibility_mode` | 2 |
| `frontend-react/src/pages/CandidateDashboard.jsx` | "Start" button on the Technical Assessment stage checks `candidate_accessibility_mode` and navigates to `/accessible-assessment` when true | 4 |

---

## How the Accessible Routing Flow Works

```
HR Portal                     Backend                          Candidate Portal
─────────                     ───────                          ────────────────
PATCH /accessible-assessment  sets candidate.accessibility_mode = True
  /candidates/{id}/accessibility                               ↓
                                                    POST /assessment/login
                                                      └─ response includes
                                                         accessibility_mode: true
                                                               ↓
                                                    CandidateLogin.jsx stores
                                                    candidate_accessibility_mode=true
                                                    in localStorage
                                                               ↓
                                                    CandidateDashboard.jsx
                                                    "Start" button on stage 2
                                                    reads flag → navigates to
                                                    /accessible-assessment
                                                               ↓
                                                    AccessibleAssessment.jsx
                                                    GET /accessible-assessment/start
                                                      └─ accessible_assessment_app
                                                         generates audio-safe questions
                                                         (no visuals, no time limit)
                                                               ↓
                                                    TTS reads each question aloud
                                                    Candidate answers by voice (STT)
                                                    or typing
                                                               ↓
                                                    POST /accessible-assessment/submit
                                                      └─ equitable LLM evaluator
                                                         ignores STT artefacts
                                                               ↓
                                                    Score + summary saved to Candidate
                                                    TTS announces result
```

---

## Enabling Accessible Mode for a Candidate (HR Action)

Call the new PATCH endpoint from the HR portal or via curl:

```bash
curl -X PATCH http://localhost:8000/accessible-assessment/candidates/42/accessibility \
     -H "Content-Type: application/json" \
     -d '{"enabled": true}'
```

Response:
```json
{ "message": "Accessibility mode enabled for Vinay Kumar" }
```

The next time that candidate logs in, the flag is returned in the login response and
automatically routes them to the accessible flow — no action required from the candidate.

---

## Key Accessibility Features in `AccessibleAssessment.jsx`

| Feature | Implementation |
|---------|---------------|
| **Auto TTS** | `window.speechSynthesis` reads each question automatically on display; re-read button always available |
| **Voice input (STT)** | Existing `AudioRecorder` component transcribes speech and appends to the answer field |
| **Answer read-back** | "Read my answer aloud" button for self-verification before moving on |
| **ARIA live region** | `role="status" aria-live="polite"` announces loading, navigation, transcription, and results |
| **Keyboard navigation** | Arrow keys (← →) move between questions globally; Tab moves through all controls; Enter/Space activate buttons; native radio group handles MCQ arrow-key selection |
| **Focus management** | Question heading receives programmatic focus on each question change so Tab order starts correctly |
| **Skip link** | "Skip to main content" appears on first Tab press |
| **Progress bar** | `role="progressbar"` with `aria-valuenow/min/max` |
| **Quick-jump strip** | Numbered pill buttons (`aria-current="step"`, answered/unanswered label) for jumping to any question |
| **No time limit** | Backend returns `time_limit_seconds: null`; frontend never renders a countdown |
| **High-contrast focus rings** | `focus:ring-4 focus:ring-sky-400 focus:ring-offset-2` applied to every interactive element |
| **Equitable evaluation** | Separate LLM prompt instructs the evaluator to ignore STT transcription artefacts |

---

## LLM Prompt Guarantees

Both prompts in `accessible_prompts.py` enforce the following for every question:

- No visual references (`"the diagram"`, `"as shown"`, `"click on"`, `"on the left"` etc. are explicitly forbidden)
- MCQ options prefixed `"Option A:"` for natural TTS parsing
- Conceptual/reasoning questions preferred over visual-output tasks
- Evaluator awards partial credit generously and ignores filler words / STT capitalisation errors

---

## Architecture Compliance Notes

- **N-tier**: DB access only via `dao/candidate_dao.py` → service (`accessible_assessment_graph.py`) → API handler (`accessible_assessment.py`). No DB queries in node functions.
- **Additive only**: The standard `assessment_graph.py`, `llm_evaluator.py`, `ai_service.py`, and `interview_manager.py` are untouched.
- **Isolated checkpointer**: The accessible graph uses `assessment_checkpoints_accessible.db` and thread IDs prefixed `accessible_` — zero collision risk with the existing graph.
- **Shared auth**: The accessible API reuses the same JWT secret and algorithm as `assessment.py` but does not import from it, maintaining loose coupling.
