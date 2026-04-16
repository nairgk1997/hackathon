import os
import json
import base64
import io
import uuid
import cv2
import threading
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Literal

from flask import Flask, request, jsonify
from openai import OpenAI

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.tools import tool

# ─── APP CONFIGURATION ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "techcorp_india_secret_2026"

# It is highly recommended to set this in your terminal: export OPENAI_API_KEY="sk-..."
API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE") 
client = OpenAI(api_key=API_KEY)

# ─── DATABASES & PERSISTENCE ───────────────────────────────────────────────────
DATA_DIR = "data"
CANDIDATES_FILE = os.path.join(DATA_DIR, "candidates.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Dummy DBs for Talent Management
BUDGET_DB = {
    "Engineering": {"budget_available": True, "max_ctc_lakhs": 35},
    "Marketing": {"budget_available": False, "max_ctc_lakhs": 0},
}

INTERNAL_TALENT_DB = [
    {"id": "E101", "name": "Rahul T.", "skills": ["Python", "Flask", "React", "SQL"], "status": "on_bench"},
    {"id": "E102", "name": "Sneha K.", "skills": ["Java", "Spring Boot", "AWS"], "status": "on_bench"},
    {"id": "E103", "name": "Amit R.", "skills": ["Python", "Django", "Machine Learning"], "status": "deployed"}
]

def load_candidates():
    if not os.path.exists(CANDIDATES_FILE):
        return {}
    with open(CANDIDATES_FILE, "r") as f:
        return json.load(f)

def save_candidates(data):
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_candidate(cid, updates):
    candidates = load_candidates()
    if cid not in candidates:
        candidates[cid] = {"id": cid, "created_at": datetime.now().isoformat(), "rounds": {}}
    candidates[cid].update(updates)
    save_candidates(candidates)
    return candidates[cid]

# ─── SESSION STORE (In-Memory) ─────────────────────────────────────────────────
interview_sessions = {}

def get_session(sid):
    return interview_sessions.get(sid, {"messages": [], "behavior_logs": [], "turn": 0})

def set_session(sid, data):
    interview_sessions[sid] = data

# ===============================================================================
# DOMAIN 1: TALENT MANAGEMENT GATEKEEPER (AGENTIC WORKFLOW)
# ===============================================================================

class TalentManagementState(TypedDict):
    manager_name: str
    department: str
    job_title: str
    job_description: str
    is_valid: bool
    budget_approved: bool
    rejection_reason: str
    internal_matches: List[Dict[str, Any]]
    final_routing: str
    messages: List[Any]

@tool
def check_budget(department: str) -> str:
    """Checks the internal database to see if a department has hiring budget."""
    data = BUDGET_DB.get(department, {"budget_available": False, "max_ctc_lakhs": 0})
    return json.dumps(data)

@tool
def get_bench_resources() -> str:
    """Retrieves a list of internal employees currently on the bench."""
    bench = [emp for emp in INTERNAL_TALENT_DB if emp["status"] == "on_bench"]
    return json.dumps(bench)

def build_tm_graph():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=API_KEY)

    def verify_request(state: TalentManagementState):
        sys_prompt = """You are a strict Talent Management Approver at TechCorp India.
        Evaluate the hiring request. Use check_budget to see if the department has budget.
        Read the JD. A valid JD must have clear responsibilities and required skills.
        Output a JSON strictly matching this format:
        {"is_valid": true/false, "budget_approved": true/false, "reason": "Explanation if rejected"}"""
        
        evaluator_llm = llm.bind_tools([check_budget])
        user_prompt = f"Dept: {state['department']}\nTitle: {state['job_title']}\nJD: {state['job_description']}"
        evaluator_llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_prompt)])
        
        # Simulating Tool Execution for backend logic
        budget_info = BUDGET_DB.get(state['department'], {})
        has_budget = budget_info.get("budget_available", False)
        is_valid = len(state['job_description']) > 50
        
        reason = ""
        if not has_budget: reason = f"No budget allocated for {state['department']}."
        elif not is_valid: reason = "Job description is too vague."
        return {"budget_approved": has_budget, "is_valid": is_valid, "rejection_reason": reason}

    def notify_rejection(state: TalentManagementState):
        msg = f"Hi {state['manager_name']}, your request for a {state['job_title']} is rejected. Reason: {state['rejection_reason']}"
        return {"final_routing": "rejected", "messages": [msg]}

    def check_internal_talent(state: TalentManagementState):
        bench_data = json.loads(get_bench_resources.invoke({}))
        sys_prompt = """You are an Internal Talent Sourcer. Compare profiles against the JD.
        Return ONLY a JSON array of matched candidate IDs. Example: ["E101"]"""
        user_prompt = f"Job Title: {state['job_title']}\nJD: {state['job_description']}\nCandidates: {json.dumps(bench_data)}"
        
        response = llm.invoke([SystemMessage(content=sys_prompt), HumanMessage(content=user_prompt)])
        try:
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            matched_ids = json.loads(clean_json)
            matched_profiles = [c for c in bench_data if c["id"] in matched_ids]
        except:
            matched_profiles = []
        return {"internal_matches": matched_profiles}

    def route_to_external(state: TalentManagementState):
        msg = f"Approved. No internal matches found. Routing to external TA team for {state['job_title']}."
        return {"final_routing": "external", "messages": [msg]}

    def finalize_internal(state: TalentManagementState):
        names = [c['name'] for c in state['internal_matches']]
        msg = f"Approved. Found bench candidates: {', '.join(names)}. Initiating internal transfer."
        return {"final_routing": "internal", "messages": [msg]}

    def route_approval(state: TalentManagementState) -> Literal["notify_rejection", "check_internal_talent"]:
        return "check_internal_talent" if state["budget_approved"] and state["is_valid"] else "notify_rejection"

    def route_sourcing(state: TalentManagementState) -> Literal["finalize_internal", "route_to_external"]:
        return "finalize_internal" if len(state.get("internal_matches", [])) > 0 else "route_to_external"

    workflow = StateGraph(TalentManagementState)
    workflow.add_node("verify_request", verify_request)
    workflow.add_node("notify_rejection", notify_rejection)
    workflow.add_node("check_internal_talent", check_internal_talent)
    workflow.add_node("route_to_external", route_to_external)
    workflow.add_node("finalize_internal", finalize_internal)

    workflow.add_edge(START, "verify_request")
    workflow.add_conditional_edges("verify_request", route_approval)
    workflow.add_edge("notify_rejection", END)
    workflow.add_conditional_edges("check_internal_talent", route_sourcing)
    workflow.add_edge("route_to_external", END)
    workflow.add_edge("finalize_internal", END)

    return workflow.compile()

