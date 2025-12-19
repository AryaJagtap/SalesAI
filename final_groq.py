"""
Sales Call Analysis - Groq Edition (Llama 3.3)
Author: AJAX
Features:
- Engine: Groq (llama-3.3-70b-versatile) for lightning-fast analysis
- UI: Modern SaaS UI with detailed 3-Column Breakdown
- Logic: Sentiment, Intent, Entities, and Sales Suggestions
"""

import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import tempfile
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import requests
import json
import pandas as pd

# NEW IMPORT
from groq import Groq

# ================== 1. PAGE CONFIG & STYLING ==================
st.set_page_config(
    page_title="SalesAI Co-Pilot (Groq)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    div.stButton > button {
        width: 100%; background-color: #21262d; color: #c9d1d9;
        border: 1px solid #30363d; border-radius: 6px; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background-color: #30363d; color: #58a6ff; border-color: #8b949e; }
    
    /* BUBBLES */
    .chat-bubble { padding: 15px; border-radius: 15px; max-width: 80%; line-height: 1.5; margin-bottom: 10px; }
    .customer-bubble { background-color: #238636; color: white; align-self: flex-start; border-bottom-left-radius: 2px; }
    
    /* ANALYSIS CARDS */
    .metric-card {
        background-color: #161b22; border: 1px solid #30363d;
        border-radius: 8px; padding: 15px; margin-bottom: 10px;
    }
    .metric-header { color: #8b949e; font-size: 0.9em; font-weight: bold; margin-bottom: 5px; }
    .metric-value { color: #58a6ff; font-family: monospace; font-size: 0.9em; }
    
    .suggestion-box { 
        background: linear-gradient(90deg, #d23600 0%, #ff5722 100%); /* Orange for Groq Theme */
        padding: 15px; border-radius: 8px; margin-top: 10px; color: white; font-weight: 500; 
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. LOGIC FUNCTIONS ==================

def legacy_rule_engine(text):
    """Fallback logic if API fails"""
    text_l = text.lower()
    intent = "General Inquiry"
    sugg = "How can I help you today?"
    entities = []
    
    if any(w in text_l for w in ["price", "cost", "much"]):
        intent = "Pricing"
        sugg = "It depends on the model. What is your budget range?"
        entities.append({"entity": "Topic", "value": "Price"})
    elif any(w in text_l for w in ["buy", "want", "need"]):
        intent = "Purchase"
        sugg = "Great! Do you have a specific brand in mind?"
    
    if "samsung" in text_l: entities.append({"entity": "Brand", "value": "Samsung"})
    if "phone" in text_l: entities.append({"entity": "Product", "value": "Phone"})

    return {
        "sentiment": {"label": "Neutral", "score": 0.5},
        "intent": {"label": intent, "score": 1.0},
        "entities": entities,
        "suggestion": sugg,
        "reasoning": "⚠️ Standard rule-based fallback (Key missing or API error)."
    }

def analyze_with_groq(text, api_key):
    """Call Groq API (Llama 3.3)"""
    if not api_key or len(api_key) < 10:
        return legacy_rule_engine(text)

    try:
        client = Groq(api_key=api_key)
        
        system_prompt = """
        You are an expert Sales Coach AI. 
        Analyze the customer's input and return a JSON object.
        Structure:
        {
            "sentiment": { "label": "Positive/Neutral/Negative", "score": 0.0-1.0 },
            "intent": { "label": "Short Intent Name", "score": 0.0-1.0 },
            "entities": [ { "entity": "Type", "value": "Extracted Data" } ],
            "suggestion": "The PERFECT next question for the sales agent.",
            "reasoning": "Why this suggestion works."
        }
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Customer said: '{text}'"}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.choices[0].message.content)
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        return legacy_rule_engine(text)

def transcribe_audio(audio_chunk, fs):
    filename = "temp_chunk.wav"
    wavfile.write(filename, fs, audio_chunk)
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        try:
            audio = r.record(source)
            return r.recognize_google(audio, language="en-IN")
        except: return None

# ================== 3. APP LOGIC ==================

# --- INITIALIZATION ---
if 'page' not in st.session_state: st.session_state.page = 'Live'
if 'live_transcript' not in st.session_state: st.session_state.live_transcript = []
if 'transcript' not in st.session_state: st.session_state.transcript = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ SalesAI")
    st.markdown("---")
    if st.button("🎙️ Live Co-Pilot"): st.session_state.page = 'Live'
    if st.button("📁 File Analysis"): st.session_state.page = 'Upload'
    st.markdown("---")
    
    st.markdown("### 🚀 Groq Configuration")
    user_key_input = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    if user_key_input:
        st.session_state.active_key = user_key_input
        st.success("✅ Groq Connected")
    else:
        st.session_state.active_key = None
        st.warning("⚠️ No Key Provided")

# --- LIVE PAGE ---
if st.session_state.page == 'Live':
    st.markdown("## 🎙️ Live Sales Co-Pilot (Groq Powered)")
    st.markdown("Record the customer. Llama 3.3 will analyze and suggest tactics instantly.")
    
    if st.button("🔴 Record Customer Input (5s)", type="primary"):
        with st.spinner("Listening..."):
            fs = 16000; sec = 5
            rec = sd.rec(int(sec * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            text = transcribe_audio(rec, fs)
            
            if text:
                current_key = st.session_state.get("active_key", None)
                with st.spinner("⚡ Groq is thinking..."):
                    analysis = analyze_with_groq(text, current_key)
                
                st.session_state.live_transcript.append({
                    "speaker": "Customer", "text": text, "analysis": analysis
                })
            else:
                st.warning("No speech detected.")

    st.markdown("---")
    st.subheader("💬 Co-Pilot Feed")
    
    for item in st.session_state.live_transcript:
        # 1. Customer Text
        st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:flex-start;">
            <div class="chat-bubble customer-bubble">
                <strong>Customer:</strong> {item['text']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Detailed Analysis Panel
        if item['analysis']:
            data = item['analysis']
            
            # 3-Column Layout
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("""<div class="metric-header">🧠 Sentiment</div>""", unsafe_allow_html=True)
                st.code(json.dumps(data.get('sentiment'), indent=2), language="json")
            with c2:
                st.markdown("""<div class="metric-header">🎯 Intent</div>""", unsafe_allow_html=True)
                st.code(json.dumps(data.get('intent'), indent=2), language="json")
            with c3:
                st.markdown("""<div class="metric-header">🔍 Entities</div>""", unsafe_allow_html=True)
                st.code(json.dumps(data.get('entities'), indent=2), language="json")

            # Suggestion Box
            st.markdown(f"""
            <div class="suggestion-box">
                💡 <strong>Suggested Reply:</strong><br>"{data.get('suggestion')}"
            </div>
            <div style="margin-top:5px; font-size:0.85em; color:#8b949e;">
                <i>Strategy: {data.get('reasoning')}</i>
            </div>
            <hr style="border-color: #30363d; margin-top: 20px;">
            """, unsafe_allow_html=True)

# --- UPLOAD PAGE ---
elif st.session_state.page == 'Upload':
    st.markdown("## 📁 File Analysis")
    uploaded_file = st.file_uploader("Upload Sales Call (WAV)", type=["wav"])
    
    if uploaded_file and st.button("Start Processing"):
        st.session_state.transcript = [] 
        current_key = st.session_state.get("active_key", None)
        
        with st.spinner("Processing with Llama 3.3..."):
            r = sr.Recognizer()
            audio = AudioSegment.from_wav(uploaded_file)
            chunks = split_on_silence(audio, min_silence_len=300, silence_thresh=audio.dBFS-16, keep_silence=200)
            
            for chunk in chunks:
                f = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                f.close()
                try:
                    chunk.export(f.name, format="wav")
                    with sr.AudioFile(f.name) as source:
                        try:
                            aud = r.record(source)
                            text = r.recognize_google(aud)
                            role = "Sales Agent"
                            if any(w in text.lower() for w in ["i want", "price", "show me", "hello"]): role = "Customer"
                            
                            analysis = None
                            if role == "Customer":
                                analysis = analyze_with_groq(text, current_key)
                                
                            st.session_state.transcript.append({"role": role, "text": text, "analysis": analysis})
                        except: pass
                finally:
                    if os.path.exists(f.name): os.remove(f.name)

    if st.session_state.transcript:
        for item in st.session_state.transcript:
            if item['role'] == "Sales Agent":
                 st.markdown(f"**Agent:** {item['text']}")
            else:
                st.markdown(f"""
                <div class="chat-bubble customer-bubble">
                    <strong>Customer:</strong> {item['text']}
                </div>
                """, unsafe_allow_html=True)
                
                if item['analysis']:
                    data = item['analysis']
                    c1, c2, c3 = st.columns(3)
                    with c1: st.code(json.dumps(data.get('sentiment'), indent=2), language="json")
                    with c2: st.code(json.dumps(data.get('intent'), indent=2), language="json")
                    with c3: st.code(json.dumps(data.get('entities'), indent=2), language="json")
                    
                    st.info(f"💡 Suggestion: {data.get('suggestion')}")
            st.markdown("---")