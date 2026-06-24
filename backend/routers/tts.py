from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from services.tts_service import text_to_speech

router = APIRouter()

class TTSRequest(BaseModel):
    text: str

@router.post("/speak")
def speak(req: TTSRequest):
    """Convert text to speech and return MP3 audio."""
    audio_bytes = text_to_speech(req.text)
    return Response(content=audio_bytes, media_type="audio/mpeg")
