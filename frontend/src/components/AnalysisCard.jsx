export default function AnalysisCard({ analysis }) {
    if (!analysis) return null;

    const { sentiment, intent, entities, engine_used } = analysis;
    const sentimentClass = (sentiment?.label || '').toLowerCase();

    return (
        <div className="analysis-grid fade-in">
            {/* Sentiment */}
            <div className="analysis-card">
                <div className="analysis-card-header">
                    <span>🧠</span> Sentiment
                </div>
                <div className="sentiment-label">
                    <span className={`sentiment-dot ${sentimentClass}`}></span>
                    {sentiment?.label || 'Unknown'}
                </div>
                <div className="confidence-bar">
                    <div
                        className="confidence-bar-fill"
                        style={{ width: `${(sentiment?.score || 0) * 100}%` }}
                    />
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                    Confidence: {((sentiment?.score || 0) * 100).toFixed(0)}%
                </div>
            </div>

            {/* Intent */}
            <div className="analysis-card">
                <div className="analysis-card-header">
                    <span>🎯</span> Intent
                </div>
                <div className="intent-badge">{intent?.label || 'Unknown'}</div>
                <div className="confidence-bar" style={{ marginTop: '14px' }}>
                    <div
                        className="confidence-bar-fill"
                        style={{ width: `${(intent?.score || 0) * 100}%` }}
                    />
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                    Confidence: {((intent?.score || 0) * 100).toFixed(0)}%
                </div>
            </div>

            {/* Entities */}
            <div className="analysis-card">
                <div className="analysis-card-header">
                    <span>🔍</span> Entities
                </div>
                {entities && entities.length > 0 ? (
                    <div className="entity-pills">
                        {entities.map((e, i) => (
                            <span className="entity-pill" key={i}>
                                <span className="entity-pill-type">{e.entity}:</span>
                                <span className="entity-pill-value">{e.value}</span>
                            </span>
                        ))}
                    </div>
                ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                        No entities detected
                    </div>
                )}

                {engine_used && (
                    <div style={{ marginTop: '12px' }}>
                        <span className={`engine-badge ${engine_used}`}>
                            ⚡ {engine_used === 'gemini' ? 'Gemini' : engine_used === 'groq' ? 'Groq' : 'Fallback'}
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}
