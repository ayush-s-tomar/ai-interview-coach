import os
import tempfile
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

_model = None

def get_model():
    global _model
    if _model is None:
        model_size = os.getenv("WHISPER_MODEL", "base")
        print(f"[Whisper] Loading model: {model_size}")
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio bytes using faster-whisper."""
    model = get_model()
    
    suffix = os.path.splitext(filename)[-1] or ".webm"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    
    try:
        segments, info = model.transcribe(tmp_path, beam_size=5, language="en")
        transcript = " ".join(seg.text.strip() for seg in segments)
        print(f"[Whisper] Transcribed ({info.language}): {transcript[:80]}...")
        return transcript.strip()
    finally:
        os.unlink(tmp_path)
