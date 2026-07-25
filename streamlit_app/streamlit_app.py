"""
AI Interview Coach — Streamlit Edition
Single-file rebuild of the original FastAPI + React app, for deployment on
Streamlit Community Cloud (Render backend was suspended).

Flow: pick role -> hear question (gTTS) -> record/upload answer ->
Faster-Whisper transcribes -> Groq LLaMA 3.3 scores -> PDF report at the end.
"""

import io
import os
import json
import random
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from faster_whisper import WhisperModel

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER

load_dotenv()

# ──────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="AI Interview Coach", page_icon="🎙️", layout="centered")

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing. Add it to `.env` locally or to Streamlit Cloud → Settings → Secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

QUESTION_BANK = {
    "SDE": [
        "Explain the difference between a stack and a queue. When would you use each?",
        "What is time complexity and why does it matter? Give an example.",
        "Explain what REST APIs are and how HTTP methods are used.",
        "What is the difference between SQL and NoSQL databases?",
        "Describe how you would debug a production issue.",
        "What is Git and explain the difference between merge and rebase.",
        "Explain object-oriented programming principles with examples.",
        "What is a memory leak and how would you identify one?",
    ],
    "AI Engineer": [
        "Explain the difference between supervised, unsupervised, and reinforcement learning.",
        "What is overfitting and how do you prevent it?",
        "Describe how transformers work in NLP.",
        "What is the difference between precision and recall?",
        "Explain gradient descent and its variants.",
        "What is RAG (Retrieval Augmented Generation) and when would you use it?",
        "How do you evaluate the performance of a language model?",
        "What is fine-tuning vs prompt engineering?",
    ],
    "Data Analyst": [
        "Explain the difference between mean, median, and mode.",
        "What is a p-value and how do you interpret it?",
        "Describe how you would handle missing data in a dataset.",
        "What is the difference between correlation and causation?",
        "Explain what A/B testing is and how you'd set one up.",
        "How would you identify outliers in a dataset?",
        "What SQL query would you write to find the top 5 customers by revenue?",
        "Explain what a pivot table is and when you'd use one.",
    ],
}

SCORING_PROMPT = """You are a strict but fair technical interview evaluator. Score the candidate's answer to the interview question below.

Role being interviewed for: {role}
Question: {question}
Candidate's Answer: {answer}

Evaluate on these 4 dimensions (each 0-10):
1. RELEVANCE: Did they answer the actual question asked?
2. CLARITY: Was the answer clear, structured, and easy to follow?
3. TECHNICAL_ACCURACY: Was the technical content correct and precise?
4. CONFIDENCE: Did the answer show confidence (avoid filler phrases like "I think maybe", "I'm not sure but")?

Return ONLY a valid JSON object with this exact structure:
{{
  "relevance": <float 0-10>,
  "clarity": <float 0-10>,
  "technical_accuracy": <float 0-10>,
  "confidence": <float 0-10>,
  "overall": <average of above>,
  "feedback": "<2-3 sentence overall feedback>",
  "keywords_matched": ["<key term 1>", "<key term 2>"],
  "improvement_tips": ["<tip 1>", "<tip 2>", "<tip 3>"]
}}"""


# ──────────────────────────────────────────────────────────────────────────
# Cached resources
# ──────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def get_whisper_model():
    """Load the Whisper model, falling back to 'tiny' if the configured
    size fails to load (e.g. OOM on Streamlit Cloud's free 1GB tier)."""
    try:
        return WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
    except Exception as e:
        if WHISPER_MODEL_SIZE != "tiny":
            st.warning(
                f"Could not load Whisper model '{WHISPER_MODEL_SIZE}' ({e}). "
                "Falling back to 'tiny'."
            )
            return WhisperModel("tiny", device="cpu", compute_type="int8")
        raise


def get_questions(role: str, count: int = 5):
    pool = QUESTION_BANK.get(role, QUESTION_BANK["SDE"])
    return random.sample(pool, min(count, len(pool)))


def text_to_speech(text: str) -> bytes:
    tts = gTTS(text=text, lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


def transcribe_audio(audio_bytes: bytes, suffix: str = ".wav") -> str:
    model = get_whisper_model()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        segments, _info = model.transcribe(tmp_path, beam_size=5, language="en")
        return " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        os.unlink(tmp_path)


def score_answer(role: str, question: str, answer: str) -> dict:
    prompt = SCORING_PROMPT.format(role=role, question=question, answer=answer)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw.strip())
    dims = ["relevance", "clarity", "technical_accuracy", "confidence"]
    result["overall"] = round(sum(result[d] for d in dims) / 4, 2)
    return result


# ──────────────────────────────────────────────────────────────────────────
# PDF report (unchanged from ReportLab service)
# ──────────────────────────────────────────────────────────────────────────

