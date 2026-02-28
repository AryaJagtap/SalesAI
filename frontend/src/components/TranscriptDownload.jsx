export default function TranscriptDownload({ segments, format = 'txt' }) {
    if (!segments || segments.length === 0) return null;

    const downloadTxt = () => {
        const lines = segments.map(seg =>
            `[${seg.timestamp || '00:00'}] ${seg.speaker}: "${seg.text}"`
        );
        const content = `Sales.Ai — Transcript\n${'='.repeat(40)}\n\n${lines.join('\n\n')}`;
        triggerDownload(content, 'transcript.txt', 'text/plain');
    };

    const downloadJson = () => {
        const data = {
            generated_by: 'Sales.Ai',
            timestamp: new Date().toISOString(),
            segments: segments,
        };
        triggerDownload(JSON.stringify(data, null, 2), 'transcript.json', 'application/json');
    };

    const triggerDownload = (content, filename, mime) => {
        const blob = new Blob([content], { type: mime });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="download-section">
            <button className="btn btn-secondary" onClick={downloadTxt}>
                📄 Download TXT
            </button>
            <button className="btn btn-secondary" onClick={downloadJson}>
                📋 Download JSON
            </button>
        </div>
    );
}
