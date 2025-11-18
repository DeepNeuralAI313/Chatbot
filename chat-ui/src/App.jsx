import React, { useState, useEffect } from 'react';
import ChatWidget from './components/ChatWidget';
import AuthForm from './components/AuthForm';
import ConversationSidebar from './components/ConversationSidebar';
import { getUserConversations } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);

  useEffect(() => {
    // Check for existing authentication
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser && storedUser !== 'undefined') {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse stored user:', error);
        // Clear invalid data
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && token) {
      loadConversations();
    }
  }, [isAuthenticated, token]);

  const loadConversations = async () => {
    try {
      const convs = await getUserConversations(token);
      setConversations(Array.isArray(convs) ? convs : []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      setConversations([]);
    }
  };

  const handleAuth = (authToken, userData) => {
    setToken(authToken);
    setUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('token', authToken);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setToken(null);
    setUser(null);
    setConversations([]);
    setActiveConversationId(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('conversationId');
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    localStorage.removeItem('conversationId');
    // Reload conversations after a short delay
    setTimeout(() => loadConversations(), 500);
  };

  const handleSelectConversation = (conversationId) => {
    setActiveConversationId(conversationId);
    localStorage.setItem('conversationId', conversationId);
  };

  if (!isAuthenticated) {
    return (
      <div className="App">
        <AuthForm onAuth={handleAuth} />
      </div>
    );
  }

  return (
    <div className="App">
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        userName={user?.name}
        onLogout={handleLogout}
      />
      <div className="main-content">
        <ChatWidget 
          token={token} 
          conversationId={activeConversationId}
          onConversationCreated={loadConversations}
        />
      </div>
    </div>
  );
}

export default App;
