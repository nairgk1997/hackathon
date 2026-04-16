import os
import json
import base64
import io
import uuid
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from openai import OpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
import threading  # Added for background processing

app = Flask(__name__)
app.secret_key = "interview_agent_secret_2024"

# ─── CONFIG ────────────────────────────────────────────────────────────────────
API_KEY = "" # Ensure your API key is set in your environment
client = OpenAI(api_key=API_KEY)
DATA_FILE = "data/candidates.json"

# Voice options
# Note: OpenAI's default voices (onyx, nova) have an American accent. 
# They will pronounce Indian English text accurately, but if you need a native 
# Indian accent for the audio output, consider integrating Google Cloud TTS or ElevenLabs.
VOICES = {
    "male":   {"name": "onyx",    "label": "James (Male)"},
    "female": {"name": "nova",    "label": "Sarah (Female)"},
}

# ─── DATA PERSISTENCE ──────────────────────────────────────────────────────────
def load_candidates():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_candidates(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_candidate(cid):
    return load_candidates().get(cid, {})

def update_candidate(cid, updates):
    candidates = load_candidates()
    if cid not in candidates:
        candidates[cid] = {"id": cid, "created_at": datetime.now().isoformat(), "rounds": {}}
    candidates[cid].update(updates)
    save_candidates(candidates)
    return candidates[cid]

def save_round_data(cid, round_key, data):
    candidates = load_candidates()
    if cid not in candidates:
        candidates[cid] = {"id": cid, "created_at": datetime.now().isoformat(), "rounds": {}}
    if "rounds" not in candidates[cid]:
        candidates[cid]["rounds"] = {}
    candidates[cid]["rounds"][round_key] = data
    save_candidates(candidates)

# ─── LLM GRAPH BUILDER ─────────────────────────────────────────────────────────
def build_graph(system_prompt: str):
    # Utilizing gpt-4o-mini as requested
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

# ─── AUDIO HELPERS ─────────────────────────────────────────────────────────────
def generate_audio(text: str, voice_gender: str = "female") -> str:
    voice = VOICES.get(voice_gender, VOICES["female"])["name"]
    # Clean text for TTS (remove markdown)
    clean = text.replace("**", "").replace("*", "").replace("#", "").replace("_", "")
    response = client.audio.speech.create(model="tts-1-hd", voice=voice, input=clean,
                                           response_format="mp3", speed=0.95)
    return base64.b64encode(response.content).decode()

def transcribe_audio(audio_bytes: bytes) -> str:
    audio_io = io.BytesIO(audio_bytes)
    audio_io.name = "audio.webm"
    # Prompt helps Whisper expect Indian English and corporate terms
    result = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_io,
        language="en",
        prompt="Hello, we are conducting a professional interview in Indian English. Terms like CTC, lakhs, crores, fresher, notice period, and SMT lines may be discussed."
    )
    return result.text

# ─── BEHAVIOR ANALYSIS (Background Task) ───────────────────────────────────────
def background_behavior_analysis(video_bytes: bytes, sid: str, turn: int):
    try:
        tmp_filename = f"/tmp/tmp_frame_{uuid.uuid4().hex}.webm"
        with open(tmp_filename, "wb") as f:
            f.write(video_bytes)
        
        cap = cv2.VideoCapture(tmp_filename)
        ret, frame = cap.read()
        cap.release()
        
        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)
            
        if not ret:
            result_text = "Frame capture failed."
        else:
            _, buf = cv2.imencode(".jpg", frame)
            b64 = base64.b64encode(buf).decode()
            
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "You are an interview proctoring system. Analyze this candidate's frame. "
                            "Check: 1) Eye contact with camera 2) Any phones/devices visible "
                            "3) Anyone else in the room 4) Reading from notes/screen. "
                            "Respond with a single concise sentence assessment."
                        )},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }],
                max_tokens=80
            )
            result_text = res.choices[0].message.content

        sess = get_session(sid)
        sess["behavior_logs"].append(f"[Turn {turn}] {result_text}")
        set_session(sid, sess)

    except Exception as e:
        sess = get_session(sid)
        sess["behavior_logs"].append(f"[Turn {turn}] Analysis unavailable: {str(e)}")
        set_session(sid, sess)

