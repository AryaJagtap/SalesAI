export default function ChatBubble({ speaker, text, timestamp }) {
    const isCustomer = speaker === 'Customer';

    return (
        <div className={`chat-bubble-wrapper ${isCustomer ? 'customer' : 'agent'}`}>
            <div className={`chat-bubble ${isCustomer ? 'customer' : 'agent'}`}>
                <div className="chat-bubble-speaker">
                    {isCustomer ? '👤 Customer' : '🧑‍💼 Sales Agent'}
                </div>
                <div>{text}</div>
                {timestamp && <div className="chat-bubble-time">{timestamp}</div>}
            </div>
        </div>
    );
}