tm_graph = build_tm_graph()

@app.route("/api/tm/request_hire", methods=["POST"])
def request_hire():
    """API for Hiring Managers to submit a JD request."""
    data = request.json
    state = {
        "manager_name": data.get("manager_name", "Manager"),
        "department": data.get("department", ""),
        "job_title": data.get("job_title", ""),
        "job_description": data.get("job_description", ""),
        "is_valid": False,
        "budget_approved": False,
        "rejection_reason": "",
        "internal_matches": [],
        "final_routing": "",
        "messages": []
    }
    
    result = tm_graph.invoke(state)
    return jsonify({
        "status": "success",
        "routing_decision": result["final_routing"],
        "system_message": result["messages"][-1] if result["messages"] else "",
        "internal_matches": result.get("internal_matches", [])
    })

# ===============================================================================
# DOMAIN 2: INTERVIEW & PROCTORING ENGINE
# ===============================================================================

def build_interview_graph(system_prompt: str):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.75, api_key=API_KEY)
    def node(state: MessagesState):
        msgs = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm.invoke(msgs)
        return {"messages": [response]}
    g = StateGraph(MessagesState)
    g.add_node("interviewer", node)
    g.add_edge(START, "interviewer")
    g.add_edge("interviewer", END)
    return g.compile()

def transcribe_audio(audio_bytes: bytes) -> str:
    audio_io = io.BytesIO(audio_bytes)
    audio_io.name = "audio.webm"
    result = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_io,
        language="en",
        prompt="Professional interview in Indian English. Terms: CTC, lakhs, crores, fresher, notice period."
    )
    return result.text

def background_behavior_analysis(video_bytes: bytes, sid: str, turn: int):
    try:
        tmp_filename = f"/tmp/tmp_frame_{uuid.uuid4().hex}.webm"
        with open(tmp_filename, "wb") as f:
            f.write(video_bytes)
        
        cap = cv2.VideoCapture(tmp_filename)
        ret, frame = cap.read()
        cap.release()
        
        if os.path.exists(tmp_filename): os.remove(tmp_filename)
            
        if ret:
            _, buf = cv2.imencode(".jpg", frame)
            b64 = base64.b64encode(buf).decode()
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "Analyze frame: 1) Eye contact 2) Phones visible 3) Others in room. 1 sentence max."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}], max_tokens=80
            )
            result_text = res.choices[0].message.content
            sess = get_session(sid)
            sess["behavior_logs"].append(f"[Turn {turn}] {result_text}")
            set_session(sid, sess)
    except Exception as e:
        pass

