import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Text query endpoint
export const submitTextQuery = async (textQuery, userId = 'anonymous') => {
  try {
    const response = await api.post('/query/text', {
      user_id: userId,
      input_type: 'text',
      text_query: textQuery,
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting text query:', error);
    throw error;
  }
};

// Image query endpoint
export const submitImageQuery = async (imageFile, textQuery = '', userId = 'anonymous') => {
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('text_query', textQuery);
    formData.append('user_id', userId);
    
    const response = await api.post('/query/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting image query:', error);
    throw error;
  }
};


// Log file query endpoint
export const submitLogQuery = async (logFile, userId = 'anonymous') => {
  try {
    const formData = new FormData();
    formData.append('log_file', logFile);
    formData.append('user_id', userId);
    
    const response = await api.post('/query/logs', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting log query:', error);
    throw error;
  }
};

// Send notification
export const sendNotification = async (notificationData) => {
  try {
    const response = await api.post('/query/notify', notificationData);
    return response.data;
  } catch (error) {
    console.error('Error sending notification:', error);
    throw error;
  }
};

// Get user history
export const getUserHistory = async (userId) => {
  try {
    const response = await api.get(`/query/history/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user history:', error);
    throw error;
  }
};

export default {
  submitTextQuery,
  submitImageQuery,
  submitLogQuery,
  sendNotification,
  getUserHistory,
};
