import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Query the smart assistant with network awareness
 * @param {string} query - The user's question
 * @param {boolean} collectSystemData - Whether to collect system data for context
 * @param {Object} context - Optional context information
 * @returns {Promise<Object>} - The assistant's response
 */
export const querySmartAssistant = async (query, collectSystemData = true, context = null) => {
  try {
    const response = await api.post('/smart/query', {
      query,
      user_id: 'user_' + Date.now(),
      collect_system_data: collectSystemData,
      context
    });
    return response.data;
  } catch (error) {
    console.error('Error querying smart assistant:', error);
    throw error;
  }
};

/**
 * Query the offline assistant
 * @param {string} query - The user's question
 * @param {Object} context - Optional context information
 * @returns {Promise<Object>} - The assistant's response
 */
export const queryOfflineAssistant = async (query, context = null) => {
  try {
    const response = await api.post('/smart/offline', {
      query,
      user_id: 'user_' + Date.now(),
      context
    });
    return response.data;
  } catch (error) {
    console.error('Error querying offline assistant:', error);
    throw error;
  }
};

/**
 * Get the status of the smart assistant services
 * @returns {Promise<Object>} - Status information
 */
export const getSmartAssistantStatus = async () => {
  try {
    const response = await api.get('/smart/status');
    return response.data;
  } catch (error) {
    console.error('Error getting smart assistant status:', error);
    throw error;
  }
};

/**
 * Legacy assistant API for backward compatibility
 */
export const queryAssistant = async (query, context = null) => {
  try {
    // Try smart assistant first
    return await querySmartAssistant(query, true, context);
  } catch (error) {
    console.warn('Smart assistant failed, trying offline mode:', error);
    // Fallback to offline assistant
    return await queryOfflineAssistant(query, context);
  }
};

/**
 * Get assistant status (legacy compatibility)
 */
export const getAssistantStatus = async () => {
  try {
    return await getSmartAssistantStatus();
  } catch (error) {
    console.error('Error getting assistant status:', error);
    return {
      network_status: 'unknown',
      preferred_mode: 'offline',
      offline_assistant: { available: false },
      services_available: {
        network_aware_assistant: false,
        device_logs_collector: false,
        enhanced_offline_assistant: false
      }
    };
  }
};

export default {
  querySmartAssistant,
  queryOfflineAssistant,
  getSmartAssistantStatus,
  queryAssistant,
  getAssistantStatus
};
