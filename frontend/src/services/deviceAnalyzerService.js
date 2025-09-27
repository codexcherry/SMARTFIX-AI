import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get the current health status of the device
 * @returns {Promise<Object>} Health status data
 */
export const getDeviceHealth = async () => {
  try {
    const response = await api.get('/query/device/health');
    return response.data;
  } catch (error) {
    console.error('Error getting device health:', error);
    // Return a fallback response instead of throwing an error
    return {
      success: false,
      status: "unknown",
      metrics: {
        cpu_usage: 0,
        memory_usage: 0,
        disk_usage: 0
      },
      error: error.message || "Unable to connect to device health service"
    };
  }
};

/**
 * Perform a quick scan of the device
 * @param {string} userId - User ID for tracking
 * @returns {Promise<Object>} Scan results
 */
export const performQuickScan = async (userId = 'voice_assistant_user') => {
  try {
    const response = await api.post('/query/device/analyze/quick', {
      scan_type: 'quick',
      user_id: userId
    });
    return response.data;
  } catch (error) {
    console.error('Error performing quick scan:', error);
    throw error;
  }
};

/**
 * Perform a deep scan of the device
 * @param {string} userId - User ID for tracking
 * @param {boolean} includeHardware - Whether to include hardware diagnostics
 * @param {boolean} includeSecurity - Whether to include security checks
 * @returns {Promise<Object>} Scan results
 */
export const performDeepScan = async (
  userId = 'voice_assistant_user',
  includeHardware = true,
  includeSecurity = true
) => {
  try {
    const response = await api.post('/query/device/analyze/deep', {
      scan_type: 'deep',
      user_id: userId,
      include_hardware: includeHardware,
      include_security: includeSecurity,
      include_failure_analysis: true,
      include_performance_history: true
    });
    return response.data;
  } catch (error) {
    console.error('Error performing deep scan:', error);
    throw error;
  }
};

/**
 * Get detailed metrics about the device
 * @returns {Promise<Object>} Detailed metrics
 */
export const getDetailedMetrics = async () => {
  try {
    const response = await api.get('/query/device/detailed-metrics');
    return response.data;
  } catch (error) {
    console.error('Error getting detailed metrics:', error);
    throw error;
  }
};

/**
 * Analyze an image for hardware or software issues
 * @param {string} imageData - Base64 encoded image data
 * @param {string} textQuery - Optional text description of the issue
 * @returns {Promise<Object>} Analysis results
 */
export const analyzeImage = async (imageData, textQuery = '') => {
  try {
    // Convert base64 to blob
    const byteString = atob(imageData.split(',')[1]);
    const mimeString = imageData.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    
    const blob = new Blob([ab], { type: mimeString });
    const file = new File([blob], "screenshot.png", { type: mimeString });
    
    const formData = new FormData();
    formData.append('image', file);
    formData.append('text_query', textQuery);
    formData.append('user_id', 'voice_assistant_user');
    
    const response = await api.post('/query/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
};

/**
 * Perform system automation based on the issue
 * @param {string} action - The action to perform
 * @param {Object} parameters - Parameters for the action
 * @returns {Promise<Object>} Result of the automation
 */
export const performAutomation = async (action, parameters = {}) => {
  try {
    const response = await api.post('/query/automation', {
      action,
      parameters,
      user_id: 'voice_assistant_user'
    });
    return response.data;
  } catch (error) {
    console.error('Error performing automation:', error);
    throw error;
  }
};

export default {
  getDeviceHealth,
  performQuickScan,
  performDeepScan,
  getDetailedMetrics,
  analyzeImage,
  performAutomation
};
