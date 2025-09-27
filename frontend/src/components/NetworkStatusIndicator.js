import React, { useState, useEffect } from 'react';
import {
  Box,
  Chip,
  Tooltip,
  IconButton,
  Badge,
  Typography,
  Fade
} from '@mui/material';
import {
  Wifi,
  WifiOff,
  CloudDone,
  CloudOff,
  Refresh,
  CheckCircle,
  Error as ErrorIcon,
  Warning
} from '@mui/icons-material';
import { getSmartAssistantStatus } from '../services/smartAssistantApi';

const NetworkStatusIndicator = ({ onStatusChange }) => {
  const [status, setStatus] = useState({
    network_status: 'checking',
    preferred_mode: 'unknown',
    services_available: {}
  });
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const newStatus = await getSmartAssistantStatus();
      setStatus(newStatus);
      setLastUpdate(new Date());
      
      if (onStatusChange) {
        onStatusChange(newStatus);
      }
    } catch (error) {
      console.error('Error loading status:', error);
      setStatus(prev => ({
        ...prev,
        network_status: 'offline',
        preferred_mode: 'offline'
      }));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
    
    // Refresh status every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = () => {
    switch (status.network_status) {
      case 'online':
        return <Wifi color="success" />;
      case 'offline':
        return <WifiOff color="error" />;
      case 'checking':
        return <CloudOff color="warning" />;
      default:
        return <CloudOff color="warning" />;
    }
  };

  const getStatusColor = () => {
    switch (status.network_status) {
      case 'online':
        return 'success';
      case 'offline':
        return 'error';
      case 'checking':
        return 'info';
      default:
        return 'warning';
    }
  };

  const getModeIcon = () => {
    switch (status.preferred_mode) {
      case 'online':
        return <CloudDone color="primary" />;
      case 'offline':
        return <CloudOff color="secondary" />;
      default:
        return <Warning color="warning" />;
    }
  };

  const getModeColor = () => {
    switch (status.preferred_mode) {
      case 'online':
        return 'success';
      case 'offline':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getServicesStatus = () => {
    const services = status.services_available || {};
    const availableCount = Object.values(services).filter(Boolean).length;
    const totalCount = Object.keys(services).length;
    
    return { available: availableCount, total: totalCount };
  };

  const servicesStatus = getServicesStatus();

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {/* Network Status */}
      <Tooltip 
        title={
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
              Network Status: {status.network_status?.toUpperCase()}
            </Typography>
            <Typography variant="caption">
              {lastUpdate ? `Last updated: ${lastUpdate.toLocaleTimeString()}` : 'Never updated'}
            </Typography>
          </Box>
        }
      >
        <Badge
          color={getStatusColor()}
          variant="dot"
          sx={{ '& .MuiBadge-dot': { width: 8, height: 8 } }}
        >
          <IconButton size="small" onClick={loadStatus} disabled={loading}>
            {loading ? <Refresh sx={{ animation: 'spin 1s linear infinite' }} /> : getStatusIcon()}
          </IconButton>
        </Badge>
      </Tooltip>

      {/* Mode Indicator */}
      <Tooltip 
        title={
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
              Assistant Mode: {status.preferred_mode?.toUpperCase()}
            </Typography>
            <Typography variant="caption">
              {status.preferred_mode === 'online' 
                ? 'Using Gemini AI with internet connection'
                : 'Using offline local assistant'
              }
            </Typography>
          </Box>
        }
      >
        <Chip
          icon={getModeIcon()}
          label={status.preferred_mode?.toUpperCase() || 'UNKNOWN'}
          size="small"
          color={getModeColor()}
          variant="outlined"
        />
      </Tooltip>

      {/* Services Status */}
      <Tooltip 
        title={
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
              Services Status
            </Typography>
            {Object.entries(status.services_available || {}).map(([service, available]) => (
              <Box key={service} sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                {available ? <CheckCircle fontSize="small" color="success" /> : <ErrorIcon fontSize="small" color="error" />}
                <Typography variant="caption">
                  {service.replace('_', ' ').toUpperCase()}: {available ? 'Available' : 'Unavailable'}
                </Typography>
              </Box>
            ))}
          </Box>
        }
      >
        <Chip
          icon={servicesStatus.available === servicesStatus.total ? <CheckCircle /> : <ErrorIcon />}
          label={`${servicesStatus.available}/${servicesStatus.total} Services`}
          size="small"
          color={servicesStatus.available === servicesStatus.total ? 'success' : 'error'}
          variant="outlined"
        />
      </Tooltip>
    </Box>
  );
};

export default NetworkStatusIndicator;