# ─── SYSTEM PROMPTS ────────────────────────────────────────────────────────────
def get_round1_prompt(jd: str, resume: str) -> str:
    return f"""You are Priya, a warm Talent Acquisition Specialist at TechCorp India, operating out of Chennai.
This is a ROUND 1: INTRODUCTORY SCREENING interview.

Job Description: {jd}
Candidate Resume: {resume}

YOUR INTERVIEW FLOW:
1. Greet warmly. Introduce yourself and TechCorp's Chennai operations.
2. Briefly share the company culture.
3. Explain the role.
4. Ask them to introduce themselves.
5. Screen questions (current role, why looking for a change, notice period, expected CTC).
6. Ask if they have questions.
7. Close the interview and mention the technical round.

REGIONAL PERSONALITY & LANGUAGE (South Indian / Chennai English):
- Use South Indian English syntax naturally. 
- Use "only" for emphasis (e.g., "We are based out of Chennai only," "You can send it to me only").
- Use phrases like "do one thing," "is it?", "prepone," and "updation".
- Be exceptionally polite, warm, and slightly formal.
- Example: "Do one thing, tell me a little bit about your background first."
- Keep responses concise (2-4 sentences). ONE question at a time.
- End your final message with exactly: [INTERVIEW_COMPLETE]"""

def get_round2_prompt(jd: str, resume: str, round1_notes: str) -> str:
    return f"""You are Arjun, a Senior Software Engineer at TechCorp India, operating out of Bangalore.
This is a ROUND 2: TECHNICAL INTERVIEW.

Job Description: {jd}
Candidate Resume: {resume}
Round 1 Notes: {round1_notes}

YOUR INTERVIEW FLOW:
1. Casual greeting, set context (45 mins, conceptual + problem solving).
2. Ask 5-6 technical questions progressively based on the JD.
3. Probe deeply on interesting answers.
4. Give a practical, real-world scenario.
5. Ask if they have technical questions for you.
6. Close the interview.

REGIONAL PERSONALITY & LANGUAGE (Bangalore Techie English):
- Use Bangalore startup/tech ecosystem English.
- Use words like "basically", "bandwidth", "super cool", "make sense?", "take offline".
- Mix casual tech slang with professional English. 
- Example: "Basically, what we are looking for is someone who can scale this. Does that make sense?" or "That's a solid approach, actually."
- Be collegial and fast-paced. If they struggle, say "No worries man/boss, let's figure it out together."
- ONE question at a time. Listen carefully.
- End your final message with exactly: [INTERVIEW_COMPLETE]"""

def get_round3_prompt(jd: str, resume: str, round1_notes: str, round2_notes: str) -> str:
    return f"""You are Meera, a People & Culture Lead at TechCorp India, operating out of Mumbai.
This is a ROUND 3: BEHAVIOURAL INTERVIEW.

Job Description: {jd}
Candidate Resume: {resume}
Round 1 Notes: {round1_notes}
Round 2 Notes: {round2_notes}

YOUR INTERVIEW FLOW:
1. Warm welcome back. Explain this is a behavioural round.
2. Ask 5-6 STAR-method questions (conflict, tight deadlines, failure, initiative).
3. Probe on outcomes.
4. Check for culture fit and preferred working style.
5. Ask if they have questions about team culture.
6. Close the interview.

REGIONAL PERSONALITY & LANGUAGE (Mumbai Corporate English):
- Use fast-paced, direct Mumbai corporate English.
- Use phrases like "fair enough," "sort it out," "completely fine," "what say?".
- Be highly practical, energetic, and slightly informal but highly professional.
- Example: "Fair enough, deadlines can get crazy. How did you sort it out eventually?"
- Create a safe space but keep the conversation moving briskly.
- ONE question at a time.
- End your final message with exactly: [INTERVIEW_COMPLETE]"""

