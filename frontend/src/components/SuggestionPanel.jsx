import { useState } from 'react';

export default function SuggestionPanel({ suggestion, reasoning }) {
    const [showReasoning, setShowReasoning] = useState(false);

    if (!suggestion) return null;

    return (
        <div className="suggestion-panel fade-in">
            <div className="suggestion-header">
                💡 Suggested Next Question
            </div>
            <div className="suggestion-text">"{suggestion}"</div>
            {reasoning && (
                <div
                    className="suggestion-reasoning"
                    onClick={() => setShowReasoning(!showReasoning)}
                >
                    <span>{showReasoning ? '▾' : '▸'}</span>
                    Strategy
                    <div className={`suggestion-reasoning-text ${showReasoning ? 'open' : ''}`}>
                        {reasoning}
                    </div>
                </div>
            )}
        </div>
    );
}
