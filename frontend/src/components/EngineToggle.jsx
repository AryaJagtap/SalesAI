export default function EngineToggle({ engine, onToggle }) {
    return (
        <div className="engine-toggle">
            <button
                className={`engine-toggle-option ${engine === 'gemini' ? 'active' : ''}`}
                onClick={() => onToggle('gemini')}
            >
                <span className="engine-dot" />
                Gemini
            </button>
            <button
                className={`engine-toggle-option ${engine === 'groq' ? 'active' : ''}`}
                onClick={() => onToggle('groq')}
            >
                <span className="engine-dot" />
                Groq
            </button>
        </div>
    );
}
