import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Execute an automation action
 * @param {string} action - The action to perform
 * @param {Object} parameters - Parameters for the action
 * @returns {Promise<Object>} Result of the automation
 */
export const executeAutomation = async (action, parameters = {}) => {
  try {
    const response = await api.post('/automation/execute', {
      action,
      parameters,
      user_id: 'voice_assistant_user'
    });
    return response.data;
  } catch (error) {
    console.error('Error executing automation:', error);
    throw error;
  }
};

/**
 * Take a screenshot
 * @returns {Promise<Object>} Screenshot data
 */
export const takeScreenshot = async () => {
  try {
    const response = await api.post('/automation/screenshot');
    return response.data;
  } catch (error) {
    console.error('Error taking screenshot:', error);
    throw error;
  }
};

/**
 * Get the current status of the automation service
 * @returns {Promise<Object>} Status information
 */
export const getAutomationStatus = async () => {
  try {
    const response = await api.get('/automation/status');
    return response.data;
  } catch (error) {
    console.error('Error getting automation status:', error);
    throw error;
  }
};

/**
 * Control screen brightness
 * @param {string} direction - "up" or "down"
 * @returns {Promise<Object>} Result of the operation
 */
export const controlBrightness = async (direction) => {
  return executeAutomation(`brightness_${direction}`);
};

/**
 * Control system volume
 * @param {string} action - "up", "down", or "mute"
 * @returns {Promise<Object>} Result of the operation
 */
export const controlVolume = async (action) => {
  return executeAutomation(`volume_${action}`);
};

/**
 * Open an application
 * @param {string} appName - Name of the application to open
 * @returns {Promise<Object>} Result of the operation
 */
export const openApplication = async (appName) => {
  return executeAutomation(`open_${appName}`);
};

/**
 * Close an application
 * @param {string} appName - Name of the application to close
 * @returns {Promise<Object>} Result of the operation
 */
export const closeApplication = async (appName) => {
  return executeAutomation(`close_${appName}`);
};

export default {
  executeAutomation,
  takeScreenshot,
  getAutomationStatus,
  controlBrightness,
  controlVolume,
  openApplication,
  closeApplication
};
