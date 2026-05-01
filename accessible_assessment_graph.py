import json
import os
import sqlite3
from typing import List, Optional, TypedDict

from langgraph.graph import StateGraph, END
from openai import OpenAI

from app.services.accessible_prompts import (
    ACCESSIBLE_QUESTION_GENERATOR_PROMPT,
    ACCESSIBLE_TECHNICAL_EVALUATOR_PROMPT,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ── State ─────────────────────────────────────────────────────────────────────

class AccessibleAssessmentState(TypedDict):
    candidate_id:         str
    job_id:               int
    resume_text:          str
    job_description:      str
    match_score:          float
    assessment_questions: List[dict]
    assessment_answers:   List[dict]
    technical_score:      Optional[int]
    reasoning_summary:    Optional[str]
    current_step:         str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_fences(raw: str) -> str:
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    return raw.strip()


# ── Node: accessible question generator ──────────────────────────────────────

def accessible_question_generator_node(state: AccessibleAssessmentState) -> dict:
    match_score   = state.get("match_score", 50)
    num_questions = 7 if match_score >= 70 else 5

    prompt = ACCESSIBLE_QUESTION_GENERATOR_PROMPT.format(
        resume_text=state.get("resume_text", "")[:3000],
        job_description=state.get("job_description", ""),
        match_score=match_score,
        num_questions=num_questions,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    parsed    = json.loads(_strip_fences(response.choices[0].message.content))
    questions = parsed.get("questions", [])
    return {"assessment_questions": questions, "current_step": "written_test"}


# ── Node: accessible technical evaluator ─────────────────────────────────────

def accessible_technical_evaluator_node(state: AccessibleAssessmentState) -> dict:
    questions = state.get("assessment_questions", [])
    answers   = state.get("assessment_answers", [])

    qa_block = ""
    for q in questions:
        qid = q["id"]
        ans = next(
            (a["answer"] for a in answers if a["question_id"] == qid),
            "No answer provided",
        )
        qa_block += f"\nQ{qid} [{q['type'].upper()}]: {q['question']}\n"
        if q["type"] == "mcq":
            qa_block += f"Options: {', '.join(q.get('options', []))}\n"
            qa_block += f"Correct:  {q.get('correct_answer', 'N/A')}\n"
        qa_block += f"Candidate answer: {ans}\n"

    prompt = ACCESSIBLE_TECHNICAL_EVALUATOR_PROMPT.format(
        job_description=state.get("job_description", ""),
        qa_block=qa_block,
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    result = json.loads(_strip_fences(response.choices[0].message.content))
    return {
        "technical_score":   result.get("technical_score", 0),
        "reasoning_summary": result.get("reasoning_summary", ""),
        "current_step":      "complete",
    }


# ── Graph assembly ────────────────────────────────────────────────────────────

def _make_accessible_checkpointer():
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        conn = sqlite3.connect(
            "./assessment_checkpoints_accessible.db",
            check_same_thread=False,
        )
        return SqliteSaver(conn)
    except Exception:
        from langgraph.checkpoint.memory import MemorySaver
        return MemorySaver()


def _build_accessible_graph(checkpointer):
    workflow = StateGraph(AccessibleAssessmentState)
    workflow.add_node("question_generator",  accessible_question_generator_node)
    workflow.add_node("technical_evaluator", accessible_technical_evaluator_node)
    workflow.set_entry_point("question_generator")
    workflow.add_edge("question_generator",  "technical_evaluator")
    workflow.add_edge("technical_evaluator", END)
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_after=["question_generator"],
    )


_checkpointer            = _make_accessible_checkpointer()
accessible_assessment_app = _build_accessible_graph(_checkpointer)
