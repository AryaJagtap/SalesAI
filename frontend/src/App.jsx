import { useState } from 'react';
import './index.css';
import { useTheme } from './hooks/useTheme';
import Sidebar from './components/Sidebar';
import LiveCopilot from './pages/LiveCopilot';
import FileAnalysis from './pages/FileAnalysis';

function App() {
  const { theme, toggleTheme } = useTheme();
  const [activePage, setActivePage] = useState('live');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [engine, setEngine] = useState('groq');

  return (
    <div className="app-layout">
      {/* Mobile menu button */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? '✕' : '☰'}
      </button>

      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'active' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <Sidebar
        activePage={activePage}
        onNavigate={(page) => {
          setActivePage(page);
          setSidebarOpen(false);
        }}
        theme={theme}
        onToggleTheme={toggleTheme}
        isOpen={sidebarOpen}
      />

      {/* Main Content */}
      <main className="main-content">
        {activePage === 'live'
          ? <LiveCopilot engine={engine} onEngineChange={setEngine} />
          : <FileAnalysis engine={engine} onEngineChange={setEngine} />
        }
      </main>
    </div>
  );
}

export default App;
