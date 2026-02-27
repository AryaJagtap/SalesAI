import { useState, useEffect, useRef } from 'react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import EngineToggle from '../components/EngineToggle';
import ChatBubble from '../components/ChatBubble';
import AnalysisCard from '../components/AnalysisCard';
import SuggestionPanel from '../components/SuggestionPanel';
import TranscriptDownload from '../components/TranscriptDownload';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function LiveCopilot({ engine, onEngineChange }) {
    const [sessionId, setSessionId] = useState('');
    const [conversation, setConversation] = useState([]);
    const [error, setError] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const { isRecording, isProcessing, startRecording, stopRecording } = useAudioRecorder();
    const feedEndRef = useRef(null);

    useEffect(() => {
        createSession();
    }, []);

    useEffect(() => {
        feedEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    const createSession = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/session/new`, { method: 'POST' });
            const data = await res.json();
            setSessionId(data.session_id);
        } catch {
            setSessionId(`local-${Date.now()}`);
        }
    };

    const handleRecord = async () => {
        setError('');
        if (isRecording) {
            try {
                const text = await stopRecording();
                if (text) {
                    await analyzeText(text);
                }
            } catch (err) {
                setError(err.message);
            }
        } else {
            try {
                await startRecording();
            } catch (err) {
                setError(err.message);
            }
        }
    };

    const analyzeText = async (text) => {
        setIsAnalyzing(true);
        const tempEntry = { speaker: 'Customer', text, analysis: null, timestamp: new Date().toLocaleTimeString() };
        setConversation(prev => [...prev, tempEntry]);

        try {
            const res = await fetch(`${API_BASE}/api/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text,
                    session_id: sessionId,
                    speed_first: engine === 'groq',
                    preferred_engine: engine,
                }),
            });

            const analysis = await res.json();

            setConversation(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = { ...tempEntry, analysis };
                return updated;
            });
        } catch (err) {
            setError('Analysis failed. Is the backend running?');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const clearConversation = async () => {
        try {
            await fetch(`${API_BASE}/api/session/${sessionId}`, { method: 'DELETE' });
        } catch { /* ignore */ }
        setConversation([]);
        createSession();
    };

    const downloadSegments = conversation.map(c => ({
        speaker: c.speaker,
        text: c.text,
        timestamp: c.timestamp || '',
    }));

    return (
        <div className="fade-in">
            <div className="page-header">
                <h2>🎙️ Live Sales Co-Pilot</h2>
                <p>Record the customer's voice. AI analyzes sentiment, intent, and suggests the best next question in real-time.</p>
            </div>

            {/* Toolbar */}
            <div className="toolbar">
                <button
                    className={`btn btn-primary record-btn ${isRecording ? 'recording' : ''}`}
                    onClick={handleRecord}
                    disabled={isProcessing || isAnalyzing}
                    style={{ flex: 'none' }}
                >
                    {isRecording ? (
                        <>🔴 Stop Recording</>
                    ) : isProcessing ? (
                        <><span className="spinner" /> Transcribing...</>
                    ) : isAnalyzing ? (
                        <><span className="spinner" /> Analyzing...</>
                    ) : (
                        <>🎙️ Start Recording</>
                    )}
                </button>

                <div className="toolbar-separator" />

                <EngineToggle engine={engine} onToggle={onEngineChange} />

                {conversation.length > 0 && (
                    <>
                        <div className="toolbar-separator" />
                        <button className="btn btn-danger" onClick={clearConversation}>
                            🗑️ Clear
                        </button>
                    </>
                )}
            </div>

            {error && (
                <div className="error-alert">
                    ⚠️ {error}
                </div>
            )}

            {/* Conversation Feed */}
            <div style={{ marginTop: '16px' }}>
                {conversation.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">🎙️</div>
                        <div className="empty-state-title">Ready to listen</div>
                        <div className="empty-state-text">
                            Click the record button to capture customer audio. AI will analyze each message and suggest your next best move.
                        </div>
                    </div>
                ) : (
                    <div className="chat-timeline">
                        {conversation.map((item, index) => (
                            <div key={index} className="slide-up">
                                <ChatBubble
                                    speaker={item.speaker}
                                    text={item.text}
                                    timestamp={item.timestamp}
                                />
                                {item.analysis && (
                                    <>
                                        <AnalysisCard analysis={item.analysis} />
                                        <SuggestionPanel
                                            suggestion={item.analysis.suggestion}
                                            reasoning={item.analysis.reasoning}
                                        />
                                    </>
                                )}
                            </div>
                        ))}
                        <div ref={feedEndRef} />
                    </div>
                )}
            </div>

            {conversation.length > 0 && (
                <TranscriptDownload segments={downloadSegments} />
            )}
        </div>
    );
}
