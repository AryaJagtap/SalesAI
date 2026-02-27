# 🚀 SalesAI V2.0 — Real-Time Sales Intelligence Platform

> **Upgraded version** of [SalesAI V1.0](https://github.com/AryaJagtap/SalesAI) — rebuilt from Streamlit to a production-grade React + FastAPI architecture.

SalesAI is a real-time AI-powered sales co-pilot that helps sales professionals close deals faster. It analyzes customer conversations, detects sentiment & intent, extracts key entities, and suggests the best next question — all in real-time.

**Works across ALL industries**: Retail, Real Estate, Insurance, Finance, Automotive, Groceries, Services, B2B, and more.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎙️ **Live Co-Pilot** | Record customer audio in real-time and get AI-powered suggestions |
| 📁 **File Analysis** | Upload recorded sales calls for full transcript + analysis |
| 🧠 **Sentiment Analysis** | Detect customer mood (Positive / Neutral / Negative) |
| 🎯 **Intent Detection** | Identify what the customer wants (Buy / Inquire / Compare / Budget / etc.) |
| 🔍 **Entity Extraction** | Extract brands, products, budgets, locations, services |
| 💡 **Smart Suggestions** | AI suggests the best next question for the sales agent |
| 🔄 **Dual AI Engine** | Toggle between Gemini and Groq with automatic fallback |
| 🌙 **Dark / Light Theme** | Emerald green theme with smooth toggle |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile |
| 📥 **Export Transcripts** | Download conversations as TXT or JSON |

---

## 🛠️ Tech Stack

### Frontend
- **React 18** + Vite (fast dev server & HMR)
- **Vanilla CSS** (custom design system, no frameworks)
- **Plus Jakarta Sans** font

### Backend
- **FastAPI** (async Python API)
- **Groq Whisper API** (primary transcription — whisper-large-v3)
- **faster-whisper** (local fallback transcription)
- **Google Gemini 2.5 Flash** (primary AI analysis)
- **Groq Llama 3.3 70B** (secondary AI analysis)
- **Pydantic V2** (data validation)

### AI Models
| Purpose | Primary | Secondary |
|---|---|---|
| Transcription | Groq Whisper `whisper-large-v3` | Local `faster-whisper` (tiny) |
| Analysis | Gemini `gemini-2.5-flash` | Groq `llama-3.3-70b-versatile` |

---

## 📂 Project Structure

```
SalesAI/
├── backend/                  # FastAPI backend
│   ├── .env.example          # Environment variables template
│   ├── config.py             # App settings
│   ├── main.py               # FastAPI entry point
│   ├── requirements.txt      # Python dependencies
│   ├── models/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── routers/
│   │   ├── analysis.py       # AI analysis endpoints
│   │   └── transcription.py  # Audio transcription endpoints
│   └── services/
│       ├── ai_engine.py      # Gemini + Groq AI analysis
│       ├── conversation.py   # Session memory management
│       └── transcriber.py    # Audio transcription + speaker detection
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx           # Main application
│   │   ├── index.css         # Design system (green theme)
│   │   ├── components/
│   │   │   ├── AnalysisCard.jsx
│   │   │   ├── ChatBubble.jsx
│   │   │   ├── EngineToggle.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── SuggestionPanel.jsx
│   │   │   └── TranscriptDownload.jsx
│   │   ├── hooks/
│   │   │   ├── useAudioRecorder.js
│   │   │   └── useTheme.js
│   │   └── pages/
│   │       ├── FileAnalysis.jsx
│   │       └── LiveCopilot.jsx
│   └── package.json
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Gemini API Key** → [Get from Google AI Studio](https://aistudio.google.com/app/apikey)
- **Groq API Key** → [Get from Groq Console](https://console.groq.com/keys)

### 1. Clone the Repository
```bash
git clone https://github.com/AryaJagtap/SalesAI.git
git checkout Version-2
cd SalesAI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Create .env file
copy .env.example .env      # Windows
# cp .env.example .env      # Mac/Linux

# Edit .env and add your API keys
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application
```bash
# Terminal 1 — Backend (from backend/ directory)
python -m uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend (from frontend/ directory)
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 🌐 Deployment

### Backend → Render (Free Tier)
1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `GEMINI_API_KEY`, `GROQ_API_KEY`

### Frontend → Vercel (Free Tier)
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. Settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add environment variable: `VITE_API_URL` = your Render backend URL (e.g., `https://salesai-backend.onrender.com`)

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GROQ_API_KEY` | Yes | Groq API key |
| `VITE_API_URL` | Frontend only | Backend URL for production |

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/transcribe` | Upload audio file for transcription |
| `POST` | `/api/transcribe/blob` | Transcribe live audio blob |
| `POST` | `/api/analyze` | Analyze customer text with AI |
| `POST` | `/api/session/new` | Create conversation session |
| `DELETE` | `/api/session/{id}` | Clear session history |
| `GET` | `/health` | Health check |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Arya Jagtap**
- GitHub: [@AryaJagtap](https://github.com/AryaJagtap)

---

> **SalesAI V2.0** — Built with ❤️ for sales professionals everywhere.
