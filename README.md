# ⚡ SalesAI – AI-Powered Sales Call Analysis Co-Pilot

SalesAI is an intelligent Streamlit-based application that analyzes sales conversations in real time or from uploaded audio files.  
It uses **state-of-the-art LLMs** to extract **sentiment, intent, key entities**, and provides **actionable next-step suggestions** for sales agents.

The project includes **two fully functional AI engines**:
- 🔹 **Gemini 2.5 Flash**
- 🔹 **Groq (LLaMA 3.3 – 70B)**

---

## 🚀 Features

### 🎙️ Live Sales Co-Pilot
- Record customer speech directly from microphone
- Real-time transcription
- AI-powered analysis of customer intent & sentiment
- Smart follow-up suggestions for sales agents

### 📁 Sales Call File Analysis
- Upload recorded sales calls (WAV format)
- Automatic silence-based audio chunking
- Role detection (Customer vs Sales Agent)
- Structured AI insights per customer message

### 🧠 AI Insights
- **Sentiment Analysis** (Positive / Neutral / Negative)
- **Intent Detection** (Buy, Pricing, Inquiry, Complaint, etc.)
- **Entity Extraction** (Brand, Product, Budget, Topic)
- **Sales Strategy Suggestions**
- Built-in **rule-based fallback engine** if API key is missing

### 🎨 Modern SaaS UI
- Dark theme
- Chat-style conversation bubbles
- 3-column analytical dashboard
- Clean, professional Streamlit layout

---

## 🧩 Project Structure

SalesAI/     
│       
├── Infosys Agile & Daily Sprint Record.xlsx               
├── LICENSE        
├── README.md        
├── Real_Time_Sales_Intelligence.pdf.pdf          
├── final_gemini.py # SalesAI using Gemini 2.5 Flash     
├── final_groq.py # SalesAI using Groq (LLaMA 3.3)       
└── requirements.txt           
    
---

## 🤖 AI Engines Used

### 🔹 Gemini Version
- Model: **gemini-2.5-flash**
- Provider: Google Generative AI
- Strengths: Balanced reasoning, structured JSON output

### 🔹 Groq Version
- Model: **llama-3.3-70b-versatile**
- Provider: Groq
- Strengths: Ultra-fast inference, high-quality reasoning

---

## 🔑 API Keys Required

You need **one API key depending on the version you run**.

### Gemini API Key
Get from:  
👉 https://aistudio.google.com/app/apikey

### Groq API Key
Get from:  
👉 https://console.groq.com/keys

> API keys are entered securely inside the app sidebar.

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository

git clone [https://github.com/your-username/SalesAI.git](https://github.com/AryaJagtap/SalesAI.git)       
cd SalesAI 

### 2️⃣ Create Virtual Environment (Recommended)

python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

### 3️⃣ Install Dependencies

pip install -r requirements.txt

### 4️⃣ Install FFmpeg (Required for Audio Processing)

Windows:
https://ffmpeg.org/download.html
(Add FFmpeg to PATH)

Linux
sudo apt install ffmpeg

macOS
brew install ffmpeg

### ▶️ Running the Application
🔹 Run Gemini Version      
streamlit run final_gemini.py

🔹 Run Groq Version       
streamlit run final_groq.py
