import React, { useState, useEffect } from 'react';
import './SettingsForm.css';
import { getSettings, updateSettings } from '../services/adminApi';

const SettingsForm = ({ token }) => {
  const [settings, setSettings] = useState({
    welcome_message: '',
    fallback_message: '',
    tone_instructions: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await getSettings(token);
      setSettings(data);
    } catch (error) {
      showNotification('Failed to load settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      await updateSettings(settings, token);
      showNotification('Settings saved successfully!', 'success');
    } catch (error) {
      showNotification('Failed to save settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  const showNotification = (message, type) => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  if (loading) {
    return <div className="loading">Loading settings...</div>;
  }

  return (
    <div className="settings-form">
      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <label htmlFor="welcome_message">
            <h3>Welcome Message</h3>
            <p className="field-description">
              First message shown when users open the chat
            </p>
          </label>
          <textarea
            id="welcome_message"
            value={settings.welcome_message}
            onChange={(e) => handleChange('welcome_message', e.target.value)}
            rows={3}
            required
          />
        </div>

        <div className="form-section">
          <label htmlFor="fallback_message">
            <h3>Fallback Message</h3>
            <p className="field-description">
              Message shown when the AI cannot find relevant information
            </p>
          </label>
          <textarea
            id="fallback_message"
            value={settings.fallback_message}
            onChange={(e) => handleChange('fallback_message', e.target.value)}
            rows={3}
            required
          />
        </div>

        <div className="form-section">
          <label htmlFor="tone_instructions">
            <h3>Tone Instructions</h3>
            <p className="field-description">
              Instructions for the AI about how to respond (language, style, tone)
            </p>
          </label>
          <textarea
            id="tone_instructions"
            value={settings.tone_instructions}
            onChange={(e) => handleChange('tone_instructions', e.target.value)}
            rows={4}
            required
          />
        </div>

        <button type="submit" className="save-button" disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </form>
    </div>
  );
};

export default SettingsForm;