def get_round4_prompt(jd: str, resume: str, all_notes: str) -> str:
    return f"""You are Rajesh, Head of HR at TechCorp India, operating out of the Delhi/NCR office.
This is the FINAL ROUND: HR & COMPENSATION NEGOTIATION.

Job Description: {jd}
Candidate Resume: {resume}
Previous Notes: {all_notes}

YOUR INTERVIEW FLOW:
1. Congratulate them firmly on reaching the final round.
2. Reconfirm role, reporting structure.
3. Discuss compensation: Ask for current CTC, present the offer range in Lakhs. Discuss in-hand, variable, and PF.
4. Explain notice period buyout policy and joining bonus if applicable.
5. Address logistics (background check, documents).
6. Give them space to ask questions.
7. Close the interview.

REGIONAL PERSONALITY & LANGUAGE (Delhi/North Indian Corporate English):
- Use authoritative, senior Delhi corporate English.
- Use phrasing like "discuss on this," "revert back," "do the needful," "take it up," "good good."
- Address the candidate with respect but maintain a senior, slightly dominant posture.
- Example: "We can discuss on the variable part, but base is fixed. I'll ask my team to revert back to you with the final numbers."
- Be very straightforward about numbers and policies.
- ONE topic at a time.
- End your final message with exactly: [INTERVIEW_COMPLETE]"""

# ─── SESSION STORE (in-memory per session) ─────────────────────────────────────
interview_sessions = {}

def get_session(sid):
    return interview_sessions.get(sid, {"messages": [], "behavior_logs": [], "turn": 0})

def set_session(sid, data):
    interview_sessions[sid] = data

# ─── ROUTES: HOME ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ─── ROUTES: ROUND 1 ───────────────────────────────────────────────────────────
@app.route("/round1")
def round1():
    return render_template("round1.html")

@app.route("/round1/start", methods=["POST"])
def round1_start():
    d = request.json
    cid = d.get("candidate_id") or str(uuid.uuid4())[:8].upper()
    jd = d.get("jd", "Software Engineer")
    resume = d.get("resume", "Experienced developer")
    voice = d.get("voice", "female")

    update_candidate(cid, {"name": d.get("name", "Candidate"), "jd": jd, "resume": resume, "status": "round1_in_progress"})

    sid = f"r1_{cid}"
    prompt = get_round1_prompt(jd, resume)
    graph = build_graph(prompt)
    init_msg = HumanMessage(content="Hello, I'm ready for the interview.")
    result = graph.invoke({"messages": [init_msg]})
    ai_msg = result["messages"][-1]

    set_session(sid, {
        "messages": [init_msg, ai_msg],
        "behavior_logs": [],
        "turn": 1,
        "cid": cid,
        "jd": jd,
        "resume": resume,
        "voice": voice,
        "graph_prompt": prompt
    })

    return jsonify({
        "session_id": sid,
        "candidate_id": cid,
        "text": ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip(),
        "audio": generate_audio(ai_msg.content, voice),
        "is_done": "[INTERVIEW_COMPLETE]" in ai_msg.content
    })

@app.route("/round1/respond", methods=["POST"])
def round1_respond():
    return handle_respond("round1")

@app.route("/round1/log_event", methods=["POST"])
def round1_log():
    return handle_log_event()

@app.route("/round1/report", methods=["POST"])
def round1_report():
    return handle_report("round1", next_round="/round2")

# ─── ROUTES: ROUND 2 ───────────────────────────────────────────────────────────
@app.route("/round2")
def round2():
    return render_template("round2.html")

@app.route("/round2/start", methods=["POST"])
def round2_start():
    d = request.json
    cid = d.get("candidate_id")
    voice = d.get("voice", "male")
    candidate = get_candidate(cid)
    jd = candidate.get("jd", "")
    resume = candidate.get("resume", "")
    round1_notes = candidate.get("rounds", {}).get("round1", {}).get("report", "No round 1 notes available.")

    prompt = get_round2_prompt(jd, resume, round1_notes)
    graph = build_graph(prompt)
    init_msg = HumanMessage(content="Hello, I'm ready for the technical interview.")
    result = graph.invoke({"messages": [init_msg]})
    ai_msg = result["messages"][-1]

    sid = f"r2_{cid}"
    set_session(sid, {
        "messages": [init_msg, ai_msg],
        "behavior_logs": [],
        "turn": 1,
        "cid": cid,
        "jd": jd,
        "resume": resume,
        "voice": voice,
        "graph_prompt": prompt
    })

    update_candidate(cid, {"status": "round2_in_progress"})

    return jsonify({
        "session_id": sid,
        "text": ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip(),
        "audio": generate_audio(ai_msg.content, voice),
        "is_done": "[INTERVIEW_COMPLETE]" in ai_msg.content
    })

