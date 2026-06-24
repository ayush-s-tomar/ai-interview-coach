import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from services.interview_service import get_questions, score_answer
from services.whisper_service import transcribe_audio
from models.schemas import RoleSelection

router = APIRouter()

# In-memory session store (use Redis in production)
sessions: dict = {}

@router.post("/start")
def start_session(payload: RoleSelection):
    """Start a new interview session and get questions."""
    session_id = str(uuid.uuid4())
    questions = get_questions(payload.role, count=5)
    sessions[session_id] = {
        "role": payload.role,
        "questions": questions,
        "current_index": 0,
        "scores": [],
        "answers": [],
    }
    return {
        "session_id": session_id,
        "role": payload.role,
        "total_questions": len(questions),
        "first_question": questions[0],
        "question_number": 1,
    }

@router.post("/transcribe-and-score")
async def transcribe_and_score(
    session_id: str = Form(...),
    question_number: int = Form(...),
    audio: UploadFile = File(...)
):
    """Receive audio, transcribe it, score the answer, return results."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    audio_bytes = await audio.read()
    
    # Transcribe
    transcript = transcribe_audio(audio_bytes, filename=audio.filename or "audio.webm")
    if not transcript:
        raise HTTPException(status_code=400, detail="Could not transcribe audio. Please speak clearly.")
    
    # Score
    q_index = question_number - 1
    question = session["questions"][q_index]
    score = score_answer(session["role"], question, transcript)
    
    session["scores"].append(score)
    session["answers"].append(transcript)
    session["current_index"] = question_number
    
    # Determine next question
    next_q = None
    is_complete = question_number >= len(session["questions"])
    if not is_complete:
        next_q = session["questions"][question_number]
    
    return {
        "transcript": transcript,
        "score": score,
        "is_complete": is_complete,
        "next_question": next_q,
        "next_question_number": question_number + 1 if not is_complete else None,
    }

@router.get("/session/{session_id}/summary")
def get_summary(session_id: str, candidate_name: str = "Candidate"):
    """Get full session summary for report generation."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    scores = session["scores"]
    avg = round(sum(s["overall"] for s in scores) / len(scores), 2) if scores else 0
    
    return {
        "session_id": session_id,
        "role": session["role"],
        "candidate_name": candidate_name,
        "questions": session["questions"][:len(scores)],
        "answers": session["answers"],
        "scores": scores,
        "total_questions": len(scores),
        "average_score": avg,
    }
