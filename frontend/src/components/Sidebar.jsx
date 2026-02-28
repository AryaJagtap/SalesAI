export default function Sidebar({ activePage, onNavigate, theme, onToggleTheme, isOpen }) {
    return (
        <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
            {/* Brand */}
            <div className="sidebar-brand">
                <div className="sidebar-brand-icon">
                    <img src="/logo.svg" alt="SalesAI" width="28" height="28" />
                </div>
                <div>
                    <h1>SalesAI</h1>
                    <span className="version-badge">V2.0</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                <div className="nav-label">Analysis</div>
                <div
                    className={`nav-item ${activePage === 'live' ? 'active' : ''}`}
                    onClick={() => onNavigate('live')}
                >
                    <span className="nav-item-icon">🎙️</span>
                    Live Co-Pilot
                </div>
                <div
                    className={`nav-item ${activePage === 'upload' ? 'active' : ''}`}
                    onClick={() => onNavigate('upload')}
                >
                    <span className="nav-item-icon">📁</span>
                    File Analysis
                </div>
            </nav>

            {/* Footer */}
            <div className="sidebar-footer">
                <div className="sidebar-status">
                    <span className="status-dot active"></span>
                    AI Engine Active
                </div>

                <div className="theme-toggle">
                    <span>{theme === 'dark' ? '🌙 Dark' : '☀️ Light'}</span>
                    <button
                        className="theme-toggle-btn"
                        onClick={onToggleTheme}
                        aria-label="Toggle theme"
                    />
                </div>
            </div>
        </aside>
    );
}