@app.route("/round2/respond", methods=["POST"])
def round2_respond():
    return handle_respond("round2")

@app.route("/round2/log_event", methods=["POST"])
def round2_log():
    return handle_log_event()

@app.route("/round2/report", methods=["POST"])
def round2_report():
    return handle_report("round2", next_round="/round3")

# ─── ROUTES: ROUND 3 ───────────────────────────────────────────────────────────
@app.route("/round3")
def round3():
    return render_template("round3.html")

@app.route("/round3/start", methods=["POST"])
def round3_start():
    d = request.json
    cid = d.get("candidate_id")
    voice = d.get("voice", "female")
    candidate = get_candidate(cid)
    jd = candidate.get("jd", "")
    resume = candidate.get("resume", "")
    rounds = candidate.get("rounds", {})
    round1_notes = rounds.get("round1", {}).get("report", "Not available.")
    round2_notes = rounds.get("round2", {}).get("report", "Not available.")

    prompt = get_round3_prompt(jd, resume, round1_notes, round2_notes)
    graph = build_graph(prompt)
    init_msg = HumanMessage(content="Hello, I'm ready for the behavioural interview.")
    result = graph.invoke({"messages": [init_msg]})
    ai_msg = result["messages"][-1]

    sid = f"r3_{cid}"
    set_session(sid, {
        "messages": [init_msg, ai_msg],
        "behavior_logs": [],
        "turn": 1,
        "cid": cid,
        "jd": jd,
        "resume": resume,
        "voice": voice,
        "graph_prompt": prompt
    })

    update_candidate(cid, {"status": "round3_in_progress"})

    return jsonify({
        "session_id": sid,
        "text": ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip(),
        "audio": generate_audio(ai_msg.content, voice),
        "is_done": "[INTERVIEW_COMPLETE]" in ai_msg.content
    })

@app.route("/round3/respond", methods=["POST"])
def round3_respond():
    return handle_respond("round3")

@app.route("/round3/log_event", methods=["POST"])
def round3_log():
    return handle_log_event()

@app.route("/round3/report", methods=["POST"])
def round3_report():
    return handle_report("round3", next_round="/round4")

# ─── ROUTES: ROUND 4 ───────────────────────────────────────────────────────────
@app.route("/round4")
def round4():
    return render_template("round4.html")

@app.route("/round4/start", methods=["POST"])
def round4_start():
    d = request.json
    cid = d.get("candidate_id")
    voice = d.get("voice", "male")
    candidate = get_candidate(cid)
    jd = candidate.get("jd", "")
    resume = candidate.get("resume", "")
    rounds = candidate.get("rounds", {})
    all_notes = "\n\n".join([
        f"Round 1 (Screening): {rounds.get('round1', {}).get('report', 'N/A')}",
        f"Round 2 (Technical): {rounds.get('round2', {}).get('report', 'N/A')}",
        f"Round 3 (Behavioural): {rounds.get('round3', {}).get('report', 'N/A')}",
    ])

    prompt = get_round4_prompt(jd, resume, all_notes)
    graph = build_graph(prompt)
    init_msg = HumanMessage(content="Hello, I'm ready for the HR discussion.")
    result = graph.invoke({"messages": [init_msg]})
    ai_msg = result["messages"][-1]

    sid = f"r4_{cid}"
    set_session(sid, {
        "messages": [init_msg, ai_msg],
        "behavior_logs": [],
        "turn": 1,
        "cid": cid,
        "jd": jd,
        "resume": resume,
        "voice": voice,
        "graph_prompt": prompt
    })

    update_candidate(cid, {"status": "round4_in_progress"})

    return jsonify({
        "session_id": sid,
        "text": ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip(),
        "audio": generate_audio(ai_msg.content, voice),
        "is_done": "[INTERVIEW_COMPLETE]" in ai_msg.content
    })

@app.route("/round4/respond", methods=["POST"])
def round4_respond():
    return handle_respond("round4")

@app.route("/round4/log_event", methods=["POST"])
def round4_log():
    return handle_log_event()

