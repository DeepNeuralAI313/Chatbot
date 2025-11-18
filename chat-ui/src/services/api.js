const API_BASE_URL = '/api';

export const sendMessage = async (message, conversationId, token) => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
};

export const getConversation = async (conversationId) => {
  const response = await fetch(`${API_BASE_URL}/conversation/${conversationId}`);

  if (!response.ok) {
    throw new Error('Failed to get conversation');
  }

  return response.json();
};

export const getSettings = async () => {
  const response = await fetch(`${API_BASE_URL}/admin/settings`);

  if (!response.ok) {
    throw new Error('Failed to get settings');
  }

  return response.json();
};

export const userSignup = async (email, name, password) => {
  const response = await fetch(`${API_BASE_URL}/user/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, name, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signup failed');
  }

  return response.json();
};

export const userLogin = async (email, password) => {
  const response = await fetch(`${API_BASE_URL}/user/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
};

export const getUserConversations = async (token) => {
  const response = await fetch(`${API_BASE_URL}/user/conversations`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to get conversations');
  }

  const data = await response.json();
  return data.conversations || [];
};