# --- Indian English Interview Prompts ---
def get_prompt(round_name, jd, resume, notes=""):
    if round_name == "round1":
        return f"""You are Priya, a Talent Acquisition Specialist at TechCorp India (Chennai). ROUND 1: SCREENING. JD: {jd}. Resume: {resume}. Ask about background, notice period, and expected CTC. Use Chennai English syntax (e.g., "do one thing", "only"). Keep it to 2-3 sentences. ONE question at a time. End naturally with: [INTERVIEW_COMPLETE]"""
    elif round_name == "round2":
        return f"""You are Arjun, a Tech Interviewer at TechCorp India (Bangalore). ROUND 2: TECHNICAL. JD: {jd}. Resume: {resume}. Notes: {notes}. Ask 5-6 technical questions progressively. Use Bangalore techie English ("basically", "bandwidth", "make sense?"). ONE question at a time. End naturally with: [INTERVIEW_COMPLETE]"""
    elif round_name == "round3":
        return f"""You are Meera, a Culture Lead at TechCorp India (Mumbai). ROUND 3: BEHAVIOURAL. JD: {jd}. Resume: {resume}. Notes: {notes}. Ask STAR method questions. Use Mumbai corporate English ("fair enough", "sort it out"). Fast-paced but empathetic. ONE question at a time. End naturally with: [INTERVIEW_COMPLETE]"""
    else: # round4
        return f"""You are Rajesh, Head of HR at TechCorp India (Delhi/NCR). FINAL ROUND: HR. JD: {jd}. Resume: {resume}. Notes: {notes}. Negotiate CTC, PF, and notice period buyout. Use authoritative Delhi English ("discuss on this", "do the needful"). ONE topic at a time. End naturally with: [INTERVIEW_COMPLETE]"""

@app.route("/api/interview/start/<round_name>", methods=["POST"])
def interview_start(round_name):
    """Initializes an interview round (round1, round2, round3, round4)"""
    d = request.json
    cid = d.get("candidate_id") or str(uuid.uuid4())[:8].upper()
    jd = d.get("jd", "Software Engineer")
    resume = d.get("resume", "Experienced developer")
    
    candidate = get_candidate(cid) if round_name != "round1" else {}
    notes = str(candidate.get("rounds", {}))

    update_candidate(cid, {"jd": jd, "resume": resume, "status": f"{round_name}_in_progress"})
    
    prompt = get_prompt(round_name, jd, resume, notes)
    graph = build_interview_graph(prompt)
    init_msg = HumanMessage(content="Hello, I'm ready for the interview.")
    result = graph.invoke({"messages": [init_msg]})
    ai_msg = result["messages"][-1]

    sid = f"{round_name}_{cid}"
    set_session(sid, {
        "messages": [init_msg, ai_msg],
        "behavior_logs": [], "turn": 1, "cid": cid, "graph_prompt": prompt
    })

    return jsonify({
        "session_id": sid,
        "candidate_id": cid,
        "text": ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip(),
        "is_done": "[INTERVIEW_COMPLETE]" in ai_msg.content
    })

@app.route("/api/interview/respond", methods=["POST"])
def interview_respond():
    """Receives audio/video file, transcribes, proctors, and returns AI response."""
    sid = request.form.get("session_id")
    sess = get_session(sid)
    video_bytes = request.files["audio"].read()

    threading.Thread(target=background_behavior_analysis, args=(video_bytes, sid, sess["turn"])).start()

    transcript = transcribe_audio(video_bytes)
    if not transcript.strip():
        return jsonify({"error": "Audio unintelligible"}), 400

    sess["messages"].append(HumanMessage(content=transcript))
    graph = build_interview_graph(sess["graph_prompt"])
    result = graph.invoke({"messages": sess["messages"]})
    ai_msg = result["messages"][-1]
    sess["messages"].append(ai_msg)
    sess["turn"] += 1
    set_session(sid, sess)

    is_done = "[INTERVIEW_COMPLETE]" in ai_msg.content
    clean_text = ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip()

    return jsonify({"user_text": transcript, "ai_text": clean_text, "is_done": is_done, "turn": sess["turn"]})

@app.route("/api/interview/report", methods=["POST"])
def interview_report():
    """Generates the final evaluation report for the round."""
    sid = request.json.get("session_id")
    round_key = request.json.get("round", "round1")
    sess = get_session(sid)
    cid = sess.get("cid")

    transcript = "\n".join([f"{'Interviewer' if isinstance(m, AIMessage) else 'Candidate'}: {m.content.replace('[INTERVIEW_COMPLETE]', '').strip()}" for m in sess["messages"] if m.content.strip()])
    behavior_summary = "\n".join(sess["behavior_logs"]) or "No flags."

    report_prompt = f"Evaluate this TechCorp India interview.\nTranscript:\n{transcript}\nBehavior Flags:\n{behavior_summary}\nProvide: 1) Impression 2) Strengths 3) Concerns 4) Integrity Score (1-10) 5) Overall Score (1-10)."
    report_res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": report_prompt}])
    report_text = report_res.choices[0].message.content

    candidate = load_candidates()
    if cid not in candidate: candidate[cid] = {"rounds": {}}
    if "rounds" not in candidate[cid]: candidate[cid]["rounds"] = {}
    candidate[cid]["rounds"][round_key] = {"report": report_text, "behavior_logs": sess["behavior_logs"]}
    save_candidates(candidate)

    return jsonify({"report": report_text, "candidate_id": cid})

# ===============================================================================
# SERVER START
# ===============================================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
