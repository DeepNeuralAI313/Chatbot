import React, { useState } from 'react';
import SettingsForm from './SettingsForm';
import Analytics from './Analytics';
import './Dashboard.css';

const Dashboard = ({ token, username, onLogout }) => {
  const [activeTab, setActiveTab] = useState('analytics');

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <h1>🤖 AI Admin Dashboard</h1>
          <div className="nav-right">
            <span className="username">👤 {username}</span>
            <button onClick={onLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="dashboard-tabs">
        <button 
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📊 Analytics
        </button>
        <button 
          className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'analytics' ? (
          <Analytics token={token} />
        ) : (
          <>
            <div className="content-header">
              <h2>Chatbot Settings</h2>
              <p>Customize your chatbot's behavior and messages</p>
            </div>
            <SettingsForm token={token} />
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