@app.route("/round4/report", methods=["POST"])
def round4_report():
    return handle_report("round4", next_round=None)

# ─── ADMIN DASHBOARD ───────────────────────────────────────────────────────────
@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin/candidates", methods=["GET"])
def admin_candidates():
    return jsonify(load_candidates())

@app.route("/admin/candidate/<cid>", methods=["GET"])
def admin_candidate_detail(cid):
    return jsonify(get_candidate(cid))

# ─── SHARED HANDLERS ───────────────────────────────────────────────────────────
def handle_respond(round_name: str):
    sid = request.form.get("session_id")
    sess = get_session(sid)
    voice = sess.get("voice", "female")
    video_bytes = request.files["audio"].read()

    current_turn = sess["turn"]

    threading.Thread(
        target=background_behavior_analysis,
        args=(video_bytes, sid, current_turn)
    ).start()

    transcript = transcribe_audio(video_bytes)
    if not transcript.strip():
        return jsonify({"error": "Could not transcribe audio. Please try again."}), 400

    sess["messages"].append(HumanMessage(content=transcript))

    graph = build_graph(sess["graph_prompt"])
    result = graph.invoke({"messages": sess["messages"]})
    ai_msg = result["messages"][-1]
    sess["messages"].append(ai_msg)
    
    sess["turn"] += 1

    is_done = "[INTERVIEW_COMPLETE]" in ai_msg.content
    clean_text = ai_msg.content.replace("[INTERVIEW_COMPLETE]", "").strip()

    set_session(sid, sess)

    return jsonify({
        "user_text": transcript,
        "ai_text": clean_text,
        "audio": generate_audio(clean_text, voice),
        "is_done": is_done,
        "turn": sess["turn"]
    })

def handle_log_event():
    event = request.json.get("event")
    sid = request.json.get("session_id")
    if sid:
        sess = get_session(sid)
        sess["behavior_logs"].append(f"[FLAG] {event}")
        set_session(sid, sess)
    return jsonify({"status": "logged"})

def handle_report(round_key: str, next_round: str):
    data = request.json
    sid = data.get("session_id")
    sess = get_session(sid)
    cid = sess.get("cid")

    transcript_lines = []
    for m in sess["messages"]:
        role = "Interviewer" if isinstance(m, AIMessage) else "Candidate"
        clean = m.content.replace("[INTERVIEW_COMPLETE]", "").strip()
        if clean:
            transcript_lines.append(f"{role}: {clean}")
    transcript = "\n".join(transcript_lines)

    behavior_summary = "\n".join(sess["behavior_logs"]) or "No flags."

    report_prompt = f"""You are a professional recruitment analyst evaluating an interview for TechCorp India. Generate a detailed interview report.

Round: {round_key.upper()}
Transcript:
{transcript}

Behavior Observations:
{behavior_summary}

Generate a structured report with these sections:
1. OVERALL IMPRESSION (2-3 sentences)
2. KEY STRENGTHS (bullet points)
3. AREAS OF CONCERN (bullet points)  
4. STANDOUT MOMENTS (notable quotes or moments)
5. BEHAVIOR INTEGRITY (based on proctoring flags)
6. RECOMMENDATION (Strongly Recommend / Recommend / Recommend with Reservations / Do Not Recommend)
7. SCORES:
   - Communication: X/10
   - Technical/Relevance: X/10
   - Confidence: X/10
   - Integrity (behavior): X/10
   - Overall: X/10

Be specific, professional, and cite actual things the candidate said."""

    report_res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": report_prompt}]
    )
    report_text = report_res.choices[0].message.content

    save_round_data(cid, round_key, {
        "completed_at": datetime.now().isoformat(),
        "transcript": transcript,
        "behavior_logs": sess["behavior_logs"],
        "report": report_text
    })

    status_map = {
        "round1": "round1_complete",
        "round2": "round2_complete",
        "round3": "round3_complete",
        "round4": "completed"
    }
    update_candidate(cid, {"status": status_map.get(round_key, "in_progress")})

    return jsonify({
        "report": report_text,
        "candidate_id": cid,
        "next_round": next_round
    })

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    app.run(debug=True, port=5000)
