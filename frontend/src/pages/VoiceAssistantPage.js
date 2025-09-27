import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Divider,
  useTheme,
  useMediaQuery,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Computer as ComputerIcon,
  Settings as SettingsIcon,
  Info as InfoIcon,
  Mic as MicIcon,
  VolumeUp as VolumeUpIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import VoiceAssistant from '../components/VoiceAssistant';
import { getDeviceHealth } from '../services/deviceAnalyzerService';

// Glass Card Component with Animated Background
const GlassCard = ({ children, hover = false, ...props }) => {
  return (
    <Card 
      sx={{
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(16px)',
        borderRadius: 3,
        border: '1px solid rgba(255, 255, 255, 0.1)',
        transition: 'all 0.3s ease',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        '&:hover': hover ? {
          borderColor: 'rgba(59, 130, 246, 0.3)',
          boxShadow: '0 0 20px rgba(59, 130, 246, 0.3), 0 0 40px rgba(59, 130, 246, 0.2)',
          transform: 'translateY(-5px)',
          '&::before': {
            opacity: 1
          },
          '&::after': {
            opacity: 1,
            transform: 'scale(1.1)'
          }
        } : {},
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: -2,
          background: 'linear-gradient(45deg, transparent, rgba(59, 130, 246, 0.1), transparent)',
          borderRadius: 'inherit',
          zIndex: -1,
          opacity: 0,
          transition: 'opacity 0.3s ease'
        },
        '&::after': {
          content: '""',
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: 'conic-gradient(from 0deg, transparent, rgba(59, 130, 246, 0.1), transparent, rgba(147, 51, 234, 0.1), transparent)',
          animation: 'rotate 4s linear infinite',
          opacity: 0,
          transition: 'opacity 0.3s ease, transform 0.3s ease',
          zIndex: -1
        },
        '@keyframes rotate': {
          '0%': {
            transform: 'rotate(0deg)'
          },
          '100%': {
            transform: 'rotate(360deg)'
          }
        },
        ...props.sx
      }}
      {...props}
    >
      {children}
    </Card>
  );
};

// SpotlightHero Component (reused from SmartFlixDashboard)
const SpotlightHero = () => {
  return (
    <Box 
      sx={{
        position: 'relative',
        height: '25vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: '50%',
          transform: 'translateX(-50%)',
          width: '100%',
          height: '100%',
          background: 'radial-gradient(circle at center, rgba(255, 87, 34, 0.15) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 0
        }
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Typography 
          variant="h2" 
          component="h1" 
          sx={{ 
            fontFamily: '"Orbitron", sans-serif',
            fontWeight: 700,
            textAlign: 'center',
            background: 'linear-gradient(to right, #FF5722, #FFC107)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2
          }}
        >
          Voice Assistant <span style={{ fontSize: '0.8em' }}>🎙️</span>
        </Typography>
      </motion.div>
      
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.3 }}
      >
        <Typography 
          variant="h6" 
          sx={{ 
            color: 'rgba(255,255,255,0.7)',
            textAlign: 'center',
            maxWidth: '600px',
            mx: 'auto',
            fontWeight: 300,
            fontFamily: '"Orbitron", sans-serif'
          }}
        >
          I'm here to troubleshoot, guide, and fix — what's on your mind
        </Typography>
      </motion.div>
    </Box>
  );
};

const VoiceAssistantPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [deviceInfo, setDeviceInfo] = useState(null);
  const [showInfo, setShowInfo] = useState(!isMobile);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch device health information
    const fetchDeviceInfo = async () => {
      try {
        const data = await getDeviceHealth();
        
        if (data.success === false) {
          // Handle error response from the service
          setError(data.error || 'Unable to fetch device information');
          // Still set the device info with fallback values
          setDeviceInfo(data);
        } else {
          setDeviceInfo(data);
          setError(null);
        }
      } catch (err) {
        console.error('Error fetching device info:', err);
        setError('Unable to fetch device information');
        
        // Set fallback device info
        setDeviceInfo({
          status: "unknown",
          metrics: {
            cpu_usage: 0,
            memory_usage: 0,
            disk_usage: 0
          }
        });
      }
    };

    fetchDeviceInfo();
    
    // Set up a polling interval to periodically refresh device info
    const interval = setInterval(fetchDeviceInfo, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Box className="min-h-screen" sx={{ 
      minHeight: '100vh', 
      bgcolor: '#000000',
      position: 'relative',
      overflow: 'auto'
    }}>
      <Box sx={{ 
        position: 'absolute', 
        inset: 0, 
        opacity: 0.05, 
        background: 'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 70%)'
      }} />

      <SpotlightHero />

      <Container maxWidth="xl" sx={{ pb: 8, px: { xs: 2, sm: 3, md: 6 }, position: 'relative', zIndex: 10 }}>
        <Box sx={{ maxWidth: '1400px', mx: 'auto' }}>
          <Grid container spacing={3}>
            {/* Main Content */}
            <Grid item xs={12} md={showInfo ? 8 : 12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <GlassCard sx={{ 
                  height: '70vh',
                  display: 'flex',
                  flexDirection: 'column',
                  overflow: 'hidden'
                }}>
                  <Box sx={{ 
                    p: 2, 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                  }}>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        fontFamily: '"Orbitron", sans-serif',
                        color: 'white'
                      }}
                    >
                      <MicIcon sx={{ mr: 1 }} fontSize="small" />
                      Voice Assistant
                    </Typography>
                    
                    {isMobile && (
                      <Tooltip title="Show/Hide Info Panel">
                        <IconButton 
                          onClick={() => setShowInfo(!showInfo)} 
                          size="small"
                          sx={{ color: 'white' }}
                        >
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                  
                  <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                    <VoiceAssistant deviceInfo={deviceInfo} />
                  </Box>
                </GlassCard>
              </motion.div>
            </Grid>

            {/* Info Panel */}
            <AnimatePresence>
              {showInfo && (
                <Grid item xs={12} md={4}>
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                  >
                    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 3 }}>
                      {/* Device Info Card */}
                      <GlassCard hover={true}>
                        <CardContent>
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              mb: 2,
                              fontFamily: '"Orbitron", sans-serif',
                              color: 'white'
                            }}
                          >
                            <Box 
                              sx={{ 
                                p: 1, 
                                borderRadius: 2, 
                                bgcolor: 'rgba(255, 255, 255, 0.05)', 
                                display: 'flex',
                                mr: 1
                              }}
                            >
                              <ComputerIcon fontSize="small" />
                            </Box>
                            Device Information
                          </Typography>
                          
                          {deviceInfo ? (
                            <Box>
                              {/* System Status */}
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Status:</Typography>
                                <Typography 
                                  variant="body2" 
                                  sx={{
                                    color: deviceInfo.status === 'healthy' ? '#4caf50' : 
                                           deviceInfo.status === 'warning' ? '#ff9800' : 
                                           deviceInfo.status === 'critical' ? '#f44336' :
                                           error ? '#f44336' : 'rgba(255, 255, 255, 0.7)',
                                    fontWeight: 'medium'
                                  }}
                                >
                                  {deviceInfo.status?.toUpperCase() || 'UNKNOWN'}
                                </Typography>
                              </Box>
                              
                              <Divider sx={{ my: 1.5, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                              
                              {/* Operating System Information */}
                              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.9)', mb: 1, fontWeight: 'bold' }}>
                                Operating System
                              </Typography>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Platform:</Typography>
                                <Typography variant="body2" sx={{ color: 'white' }}>
                                  {navigator.platform || 'Unknown'}
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>User Agent:</Typography>
                                <Typography variant="body2" sx={{ color: 'white', fontSize: '0.7rem', maxWidth: '60%', textAlign: 'right' }}>
                                  {navigator.userAgent.split(' ')[0] || 'Unknown'}
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Language:</Typography>
                                <Typography variant="body2" sx={{ color: 'white' }}>
                                  {navigator.language || 'Unknown'}
                                </Typography>
                              </Box>
                              
                              <Divider sx={{ my: 1.5, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                              
                              {/* Network Information */}
                              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.9)', mb: 1, fontWeight: 'bold' }}>
                                Network Status
                              </Typography>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Connection:</Typography>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    color: navigator.onLine ? '#4caf50' : '#f44336',
                                    fontWeight: 'medium'
                                  }}
                                >
                                  {navigator.onLine ? 'Online' : 'Offline'}
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Network Speed:</Typography>
                                <Typography variant="body2" sx={{ color: 'white' }}>
                                  {navigator.connection?.downlink ? `${navigator.connection.downlink} Mbps` : 'Unknown'}
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>RTT:</Typography>
                                <Typography variant="body2" sx={{ color: 'white' }}>
                                  {navigator.connection?.rtt ? `${navigator.connection.rtt}ms` : 'Unknown'}
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Connection Type:</Typography>
                                <Typography variant="body2" sx={{ color: 'white' }}>
                                  {navigator.connection?.effectiveType || 'Unknown'}
                                </Typography>
                              </Box>
                              
                              <Divider sx={{ my: 1.5, borderColor: 'rgba(255, 255, 255, 0.1)' }} />
                              
                              {/* Performance Metrics */}
                              <Typography variant="subtitle2" sx={{ color: 'rgba(255, 255, 255, 0.9)', mb: 1, fontWeight: 'bold' }}>
                                System Performance
                              </Typography>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>CPU Usage:</Typography>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    color: deviceInfo.metrics?.cpu_usage > 80 ? '#ff9800' : 
                                           deviceInfo.metrics?.cpu_usage > 90 ? '#f44336' : '#4caf50',
                                    fontWeight: 'medium'
                                  }}
                                >
                                  {deviceInfo.metrics?.cpu_usage?.toFixed(1) || 0}%
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Memory Usage:</Typography>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    color: deviceInfo.metrics?.memory_usage > 80 ? '#ff9800' : 
                                           deviceInfo.metrics?.memory_usage > 90 ? '#f44336' : '#4caf50',
                                    fontWeight: 'medium'
                                  }}
                                >
                                  {deviceInfo.metrics?.memory_usage?.toFixed(1) || 0}%
                                </Typography>
                              </Box>
                              
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>Disk Usage:</Typography>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    color: deviceInfo.metrics?.disk_usage > 80 ? '#ff9800' : 
                                           deviceInfo.metrics?.disk_usage > 90 ? '#f44336' : '#4caf50',
                                    fontWeight: 'medium'
                                  }}
                                >
                                  {deviceInfo.metrics?.disk_usage?.toFixed(1) || 0}%
                                </Typography>
                              </Box>
                              
                              {/* Last Updated */}
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.7rem' }}>Last Updated:</Typography>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.7rem' }}>
                                  {deviceInfo.timestamp ? new Date(deviceInfo.timestamp).toLocaleTimeString() : 'Just now'}
                                </Typography>
                              </Box>
                              
                              {error && (
                                <Box sx={{ mt: 2, p: 1.5, bgcolor: 'rgba(244, 67, 54, 0.1)', borderRadius: 1, border: '1px solid rgba(244, 67, 54, 0.3)' }}>
                                  <Typography sx={{ color: '#f44336', fontSize: '0.75rem' }}>
                                    {error}
                                  </Typography>
                                </Box>
                              )}
                            </Box>
                          ) : (
                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 2 }}>
                              <CircularProgress size={24} sx={{ mb: 1, color: '#FF5722' }} />
                              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                                Loading device information...
                              </Typography>
                            </Box>
                          )}
                        </CardContent>
                      </GlassCard>

                    </Box>
                  </motion.div>
                </Grid>
              )}
            </AnimatePresence>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default VoiceAssistantPage;