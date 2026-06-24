# 🎙️ AI Interview Coach

> Real-time voice interview simulator that scores answers on relevance, clarity, and depth — generates a personalized PDF feedback report.

## ✨ Features
- 🎤 **Voice Recording** — Record answers in-browser using MediaRecorder API
- 🔊 **Text-to-Speech Questions** — Questions read aloud via gTTS
- ⚡ **Instant Transcription** — Faster-Whisper transcribes your answer locally
- 🧠 **AI Scoring via Groq** — Llama3-70b scores on 4 dimensions (no GPU required)
- 📄 **PDF Report** — ReportLab generates a detailed feedback report
- 🎯 **3 Roles** — SDE, AI Engineer, Data Analyst (5 questions each)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.11 |
| Transcription | Faster-Whisper (local, CPU) |
| AI Scoring | Groq API (Llama3-70b-8192) |
| TTS | gTTS (Google Text-to-Speech) |
| PDF | ReportLab |
| Frontend | React + Vite |
| Deployment | Docker + docker-compose |

---

## 🚀 Setup Instructions

### Step 1: Get a Groq API Key (Free)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → Go to **API Keys** → Create new key
3. Copy the key — it starts with `gsk_`

---

### Step 2: Clone and Configure

```bash
# Navigate into the project
cd ai-interview-coach

# Copy the environment file
cp .env.example .env

# Edit .env and paste your Groq key
nano .env   # or use any editor
```

Your `.env` should look like:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

---

### Option A: Run with Docker (Recommended)

**Prerequisites:** Docker + Docker Compose installed

```bash
# Build and start both services
docker compose up --build

# Access the app at:
# Frontend: http://localhost:3000
# API docs:  http://localhost:8000/docs
```

To stop:
```bash
docker compose down
```

---

### Option B: Run Locally (Manual)

**Prerequisites:** Python 3.11+, Node.js 18+, ffmpeg

#### Backend Setup

```bash
cd backend

# Install ffmpeg (required by faster-whisper)
# Ubuntu/Debian:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg
# Windows: download from https://ffmpeg.org/download.html

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies (takes ~2 min, downloads Whisper model)
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start the backend
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev

# Open: http://localhost:5173
```

---

## 📁 Project Structure

```
ai-interview-coach/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── routers/
│   │   ├── interview.py         # /api/interview/* endpoints
│   │   ├── tts.py               # /api/tts/speak endpoint
│   │   └── report.py            # /api/report/generate/* endpoint
│   ├── services/
│   │   ├── interview_service.py # Question bank + Groq scoring
│   │   ├── whisper_service.py   # Faster-Whisper transcription
│   │   ├── tts_service.py       # gTTS audio generation
│   │   └── report_service.py    # ReportLab PDF generation
│   └── models/
│       └── schemas.py           # Pydantic data models
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component + state
│   │   ├── components/
│   │   │   ├── RoleSelector.jsx # Role/name selection screen
│   │   │   ├── InterviewRoom.jsx# Main interview UI
│   │   │   └── ScoreCard.jsx    # Per-question score display
│   │   ├── hooks/
│   │   │   └── useRecorder.js   # MediaRecorder hook
│   │   └── utils/
│   │       └── api.js           # Axios API calls
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interview/start` | Start session, get first question |
| POST | `/api/interview/transcribe-and-score` | Submit audio, get transcript + score |
| GET | `/api/interview/session/{id}/summary` | Get full session results |
| POST | `/api/tts/speak` | Convert text to MP3 audio |
| GET | `/api/report/generate/{id}` | Download PDF report |

Interactive API docs: **http://localhost:8000/docs**

---

## 💡 How It Works (Flow)

```
User selects role
      ↓
Backend returns 5 random questions from question bank
      ↓
Question is sent to /api/tts/speak → gTTS returns MP3 → plays in browser
      ↓
User clicks microphone button → MediaRecorder records WebM audio
      ↓
Audio sent to /api/interview/transcribe-and-score
      ↓
Faster-Whisper transcribes audio text (local, CPU)
      ↓
Groq (Llama3-70b) scores the transcript on 4 dimensions
      ↓
Scores + feedback shown in UI
      ↓
After all 5 questions → "Download PDF Report"
      ↓
ReportLab generates styled PDF with per-question breakdown
```

---

## 🎯 Scoring Dimensions

| Dimension | What's Measured |
|-----------|----------------|
| **Relevance** (0-10) | Did you answer what was asked? |
| **Clarity** (0-10) | Was your answer well-structured? |
| **Technical Accuracy** (0-10) | Was the content technically correct? |
| **Confidence** (0-10) | Did you avoid hedging phrases? |

---

## 🐛 Troubleshooting

**Whisper model download on first run:**
The first run downloads the Whisper `base` model (~140MB). This is cached locally. Change `WHISPER_MODEL=tiny` in `.env` for faster startup.

**Microphone not working:**
The browser requires HTTPS or localhost for microphone access. In development on `localhost` it works fine.

**Groq rate limits:**
The free tier of Groq allows ~30 req/min which is well above what this app needs.

**ffmpeg not found:**
Faster-Whisper requires ffmpeg to be installed on the system (not via pip).

---

## 📈 Resume Line

> "Built a real-time voice interview simulator with Faster-Whisper transcription, Groq LLM scoring on 4 dimensions (relevance, clarity, technical accuracy, confidence), and automated PDF feedback reports using ReportLab — deployed via Docker."
