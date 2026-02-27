import { useState, useRef, useEffect } from 'react';
import EngineToggle from '../components/EngineToggle';
import ChatBubble from '../components/ChatBubble';
import AnalysisCard from '../components/AnalysisCard';
import SuggestionPanel from '../components/SuggestionPanel';
import TranscriptDownload from '../components/TranscriptDownload';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function FileAnalysis({ engine, onEngineChange }) {
    const [file, setFile] = useState(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [progress, setProgress] = useState(0);
    const [segments, setSegments] = useState([]);
    const [analyzedSegments, setAnalyzedSegments] = useState([]);
    const [error, setError] = useState('');
    const [sessionId, setSessionId] = useState('');
    const fileInputRef = useRef(null);

    useEffect(() => {
        createSession();
    }, []);

    const createSession = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/session/new`, { method: 'POST' });
            const data = await res.json();
            setSessionId(data.session_id);
        } catch {
            setSessionId(`local-${Date.now()}`);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) validateAndSetFile(droppedFile);
    };

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) validateAndSetFile(selectedFile);
    };

    const validateAndSetFile = (f) => {
        const allowed = ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm'];
        const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
        if (!allowed.includes(ext)) {
            setError(`Unsupported format: ${ext}. Supported: ${allowed.join(', ')}`);
            return;
        }
        if (f.size > 50 * 1024 * 1024) {
            setError('File too large. Maximum size is 50MB.');
            return;
        }
        setFile(f);
        setError('');
        setSegments([]);
        setAnalyzedSegments([]);
    };

    const processFile = async () => {
        if (!file) return;
        setIsProcessing(true);
        setProgress(10);
        setError('');
        setAnalyzedSegments([]);

        try {
            // Step 1: Transcribe
            const formData = new FormData();
            formData.append('file', file);
            setProgress(20);

            const res = await fetch(`${API_BASE}/api/transcribe`, {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Transcription failed');
            }

            const data = await res.json();
            setSegments(data.segments);
            setProgress(50);

            // Step 2: Analyze customer segments
            const analyzed = [];
            const customerSegments = data.segments.filter(s => s.speaker === 'Customer');
            const totalToAnalyze = customerSegments.length;

            for (let i = 0; i < data.segments.length; i++) {
                const seg = data.segments[i];
                let analysis = null;

                if (seg.speaker === 'Customer') {
                    try {
                        const aRes = await fetch(`${API_BASE}/api/analyze`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                text: seg.text,
                                session_id: sessionId,
                                speed_first: engine === 'groq',
                                preferred_engine: engine,
                            }),
                        });
                        analysis = await aRes.json();
                    } catch {
                        // Analysis failed for this segment, continue
                    }

                    const analyzedCount = analyzed.filter(a => a.analysis).length + 1;
                    setProgress(50 + Math.round((analyzedCount / Math.max(totalToAnalyze, 1)) * 45));
                }

                analyzed.push({ ...seg, analysis });
            }

            setAnalyzedSegments(analyzed);
            setProgress(100);
        } catch (err) {
            setError(err.message || 'Processing failed. Is the backend running?');
        } finally {
            setIsProcessing(false);
        }
    };

    const resetAll = async () => {
        setFile(null);
        setSegments([]);
        setAnalyzedSegments([]);
        setProgress(0);
        setError('');
        try {
            await fetch(`${API_BASE}/api/session/${sessionId}`, { method: 'DELETE' });
        } catch { /* ignore */ }
        createSession();
    };

    const downloadSegments = analyzedSegments.map(s => ({
        speaker: s.speaker,
        text: s.text,
        timestamp: s.timestamp || '',
    }));

    const totalSegments = analyzedSegments.length;
    const customerCount = analyzedSegments.filter(s => s.speaker === 'Customer').length;
    const agentCount = analyzedSegments.filter(s => s.speaker === 'Sales Agent').length;

    return (
        <div className="fade-in">
            <div className="page-header">
                <h2>📁 File Analysis</h2>
                <p>Upload a recorded sales call. AI will transcribe, identify speakers, and analyze each customer message.</p>
            </div>

            {/* Engine Toggle */}
            {!analyzedSegments.length && (
                <div className="toolbar" style={{ justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 600 }}>AI Engine:</span>
                        <EngineToggle engine={engine} onToggle={onEngineChange} />
                    </div>
                </div>
            )}

            {/* Upload Zone */}
            {!file && (
                <div
                    className={`upload-zone ${isDragging ? 'dragover' : ''}`}
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <div className="upload-zone-icon">📂</div>
                    <div className="upload-zone-text">
                        <strong>Click to browse</strong> or drag & drop your audio file
                    </div>
                    <div className="upload-zone-formats">
                        Supports: WAV, MP3, M4A, OGG, FLAC, WEBM • Max 50MB
                    </div>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".wav,.mp3,.m4a,.ogg,.flac,.webm"
                        onChange={handleFileSelect}
                        style={{ display: 'none' }}
                    />
                </div>
            )}

            {/* File Selected */}
            {file && analyzedSegments.length === 0 && (
                <div className="file-card slide-up">
                    <div className="file-info">
                        <div className="file-icon">🎵</div>
                        <div className="file-details">
                            <h4>{file.name}</h4>
                            <span>{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                        </div>
                    </div>
                    <div className="file-actions">
                        <button className="btn btn-primary" onClick={processFile} disabled={isProcessing}>
                            {isProcessing ? (
                                <><span className="spinner" /> Processing...</>
                            ) : (
                                <>⚡ Start Analysis</>
                            )}
                        </button>
                        <button className="btn btn-secondary" onClick={resetAll} disabled={isProcessing}>
                            ✕ Remove
                        </button>
                    </div>
                </div>
            )}

            {/* Progress */}
            {isProcessing && (
                <div className="slide-up" style={{ marginBottom: '20px' }}>
                    <div className="progress-bar-container">
                        <div className="progress-bar" style={{ width: `${progress}%` }} />
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                        {progress < 50 ? 'Transcribing audio...' : progress < 95 ? 'Analyzing conversation...' : 'Finishing up...'}
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="error-alert">
                    ⚠️ {error}
                </div>
            )}

            {/* Results */}
            {analyzedSegments.length > 0 && (
                <div className="slide-up">
                    {/* Summary bar */}
                    <div className="summary-bar">
                        <div className="summary-stats">
                            <div className="summary-stat">
                                <div className="summary-stat-value">{totalSegments}</div>
                                <div className="summary-stat-label">Segments</div>
                            </div>
                            <div className="summary-stat">
                                <div className="summary-stat-value">{customerCount}</div>
                                <div className="summary-stat-label">Customer</div>
                            </div>
                            <div className="summary-stat">
                                <div className="summary-stat-value">{agentCount}</div>
                                <div className="summary-stat-label">Agent</div>
                            </div>
                        </div>
                        <button className="btn btn-secondary" onClick={resetAll}>
                            📤 Upload Another
                        </button>
                    </div>

                    {/* Conversation */}
                    <div className="chat-timeline">
                        {analyzedSegments.map((item, index) => (
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
                    </div>

                    {/* Download */}
                    <TranscriptDownload segments={downloadSegments} />
                </div>
            )}
        </div>
    );
}
