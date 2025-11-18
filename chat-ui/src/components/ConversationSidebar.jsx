import React from 'react';
import './ConversationSidebar.css';

const ConversationSidebar = ({ conversations, activeConversationId, onSelectConversation, onNewConversation, userName, onLogout }) => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="user-info">
          <div className="user-avatar">{userName?.charAt(0).toUpperCase()}</div>
          <div className="user-details">
            <div className="user-name">{userName}</div>
            <button className="logout-btn" onClick={onLogout}>Logout</button>
          </div>
        </div>
      </div>

      <button className="new-chat-btn" onClick={onNewConversation}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        New Conversation
      </button>

      <div className="conversations-list">
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>No conversations yet</p>
            <p className="hint">Start a new chat to begin!</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${activeConversationId === conv.id ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="conversation-title">{conv.title || 'New Conversation'}</div>
              <div className="conversation-meta">
                <span className="message-count">💬 {conv.message_count}</span>
                <span className="conversation-date">
                  {new Date(conv.last_message_at || conv.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationSidebar;
