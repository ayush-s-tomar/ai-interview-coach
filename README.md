# 🎙️ AI Interview Coach

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Deployed](https://img.shields.io/badge/Live-Vercel-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Real-time voice interview simulator that scores answers on relevance, clarity, and depth — generates a personalized PDF feedback report.

🔗 **[Live Demo](https://ai-interview-coach-two-dusky.vercel.app)** · **[API Docs](https://ai-interview-coach-65p8.onrender.com/docs)**

---

## 💡 Why I Built This

Every fresher faces the same problem — you can study DSA and system design, but nobody tells you how your actual answers sound in a real interview. I built this while preparing for interviews myself. It's the tool I wished existed.

---

## ✨ Features

- 🎯 **Role-based questions** — Software Engineer, AI/ML Engineer, Data Analyst
- 🎤 **Voice recording** — Answer questions verbally in real-time
- 🤖 **AI scoring** — Powered by Groq (LLaMA 3.3) across 4 dimensions:
  - Relevance · Clarity · Technical Accuracy · Confidence
- 📄 **PDF report** — Detailed per-question breakdown with improvement tips
- ⚡ **Fast transcription** — Faster-Whisper for accurate speech-to-text
- 🔒 **Privacy first** — No audio stored, transcription happens in-memory

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | React + Vite | Fast builds, clean component model |
| Backend | FastAPI + Python | Async support, automatic API docs |
| Transcription | Faster-Whisper | 4x faster than OpenAI Whisper |
| AI Scoring | Groq API (LLaMA 3.3 70B) | Free, fast inference |
| Text-to-Speech | gTTS | Lightweight, no API key needed |
| PDF Generation | ReportLab | Full control over layout |
| Deployment | Vercel + Render | Free tier, zero DevOps |
| Containerization | Docker + Docker Compose | One command setup |

---

## 🏗️ Architecture

```
User Browser
    │
    ▼
Vercel (React Frontend)
    │ /api/* proxy
    ▼
Render (FastAPI Backend)
    ├── Faster-Whisper → transcribe audio
    ├── Groq API → score answer
    ├── gTTS → speak question
    └── ReportLab → generate PDF
```

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/ayush-s-tomar/ai-interview-coach.git
cd ai-interview-coach

# Add your Groq API key
cp .env.example .env
# Edit .env and add GROQ_API_KEY=gsk_...

# Start with Docker
docker compose up --build
```

Frontend → http://localhost:3000  
API docs → http://localhost:8000/docs

---

## 📊 How It Works

```
1. Select role    →  SDE / AI Engineer / Data Analyst
2. Hear question  →  gTTS speaks the question aloud
3. Record answer  →  Browser captures audio via MediaRecorder
4. Transcribe     →  Faster-Whisper converts speech to text
5. Score          →  Groq LLaMA 3.3 scores on 4 dimensions
6. Download       →  ReportLab generates personalized PDF
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Get free at [console.groq.com](https://console.groq.com) |
| `WHISPER_MODEL` | `tiny` (fast) or `base` (accurate) |

---

## 📁 Project Structure

```
ai-interview-coach/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── interview.py         # Session + scoring endpoints
│   │   ├── tts.py               # Text-to-speech endpoint
│   │   └── report.py            # PDF generation endpoint
│   └── services/
│       ├── whisper_service.py   # Audio transcription
│       ├── interview_service.py # Question bank + AI scoring
│       ├── tts_service.py       # gTTS wrapper
│       └── report_service.py    # ReportLab PDF builder
├── frontend/
│   └── src/
│       ├── components/          # React UI components
│       └── hooks/               # useRecorder custom hook
└── docker-compose.yml
```

---

## 🗺️ Roadmap

- [ ] Add more roles (Product Manager, Data Engineer)
- [ ] Confidence detection via audio analysis
- [ ] Interview history dashboard
- [ ] Shareable report links

---

## 📄 License

MIT — free to use, modify and distribute.

---

*Built to solve a real problem — I made this while preparing for interviews myself.*