from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from services.report_service import generate_report
from routers.interview import sessions

router = APIRouter()

@router.get("/generate/{session_id}")
def generate_pdf_report(session_id: str, candidate_name: str = "Candidate"):
    """Generate and return a PDF report for a completed session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    scores = session.get("scores", [])
    if not scores:
        raise HTTPException(status_code=400, detail="No answers scored yet")
    
    avg = round(sum(s["overall"] for s in scores) / len(scores), 2)
    
    session_data = {
        "session_id": session_id,
        "role": session["role"],
        "candidate_name": candidate_name,
        "questions": session["questions"][:len(scores)],
        "answers": session["answers"],
        "scores": scores,
        "average_score": avg,
    }
    
    pdf_bytes = generate_report(session_data)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="interview_report_{session_id[:8]}.pdf"'
        }
    )