def generate_report(session_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", parent=styles["Title"],
        fontSize=22, textColor=colors.HexColor("#1a1a2e"), spaceAfter=4)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#4a4a8a"), spaceAfter=12)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2d2d72"), spaceBefore=14, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, leading=15, textColor=colors.HexColor("#333333"))
    tip_style = ParagraphStyle("Tip", parent=styles["Normal"],
        fontSize=9, leading=13, textColor=colors.HexColor("#555555"), leftIndent=10)

    elements = []
    role = session_data.get("role", "Software Engineer")
    candidate = session_data.get("candidate_name", "Candidate")
    date_str = datetime.now().strftime("%B %d, %Y")
    scores_list = session_data.get("scores", [])
    questions = session_data.get("questions", [])
    answers = session_data.get("answers", [])

    elements.append(Paragraph("AI Interview Coach", title_style))
    elements.append(Paragraph(f"Performance Report — {role} | {date_str}", subtitle_style))
    elements.append(Paragraph(f"Candidate: <b>{candidate}</b>", body_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2d2d72"), spaceAfter=12))

    avg_scores = {"Relevance": 0, "Clarity": 0, "Technical Accuracy": 0, "Confidence": 0, "Overall": 0}
    if scores_list:
        for s in scores_list:
            avg_scores["Relevance"] += s.get("relevance", 0)
            avg_scores["Clarity"] += s.get("clarity", 0)
            avg_scores["Technical Accuracy"] += s.get("technical_accuracy", 0)
            avg_scores["Confidence"] += s.get("confidence", 0)
            avg_scores["Overall"] += s.get("overall", 0)
        n = len(scores_list)
        avg_scores = {k: round(v / n, 1) for k, v in avg_scores.items()}

    elements.append(Paragraph("Overall Performance", heading_style))

    def score_bar(score):
        filled = int(score)
        return "█" * filled + "░" * (10 - filled) + f"  {score}/10"

    summary_data = [["Dimension", "Score", "Visual"]]
    for dim, val in avg_scores.items():
        summary_data.append([dim, f"{val}/10", score_bar(val)])

    t = Table(summary_data, colWidths=[55 * mm, 25 * mm, 80 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d2d72")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f0f0f8"), colors.white]),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("FONTNAME", (2, 1), (2, -1), "Courier"),
        ("TEXTCOLOR", (2, 1), (2, -1), colors.HexColor("#2d2d72")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Question-by-Question Breakdown", heading_style))
    for i, (q, a, s) in enumerate(zip(questions, answers, scores_list), 1):
        block = []
        block.append(Paragraph(f"<b>Q{i}:</b> {q}", body_style))
        block.append(Spacer(1, 3))
        ans_text = a if len(a) <= 300 else a[:300] + "..."
        block.append(Paragraph(f"<i>Answer:</i> {ans_text}", tip_style))
        block.append(Spacer(1, 4))

        scores_row = [
            ["Relevance", "Clarity", "Tech Accuracy", "Confidence", "Overall"],
            [f"{s.get('relevance',0)}/10", f"{s.get('clarity',0)}/10",
             f"{s.get('technical_accuracy',0)}/10", f"{s.get('confidence',0)}/10",
             f"{s.get('overall',0)}/10"],
        ]
        mini_t = Table(scores_row, colWidths=[32 * mm] * 5)
        mini_t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8f4")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#bbbbcc")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        block.append(mini_t)
        block.append(Spacer(1, 4))
        block.append(Paragraph(f"<b>Feedback:</b> {s.get('feedback','')}", body_style))
        block.append(Spacer(1, 3))

        tips = s.get("improvement_tips", [])
        if tips:
            block.append(Paragraph("<b>Improvement Tips:</b>", body_style))
            for tip in tips:
                block.append(Paragraph(f"• {tip}", tip_style))

        block.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd"),
                                 spaceAfter=8, spaceBefore=8))
        elements.append(KeepTogether(block))

    overall = avg_scores.get("Overall", 0)
    if overall >= 7.5:
        verdict = "Strong Candidate — You demonstrated solid knowledge. Focus on depth in weak areas."
        verdict_color = "#1a7a1a"
    elif overall >= 5:
        verdict = "Promising — Good foundation with room to grow. Review flagged topics before your next interview."
        verdict_color = "#8a6a00"
    else:
        verdict = "Needs Work — Revisit the fundamentals and practice structured answers using the STAR method."
        verdict_color = "#8a1a1a"

    verdict_style = ParagraphStyle("Verdict", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor(verdict_color), leading=16)
    elements.append(Paragraph("Final Verdict", heading_style))
    elements.append(Paragraph(verdict, verdict_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Generated by AI Interview Coach • Practice makes perfect.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                       textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(elements)
    return buffer.getvalue()


# ──────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "stage": "role_select",   # role_select -> interview -> summary
        "role": None,
        "candidate_name": "Candidate",
        "questions": [],
        "current_index": 0,
        "answers": [],
        "scores": [],
        "last_audio_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session():
    for k in ["stage", "role", "questions", "current_index", "answers", "scores", "last_audio_id"]:
        if k in st.session_state:
            del st.session_state[k]
    init_state()


init_state()

st.title("🎙️ AI Interview Coach")
st.caption("Real-time voice interview simulator — scored on relevance, clarity, technical accuracy, and confidence.")

# ──────────────────────────────────────────────────────────────────────────
# Stage 1 — role selection
# ──────────────────────────────────────────────────────────────────────────

if st.session_state.stage == "role_select":
    st.session_state.candidate_name = st.text_input("Your name", value=st.session_state.candidate_name)
    role = st.selectbox("Choose the role you're interviewing for", list(QUESTION_BANK.keys()))
    num_q = st.slider("Number of questions", 3, 8, 5)

    if st.button("Start Interview", type="primary"):
        st.session_state.role = role
        st.session_state.questions = get_questions(role, num_q)
        st.session_state.current_index = 0
        st.session_state.answers = []
        st.session_state.scores = []
        st.session_state.stage = "interview"
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# Stage 2 — interview loop
# ──────────────────────────────────────────────────────────────────────────

elif st.session_state.stage == "interview":
    idx = st.session_state.current_index
    total = len(st.session_state.questions)
    question = st.session_state.questions[idx]

    st.progress(idx / total, text=f"Question {idx + 1} of {total}")
    st.subheader(f"Q{idx + 1}. {question}")

    with st.spinner("Loading question audio..."):
        try:
            audio_bytes = text_to_speech(question)
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.warning(f"Could not generate question audio: {e}")

    st.markdown("**Record or upload your answer:**")
    mic_audio = st.audio_input("Record your answer")
    uploaded_audio = st.file_uploader("...or upload an audio file", type=["wav", "mp3", "m4a", "webm"])

    answer_audio = mic_audio or uploaded_audio

    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.button("Submit Answer", type="primary", disabled=answer_audio is None)
    with col2:
        skip = st.button("Skip Question")

    if submit and answer_audio is not None:
        with st.spinner("Transcribing your answer..."):
            audio_bytes = answer_audio.getvalue() if hasattr(answer_audio, "getvalue") else answer_audio.read()
            transcript = transcribe_audio(audio_bytes)

        if not transcript:
            st.error("Could not transcribe audio — please speak clearly and try again.")
        else:
            st.info(f"**Transcript:** {transcript}")
            with st.spinner("Scoring your answer with AI..."):
                try:
                    score = score_answer(st.session_state.role, question, transcript)
                except Exception as e:
                    st.error(f"Scoring failed: {e}")
                    score = None

            if score:
                st.session_state.answers.append(transcript)
                st.session_state.scores.append(score)
                st.session_state.current_index += 1
                if st.session_state.current_index >= total:
                    st.session_state.stage = "summary"
                st.rerun()

    if skip:
        st.session_state.answers.append("(skipped)")
        st.session_state.scores.append({
            "relevance": 0, "clarity": 0, "technical_accuracy": 0, "confidence": 0,
            "overall": 0, "feedback": "Question skipped.", "improvement_tips": []
        })
        st.session_state.current_index += 1
        if st.session_state.current_index >= total:
            st.session_state.stage = "summary"
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# Stage 3 — summary + PDF
# ──────────────────────────────────────────────────────────────────────────

elif st.session_state.stage == "summary":
    st.success("Interview complete!")

    scores = st.session_state.scores
    avg = round(sum(s["overall"] for s in scores) / len(scores), 2) if scores else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Role", st.session_state.role)
    c2.metric("Questions Answered", len(scores))
    c3.metric("Average Score", f"{avg}/10")

    for i, (q, a, s) in enumerate(zip(st.session_state.questions, st.session_state.answers, scores), 1):
        with st.expander(f"Q{i}: {q}"):
            st.write(f"**Your answer:** {a}")
            st.write(
                f"Relevance: {s['relevance']}/10 · Clarity: {s['clarity']}/10 · "
                f"Technical Accuracy: {s['technical_accuracy']}/10 · Confidence: {s['confidence']}/10"
            )
            st.write(f"**Feedback:** {s.get('feedback', '')}")
            tips = s.get("improvement_tips", [])
            if tips:
                st.write("**Improvement tips:**")
                for tip in tips:
                    st.write(f"- {tip}")

    session_data = {
        "role": st.session_state.role,
        "candidate_name": st.session_state.candidate_name,
        "questions": st.session_state.questions,
        "answers": st.session_state.answers,
        "scores": scores,
    }
    pdf_bytes = generate_report(session_data)

    st.download_button(
        "Download PDF Report",
        data=pdf_bytes,
        file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        type="primary",
    )

    if st.button("Start a New Interview"):
        reset_session()
        st.rerun()