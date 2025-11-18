import React, { useState, useEffect, useRef } from 'react';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';
import './ChatWidget.css';
import { sendMessage } from '../services/api';

const ChatWidget = ({ token, conversationId: propConversationId, onConversationCreated }) => {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(propConversationId);
  const [isLoading, setIsLoading] = useState(false);
  const [humanHandoff, setHumanHandoff] = useState(false);
  const [welcomeMessage, setWelcomeMessage] = useState('');
  const [showPopup, setShowPopup] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Update conversation ID when prop changes
    setConversationId(propConversationId);
    if (propConversationId) {
      // Load messages for this conversation
      loadConversationMessages(propConversationId);
    } else {
      // New conversation - clear messages
      setMessages([]);
      setHumanHandoff(false);
    }
  }, [propConversationId]);

  useEffect(() => {
    // Fetch welcome message from settings
    fetchWelcomeMessage();
  }, []);

  useEffect(() => {
    // Show welcome message for new conversation
    if (messages.length === 0 && welcomeMessage && !propConversationId) {
      setMessages([{
        role: 'assistant',
        content: welcomeMessage,
        timestamp: new Date().toISOString()
      }]);
    }
  }, [welcomeMessage, propConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversationMessages = async (convId) => {
    try {
      const response = await fetch(`/api/user/conversations/${convId}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const msgs = await response.json();
        setMessages(msgs);
      }
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
    }
  };

  const fetchWelcomeMessage = async () => {
    try {
      const response = await fetch('/api/admin/settings');
      if (response.ok) {
        const settings = await response.json();
        setWelcomeMessage(settings.welcome_message);
      }
    } catch (error) {
      console.error('Failed to fetch welcome message:', error);
      setWelcomeMessage('Hello! How can I help you today?');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleHumanConnect = () => {
    setShowPopup(true);
    // Auto-hide popup after 3 seconds
    setTimeout(() => {
      setShowPopup(false);
    }, 3000);
  };

  const handleSendMessage = async (messageText) => {
    if (humanHandoff) return;

    // Add user message to UI
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(messageText, conversationId, token);
      
      // Store conversation ID and notify parent
      if (!conversationId) {
        setConversationId(response.conversation_id);
        localStorage.setItem('conversationId', response.conversation_id);
        if (onConversationCreated) {
          onConversationCreated();
        }
      }

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toISOString(),
        needsHuman: response.needs_human || false
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Check for human handoff
      if (response.needs_human) {
        setHumanHandoff(true);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, an error occurred. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-title">
            <h3>AI Chat Assistant</h3>
            <span className="chat-status">● Online</span>
          </div>
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <ChatBubble key={index} message={msg} onHumanConnect={handleHumanConnect} />
        ))}
        {isLoading && (
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {showPopup && (
        <div className="popup-overlay" onClick={() => setShowPopup(false)}>
          <div className="popup-modal" onClick={(e) => e.stopPropagation()}>
            <div className="popup-icon">⏳</div>
            <h3>Feature Coming Soon</h3>
            <p>Human handoff feature is still in development. We'll notify you once it's ready!</p>
            <button className="popup-close-btn" onClick={() => setShowPopup(false)}>Got it</button>
          </div>
        </div>
      )}

      <ChatInput onSend={handleSendMessage} disabled={humanHandoff || isLoading} />
    </div>
  );
};

export default ChatWidget;
