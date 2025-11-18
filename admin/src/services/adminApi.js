const API_BASE_URL = '/api';

export const login = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/admin/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    throw new Error('Invalid credentials');
  }

  return response.json();
};

export const getSettings = async (token) => {
  const response = await fetch(`${API_BASE_URL}/admin/settings`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to get settings');
  }

  return response.json();
};

export const updateSettings = async (settings, token) => {
  const response = await fetch(`${API_BASE_URL}/admin/settings`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(settings)
  });

  if (!response.ok) {
    throw new Error('Failed to update settings');
  }

  return response.json();
};
