import React from 'react';
import './ChatBubble.css';

const ChatBubble = ({ message, onHumanConnect }) => {
  const isUser = message.role === 'user';
  
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  // Format AI response for better readability
  const formatContent = (content) => {
    if (isUser) return content;
    
    // Split into paragraphs
    const paragraphs = content.split('\n').filter(p => p.trim());
    
    return paragraphs.map((para, index) => {
      // Check if it's a numbered list item (1., 2., etc.)
      const numberedMatch = para.match(/^(\d+)\.\s*\*\*(.+?)\*\*\s*(.*)/);
      if (numberedMatch) {
        const [, num, title, text] = numberedMatch;
        return (
          <div key={index} className="formatted-list-item">
            <span className="list-number">{num}.</span>
            <span className="list-title">{title}:</span>
            <span className="list-text">{text}</span>
          </div>
        );
      }
      
      // Check for bold text with **
      const parts = para.split(/(\*\*.*?\*\*)/g);
      return (
        <p key={index} className="formatted-paragraph">
          {parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={i}>{part.slice(2, -2)}</strong>;
            }
            return part;
          })}
        </p>
      );
    });
  };

  return (
    <div className={`chat-bubble-container ${isUser ? 'user' : 'assistant'}`}>
      <div className={`chat-bubble ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-content">
          {isUser ? message.content : formatContent(message.content)}
        </div>
        {message.needsHuman && !isUser && (
          <button className="human-connect-btn" onClick={onHumanConnect}>
            🤝 Connect with Human
          </button>
        )}
        <div className="message-time">{formatTime(message.timestamp)}</div>
      </div>
    </div>
  );
};

export default ChatBubble;
