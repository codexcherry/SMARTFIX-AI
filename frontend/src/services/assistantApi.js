import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Query the assistant with a text question
 * @param {string} query - The user's question
 * @param {Object} context - Optional context information (device info, etc)
 * @returns {Promise<Object>} - The assistant's response
 */
export const queryAssistant = async (query, context = null) => {
  try {
    const response = await api.post('/assistant/local', {
      query,
      context
    });
    return response.data;
  } catch (error) {
    console.error('Error querying assistant:', error);
    throw error;
  }
};

/**
 * Get the current status of the assistant
 * @returns {Promise<Object>} - Status information
 */
export const getAssistantStatus = async () => {
  try {
    const response = await api.get('/assistant/status');
    return response.data;
  } catch (error) {
    console.error('Error getting assistant status:', error);
    throw error;
  }
};

export default {
  queryAssistant,
  getAssistantStatus
};
