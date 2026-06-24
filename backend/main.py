from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import interview, tts, report

app = FastAPI(title="AI Interview Coach API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(tts.router, prefix="/api/tts", tags=["TTS"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])

@app.get("/")
def root():
    return {"status": "AI Interview Coach API running"}
