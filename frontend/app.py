import streamlit as st
import requests
import json
import time

# Base URL of the FastAPI backend
BACKEND_URL = "http://127.0.0.1:8000"

# Set up Streamlit Page configurations
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS Injection for a premium SaaS look
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
    
    /* Global style overrides */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1e1e38 0%, #0c0c1e 70%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .title-text {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700;
    }
    
    /* Neon Text Gradient */
    .neon-text-gradient {
        background: linear-gradient(90deg, #45f3ff, #00ff87, #ff007f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(69, 243, 255, 0.2);
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(13, 13, 33, 0.7);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        margin-bottom: 20px;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: rgba(69, 243, 255, 0.3);
        box-shadow: 0 20px 45px rgba(69, 243, 255, 0.15);
    }
    
    /* Styled Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #0c0c1e !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 35px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 8px 20px rgba(0, 242, 254, 0.4) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        width: 100%;
        display: block;
    }
    
    .stButton>button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 12px 25px rgba(0, 242, 254, 0.6) !important;
        color: #ffffff !important;
    }
    
    /* Secondary Action Button */
    .sec-btn>button {
        background: transparent !important;
        border: 2px solid #ff007f !important;
        color: #ff007f !important;
        box-shadow: 0 0 15px rgba(255, 0, 127, 0.2) !important;
    }
    .sec-btn>button:hover {
        background: #ff007f !important;
        color: #ffffff !important;
        box-shadow: 0 0 25px rgba(255, 0, 127, 0.5) !important;
    }
    
    /* Upload Boxes styling */
    .upload-box {
        border: 2px dashed rgba(69, 243, 255, 0.3);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        background: rgba(255, 255, 255, 0.02);
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #45f3ff;
        background: rgba(69, 243, 255, 0.05);
    }
    
    /* Chat Bubble Design */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 15px;
        margin-bottom: 25px;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .chat-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        width: 100%;
    }
    
    .chat-row.user {
        flex-direction: row-reverse;
    }
    
    .avatar {
        font-size: 1.8rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .bubble {
        padding: 16px 20px;
        border-radius: 18px;
        max-width: 75%;
        font-size: 0.98rem;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        position: relative;
    }
    
    .bubble.ai {
        background: rgba(26, 32, 53, 0.85);
        color: #e2e8f0;
        border-left: 4px solid #00ff87;
        border-top-left-radius: 2px;
        border: 1px solid rgba(0, 255, 135, 0.15);
    }
    
    .bubble.user {
        background: rgba(88, 28, 135, 0.6);
        color: #f8fafc;
        border-right: 4px solid #ff007f;
        border-top-right-radius: 2px;
        border: 1px solid rgba(255, 0, 127, 0.15);
    }
    
    /* Circular progress indicator */
    .circular-progress-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px auto;
    }
    
    .progress-circle {
        position: relative;
        width: 150px;
        height: 150px;
    }
    
    .progress-circle svg {
        transform: rotate(-90deg);
        width: 100%;
        height: 100%;
    }
    
    .progress-circle circle {
        fill: none;
        stroke-width: 12;
    }
    
    .progress-circle .bg {
        stroke: #1e1e30;
    }
    
    .progress-circle .bar {
        stroke-dasharray: 440;
        transition: stroke-dashoffset 1.5s ease-in-out;
        stroke-linecap: round;
    }
    
    .score-val {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-family: 'Outfit', sans-serif;
    }
    
    .score-num {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
    }
    
    .score-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    
    /* Evaluation cards inside Chat */
    .eval-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    
    /* Typing Animation */
    .typing-indicator {
        display: flex;
        gap: 5px;
        padding: 10px 15px;
        background: rgba(26, 32, 53, 0.85);
        border-radius: 12px;
        width: fit-content;
        margin-left: 55px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #00ff87;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out both;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State Variables
if "screen" not in st.session_state:
    st.session_state.screen = "landing"
if "main_questions" not in st.session_state:
    st.session_state.main_questions = []
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_followup" not in st.session_state:
    st.session_state.is_followup = False
if "followup_count" not in st.session_state:
    st.session_state.followup_count = 0
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = None
if "last_evaluation" not in st.session_state:
    st.session_state.last_evaluation = None

# Inject CSS
inject_custom_css()

# API Interaction Helpers
def upload_files_to_backend(resume_file, jd_file, jd_text):
    files = {
        "resume": (resume_file.name, resume_file.getvalue(), "application/pdf")
    }
    data = {}
    if jd_file:
        files["jd_file"] = (jd_file.name, jd_file.getvalue(), jd_file.type)
    if jd_text:
        data["jd_text"] = jd_text
        
    try:
        response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": f"Could not connect to FastAPI server. Please ensure it is running on port 8000. Error: {str(e)}"}

def generate_questions_from_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/generate-questions")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def evaluate_answer_via_backend(question, answer):
    try:
        payload = {"question": question, "answer": answer}
        response = requests.post(f"{BACKEND_URL}/evaluate", json=payload)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def generate_followup_via_backend(question, answer):
    try:
        payload = {"question": question, "answer": answer}
        response = requests.post(f"{BACKEND_URL}/generate-followup", json=payload)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_final_feedback_from_backend():
    try:
        response = requests.get(f"{BACKEND_URL}/feedback")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# SCREEN 1: LANDING SCREEN
def render_landing():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    cols = st.columns([1, 8, 1])
    with cols[1]:
        st.markdown("""
        <div style='text-align: center;'>
            <div style='font-size: 4.5rem; margin-bottom: 5px;'>🤖</div>
            <h1 class='neon-text-gradient' style='font-size: 3.8rem; margin-bottom: 15px;'>AI Interview Assistant</h1>
            <p style='font-size: 1.4rem; color: #94a3b8; max-width: 700px; margin: 0 auto 35px auto; line-height: 1.6;'>
                Elevate your preparation with RAG-powered smart interviews. Real-time evaluations, strict follow-up questions, and custom feedback based directly on your target JD and Resume.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Start button container
        btn_cols = st.columns([3, 2, 3])
        with btn_cols[1]:
            if st.button("Start Interview 🚀"):
                st.session_state.screen = "upload"
                st.rerun()
                
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# SCREEN 2: UPLOAD RESUME & JD
def render_upload():
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns([1, 8, 1])
    with cols[1]:
        st.markdown("<h2 style='text-align: center; color: #45f3ff; margin-bottom: 25px;'>Upload Setup Details</h2>", unsafe_allow_html=True)
        
        # Display backend warning if offline
        try:
            requests.get(BACKEND_URL)
        except:
            st.error("⚠️ Backend server offline! Run 'uvicorn backend.main:app --reload' in the background to activate backend APIs.")
            
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        
        up_cols = st.columns(2)
        with up_cols[0]:
            st.markdown("<h4 style='color: #00ff87; margin-bottom: 10px;'>📄 1. Candidate Resume</h4>", unsafe_allow_html=True)
            resume_file = st.file_uploader("Upload Resume (PDF format)", type=["pdf"], key="res_uploader")
            
        with up_cols[1]:
            st.markdown("<h4 style='color: #ff007f; margin-bottom: 10px;'>💼 2. Job Description</h4>", unsafe_allow_html=True)
            jd_type = st.radio("Choose Input Type:", ["Upload File", "Paste Text"], horizontal=True)
            
            jd_file = None
            jd_text = ""
            if jd_type == "Upload File":
                jd_file = st.file_uploader("Upload Job Description (PDF/TXT)", type=["pdf", "txt"], key="jd_uploader")
            else:
                jd_text = st.text_area("Paste Job Description Text", height=150, placeholder="Provide details of the role here...")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Trigger button
        st.markdown("<br>", unsafe_allow_html=True)
        sub_cols = st.columns([3, 2, 3])
        with sub_cols[1]:
            if st.button("Initialize Interview ⚙️"):
                if not resume_file:
                    st.error("Please upload a resume.")
                elif jd_type == "Upload File" and not jd_file:
                    st.error("Please upload a Job Description file.")
                elif jd_type == "Paste Text" and not jd_text.strip():
                    st.error("Please paste Job Description text.")
                else:
                    with st.spinner("Processing files & preparing FAISS index..."):
                        res = upload_files_to_backend(resume_file, jd_file, jd_text)
                        
                        if res.get("status") == "success":
                            # Generate Questions
                            q_res = generate_questions_from_backend()
                            if q_res.get("status") == "success":
                                st.session_state.main_questions = q_res.get("questions", [])
                                st.session_state.current_question_index = 0
                                st.session_state.current_question = st.session_state.main_questions[0]
                                st.session_state.is_followup = False
                                st.session_state.followup_count = 0
                                st.session_state.chat_history = [
                                    {"role": "assistant", "content": st.session_state.current_question}
                                ]
                                st.session_state.screen = "interview"
                                st.success("Setup complete!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Failed to generate questions: {q_res.get('detail', 'Unknown error')}")
                        else:
                            st.error(f"Processing failed: {res.get('detail', res.get('message', 'Unknown error'))}")

# SCREEN 3: INTERVIEW CHAT INTERFACE
def render_interview():
    st.markdown(f"<h2 style='text-align: center; color: #45f3ff;'>Mock Interview</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #94a3b8;'>Question {st.session_state.current_question_index + 1} of 5</p>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    # Render chat history
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        avatar = "🤖" if msg["role"] == "assistant" else "🧑"
        css_class = "ai" if msg["role"] == "assistant" else "user"
        align_class = "" if msg["role"] == "assistant" else "user"
        
        st.markdown(f"""
        <div class="chat-row {align_class}">
            <div class="avatar">{avatar}</div>
            <div class="bubble {css_class}">
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display evaluation if attached to the message
        if "evaluation" in msg and msg["evaluation"]:
            eval_data = msg["evaluation"]
            st.markdown(f"""
            <div class="chat-row">
                <div style="width: 55px;"></div>
                <div class="eval-card" style="width: 70%; border-left: 4px solid {'#00ff87' if eval_data['score'] >= 5 else '#ff007f'};">
                    <span style="font-weight: 700; color: {'#00ff87' if eval_data['score'] >= 5 else '#ff007f'};">
                        Score: {eval_data['score']}/10
                    </span><br>
                    <strong>💪 Strengths:</strong> {', '.join(eval_data.get('strengths', []))}<br>
                    <strong>⚠️ Areas to Improve:</strong> {', '.join(eval_data.get('improvements', []))}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("</div>", unsafe_allow_html=True)
    
    # User Input area
    # If we are waiting for user input
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
    
    # Text Input Form
    with st.form(key="answer_form", clear_on_submit=True):
        user_answer = st.text_area("Your Answer:", key="user_answer_input", height=100, placeholder="Explain your answer clearly and technically...")
        submit_btn = st.form_submit_button("Submit Answer")
        
        if submit_btn:
            if not user_answer.strip():
                st.warning("Please type your answer before submitting.")
            else:
                # Add answer to history
                st.session_state.chat_history.append({"role": "user", "content": user_answer})
                
                # Show typing animation
                placeholder = st.empty()
                with placeholder.container():
                    st.markdown("""
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                # Call evaluation API
                res = evaluate_answer_via_backend(st.session_state.current_question, user_answer)
                placeholder.empty()
                
                if res.get("status") == "success":
                    eval_data = res.get("evaluation", {})
                    score = eval_data.get("score", 5.0)
                    
                    # Attach evaluation metadata to user's chat message to display it
                    st.session_state.chat_history[-1]["evaluation"] = eval_data
                    st.session_state.last_evaluation = eval_data
                    
                    # Smart Followup condition:
                    # Score < 5 and we haven't asked a follow-up for the current main question yet
                    if score < 5 and not st.session_state.is_followup and st.session_state.followup_count == 0:
                        # Generate Followup Question
                        follow_placeholder = st.empty()
                        with follow_placeholder.container():
                            st.markdown("""
                            <div class="typing-indicator">
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                                <div class="typing-dot"></div>
                            </div>
                            """, unsafe_allow_html=True)
                        follow_res = generate_followup_via_backend(st.session_state.current_question, user_answer)
                        follow_placeholder.empty()
                        
                        if follow_res.get("status") == "success":
                            followup_q = follow_res.get("followup", "Can you explain that in more detail?")
                            st.session_state.current_question = followup_q
                            st.session_state.is_followup = True
                            st.session_state.followup_count = 1
                            # Add follow-up question to chat
                            st.session_state.chat_history.append({"role": "assistant", "content": followup_q})
                            st.rerun()
                        else:
                            st.error("Could not generate follow-up question. Proceeding to next question.")
                            time.sleep(1)
                            
                    # Else (score >= 5 or we already did a follow-up):
                    # Proceed to next main question
                    st.session_state.is_followup = False
                    st.session_state.followup_count = 0
                    st.session_state.current_question_index += 1
                    
                    if st.session_state.current_question_index < len(st.session_state.main_questions):
                        next_q = st.session_state.main_questions[st.session_state.current_question_index]
                        st.session_state.current_question = next_q
                        st.session_state.chat_history.append({"role": "assistant", "content": next_q})
                        st.rerun()
                    else:
                        # Completed all questions! Transition to feedback screen
                        st.session_state.screen = "feedback"
                        st.rerun()
                else:
                    st.error(f"Error communicating with evaluator: {res.get('message', 'Unknown error')}")
                    
    st.markdown("</div>", unsafe_allow_html=True)

# SCREEN 4: FEEDBACK DASHBOARD
def render_feedback():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;' class='neon-text-gradient'>Performance Evaluation</h1>", unsafe_allow_html=True)
    
    # Load feedback report if not already loaded
    if st.session_state.feedback_data is None:
        with st.spinner("Compiling performance stats and hiring metrics..."):
            res = get_final_feedback_from_backend()
            if res.get("status") == "success":
                st.session_state.feedback_data = res
            else:
                st.error(f"Could not retrieve feedback: {res.get('message', 'Unknown Error')}")
                st.session_state.feedback_data = {}
                
    feedback = st.session_state.feedback_data
    if not feedback:
        return
        
    score = feedback.get("overall_score", 0)
    decision = feedback.get("decision", "Maybe")
    
    # Pick progress circle color based on score
    if score >= 70:
        color = "#00ff87"  # Green
        decision_emoji = "✅ Hire (Yes)" if decision == "Yes" else "🤔 Maybe"
    elif score >= 50:
        color = "#ffb703"  # Yellow
        decision_emoji = "🤔 Maybe"
    else:
        color = "#ff007f"  # Red
        decision_emoji = "❌ Do Not Hire (No)" if decision == "No" else "🤔 Maybe"
        
    # Offset calculation for 440px stroke-dasharray
    stroke_offset = 440 - (440 * score / 100)
    
    # Grid layout for Dashboard
    cols = st.columns([1, 4, 6, 1])
    
    with cols[1]:
        # Score and Decision Card
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <h3 style="color: #45f3ff; margin-bottom: 20px;">Overall Match</h3>
            <div class="circular-progress-wrapper">
                <div class="progress-circle">
                    <svg>
                        <circle class="bg" cx="75" cy="75" r="70"></circle>
                        <circle class="bar" cx="75" cy="75" r="70" style="stroke-dashoffset: {stroke_offset}; stroke: {color};"></circle>
                    </svg>
                    <div class="score-val">
                        <div class="score-num" style="color: {color};">{score}</div>
                        <div class="score-label">Score</div>
                    </div>
                </div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.08); margin: 20px 0;">
            <p style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Hiring Decision</p>
            <h4 style="color: {color}; font-size: 1.4rem;">{decision_emoji}</h4>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        # Details Card
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #45f3ff; margin-bottom: 20px;'>Interview Analysis</h3>", unsafe_allow_html=True)
        
        # Strengths
        st.markdown("<h5 style='color: #00ff87; font-weight: 600;'>💪 Key Strengths</h5>", unsafe_allow_html=True)
        for s in feedback.get("strengths", []):
            st.markdown(f"<p style='font-size: 0.95rem; margin-left: 15px;'>• {s}</p>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Weaknesses
        st.markdown("<h5 style='color: #ff007f; font-weight: 600;'>⚠️ Areas for Improvement</h5>", unsafe_allow_html=True)
        for w in feedback.get("weaknesses", []):
            st.markdown(f"<p style='font-size: 0.95rem; margin-left: 15px;'>• {w}</p>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Suggestions
        st.markdown("<h5 style='color: #45f3ff; font-weight: 600;'>💡 Actionable Suggestions</h5>", unsafe_allow_html=True)
        for sug in feedback.get("suggestions", []):
            st.markdown(f"<p style='font-size: 0.95rem; margin-left: 15px;'>• {sug}</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Full detailed score breakdown accordion style
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 View Detailed Question Breakdown", expanded=False):
        for idx, item in enumerate(feedback.get("detailed_evaluations", [])):
            st.markdown(f"""
            <div class="glass-card" style="padding: 20px; border-left: 4px solid {'#00ff87' if item['score'] >= 5 else '#ff007f'};">
                <h5 style="color: #45f3ff; margin-bottom: 5px;">Question {idx+1}: {item['question']}</h5>
                <p style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 10px;"><strong>Candidate Answer:</strong> <em>{item['answer']}</em></p>
                <div style="font-size: 0.88rem; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                    <span style="color: {'#00ff87' if item['score'] >= 5 else '#ff007f'}; font-weight: 700;">Score: {item['score']}/10</span><br>
                    <strong>Strengths:</strong> {', '.join(item['strengths'])}<br>
                    <strong>Improvements:</strong> {', '.join(item['improvements'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # Reset Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    btn_cols = st.columns([4, 2, 2, 4])
    with btn_cols[1]:
        if st.button("New Interview 🔄"):
            # Clear state
            st.session_state.screen = "upload"
            st.session_state.main_questions = []
            st.session_state.current_question_index = 0
            st.session_state.current_question = ""
            st.session_state.chat_history = []
            st.session_state.is_followup = False
            st.session_state.followup_count = 0
            st.session_state.feedback_data = None
            st.session_state.last_evaluation = None
            st.rerun()
            
    with btn_cols[2]:
        # Custom secondary action using markdown container trick if st.button can't be custom colored easily
        # but we configured .sec-btn classes in CSS
        st.markdown("<div class='sec-btn'>", unsafe_allow_html=True)
        if st.button("Back to Home 🏠"):
            st.session_state.screen = "landing"
            st.session_state.main_questions = []
            st.session_state.current_question_index = 0
            st.session_state.current_question = ""
            st.session_state.chat_history = []
            st.session_state.is_followup = False
            st.session_state.followup_count = 0
            st.session_state.feedback_data = None
            st.session_state.last_evaluation = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Application Routing Engine
if st.session_state.screen == "landing":
    render_landing()
elif st.session_state.screen == "upload":
    render_upload()
elif st.session_state.screen == "interview":
    render_interview()
elif st.session_state.screen == "feedback":
    render_feedback()
