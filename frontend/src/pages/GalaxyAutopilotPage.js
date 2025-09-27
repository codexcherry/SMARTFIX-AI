import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  CardHeader,
  Button,
  Chip,
  LinearProgress,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AutoFixHigh as AutoFixHighIcon,
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Healing as HealingIcon,
  Settings as SettingsIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Close as CloseIcon
} from '@mui/icons-material';

// Galaxy Autopilot Main Page Component
export default function GalaxyAutopilotPage() {
  const [activeLayer, setActiveLayer] = useState(null);
  const [systemStatus, setSystemStatus] = useState({
    surface: { status: 'active', health: 95 },
    deep: { status: 'active', health: 88 },
    immune: { status: 'active', health: 92 },
    regenerative: { status: 'active', health: 85 },
    optimization: { status: 'active', health: 90 }
  });
  const [isRunning, setIsRunning] = useState(true);
  const [recentActions, setRecentActions] = useState([
    { id: 1, action: 'Auto-restarted crashed app', layer: 'surface', timestamp: '2 minutes ago', success: true },
    { id: 2, action: 'Cleared system cache', layer: 'surface', timestamp: '5 minutes ago', success: true },
    { id: 3, action: 'Repaired corrupted system file', layer: 'deep', timestamp: '10 minutes ago', success: true },
    { id: 4, action: 'Quarantined suspicious app', layer: 'immune', timestamp: '15 minutes ago', success: true },
    { id: 5, action: 'Optimized battery usage', layer: 'optimization', timestamp: '20 minutes ago', success: true }
  ]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const healingLayers = [
    {
      id: 'surface',
      name: 'Surface Healing',
      description: 'Instant resolution of common daily issues',
      icon: AutoFixHighIcon,
      color: '#4CAF50',
      features: [
        'Auto-restart crashed apps via Device Care APIs',
        'Clear cache/junk using Android Intelligence Services',
        'Throttle/Kill battery-draining processes via Knox Real-Time Monitor'
      ],
      status: systemStatus.surface
    },
    {
      id: 'deep',
      name: 'Deep Healing',
      description: 'Recover from OS/file-system corruption without factory reset',
      icon: HealingIcon,
      color: '#2196F3',
      features: [
        'Checksum & Auto-Repair corrupted system files via Samsung FOTA',
        'System Rollback to known-good "OS Snapshot"',
        'Seamless Config Restoration from Samsung Cloud'
      ],
      status: systemStatus.deep
    },
    {
      id: 'immune',
      name: 'Immune System',
      description: 'Autonomous protection against external threats and malware',
      icon: SecurityIcon,
      color: '#F44336',
      features: [
        'Behavioral AI Analysis for ransomware/spyware detection',
        'Auto-Quarantine malicious apps into Knox Vault sandbox',
        'Emergency Rollback to Knox-certified "Safe State"'
      ],
      status: systemStatus.immune
    },
    {
      id: 'regenerative',
      name: 'Regenerative Layer',
      description: 'Predictive analytics to prevent failures before they occur',
      icon: PsychologyIcon,
      color: '#FF9800',
      features: [
        'LSTM/RNN ML Models on Galaxy NPU for battery health prediction',
        'App crash probability analysis',
        'Storage NAND wear-level alerts'
      ],
      status: systemStatus.regenerative
    },
    {
      id: 'optimization',
      name: 'Self-Optimization',
      description: 'Continuously evolve device performance tailored to user',
      icon: SpeedIcon,
      color: '#9C27B0',
      features: [
        'Reinforcement Learning for dynamic CPU/GPU scheduling',
        'App Pre-loading based on predictive user habit analysis',
        'AI-Driven Task Scheduling for optimal battery and thermal management'
      ],
      status: systemStatus.optimization
    }
  ];

  const handleLayerClick = (layer) => {
    setActiveLayer(layer);
  };

  const handleStartStop = () => {
    setIsRunning(!isRunning);
    setSnackbarMessage(isRunning ? 'Galaxy Autopilot paused' : 'Galaxy Autopilot started');
    setSnackbarOpen(true);
  };

  const handleRefresh = () => {
    setSnackbarMessage('System status refreshed');
    setSnackbarOpen(true);
    // Simulate refresh
    setSystemStatus(prev => ({
      surface: { ...prev.surface, health: Math.min(100, prev.surface.health + Math.random() * 5) },
      deep: { ...prev.deep, health: Math.min(100, prev.deep.health + Math.random() * 5) },
      immune: { ...prev.immune, health: Math.min(100, prev.immune.health + Math.random() * 5) },
      regenerative: { ...prev.regenerative, health: Math.min(100, prev.regenerative.health + Math.random() * 5) },
      optimization: { ...prev.optimization, health: Math.min(100, prev.optimization.health + Math.random() * 5) }
    }));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircleIcon sx={{ color: '#4CAF50' }} />;
      case 'warning': return <WarningIcon sx={{ color: '#FF9800' }} />;
      case 'error': return <ErrorIcon sx={{ color: '#F44336' }} />;
      default: return <InfoIcon sx={{ color: '#2196F3' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'error': return '#F44336';
      default: return '#2196F3';
    }
  };

  return (
    <Box sx={{
      minHeight: '100vh',
      bgcolor: '#000000',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background Effects */}
      <Box sx={{
        position: 'absolute',
        inset: 0,
        opacity: 0.05,
        background: 'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 70%)'
      }} />

      {/* Header */}
      <Box sx={{
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
          background: 'radial-gradient(circle at center, rgba(59, 130, 246, 0.15) 0%, transparent 70%)',
          pointerEvents: 'none',
          zIndex: 0
        }
      }}>
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
              background: 'linear-gradient(to right, #ffffff, #a0aec0)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2
            }}
          >
            Galaxy Autopilot <span style={{ fontSize: '0.8em' }}>🚀</span>
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
              maxWidth: '800px',
              mx: 'auto',
              fontWeight: 300
            }}
          >
            Multi-Layer AI Self-Healing System for Galaxy Devices
          </Typography>
        </motion.div>

        {/* Control Buttons */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={isRunning ? <PauseIcon /> : <PlayArrowIcon />}
            onClick={handleStartStop}
            sx={{
              background: isRunning ? 'linear-gradient(45deg, #FF5252 30%, #FF8A80 90%)' : 'linear-gradient(45deg, #4CAF50 30%, #81C784 90%)',
              color: 'white',
              px: 3,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600
            }}
          >
            {isRunning ? 'Pause' : 'Start'} Autopilot
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            sx={{
              color: 'white',
              borderColor: 'rgba(255, 255, 255, 0.3)',
              px: 3,
              py: 1,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.6)',
                bgcolor: 'rgba(255, 255, 255, 0.05)'
              }
            }}
          >
            Refresh Status
          </Button>
        </Box>
      </Box>

      <Container maxWidth="xl" sx={{ pb: 8, px: { xs: 2, sm: 3, md: 6 }, position: 'relative', zIndex: 10 }}>
        <Box sx={{ maxWidth: '1400px', mx: 'auto' }}>
          {/* System Overview */}
          <Card sx={{
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(16px)',
            borderRadius: 3,
            border: '1px solid rgba(255, 255, 255, 0.1)',
            mb: 4
          }}>
            <CardHeader
              title={
                <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
                  System Overview
                </Typography>
              }
            />
            <CardContent>
              <Grid container spacing={3}>
                {healingLayers.map((layer) => (
                  <Grid item xs={12} sm={6} md={4} lg={2.4} key={layer.id}>
                    <Card
                      sx={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid rgba(255, 255, 255, 0.1)',
                        borderRadius: 2,
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        '&:hover': {
                          borderColor: layer.color,
                          boxShadow: `0 0 20px ${layer.color}40`,
                          transform: 'translateY(-4px)'
                        }
                      }}
                      onClick={() => handleLayerClick(layer)}
                    >
                      <CardContent sx={{ textAlign: 'center', p: 2 }}>
                        <Box sx={{ mb: 2 }}>
                          <layer.icon sx={{ fontSize: 40, color: layer.color }} />
                        </Box>
                        <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                          {layer.name}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
                          {getStatusIcon(layer.status.status)}
                          <Typography variant="caption" sx={{ color: getStatusColor(layer.status.status) }}>
                            {layer.status.status.toUpperCase()}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={layer.status.health}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: layer.color,
                              borderRadius: 3
                            }
                          }}
                        />
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', mt: 1, display: 'block' }}>
                          {layer.status.health}% Health
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Recent Actions */}
          <Card sx={{
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(16px)',
            borderRadius: 3,
            border: '1px solid rgba(255, 255, 255, 0.1)',
            mb: 4
          }}>
            <CardHeader
              title={
                <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
                  Recent Healing Actions
                </Typography>
              }
            />
            <CardContent>
              <List>
                {recentActions.map((action, index) => (
                  <React.Fragment key={action.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        {action.success ? (
                          <CheckCircleIcon sx={{ color: '#4CAF50' }} />
                        ) : (
                          <ErrorIcon sx={{ color: '#F44336' }} />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body1" sx={{ color: 'white', fontWeight: 500 }}>
                            {action.action}
                          </Typography>
                        }
                        secondary={
                          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                            <Chip
                              label={action.layer}
                              size="small"
                              sx={{
                                backgroundColor: healingLayers.find(l => l.id === action.layer)?.color + '20',
                                color: healingLayers.find(l => l.id === action.layer)?.color,
                                fontSize: '0.75rem',
                                height: 20
                              }}
                            />
                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                              {action.timestamp}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentActions.length - 1 && <Divider sx={{ bgcolor: 'rgba(255, 255, 255, 0.1)' }} />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Core Technologies */}
          <Card sx={{
            background: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(16px)',
            borderRadius: 3,
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <CardHeader
              title={
                <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
                  Core Technologies
                </Typography>
              }
            />
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <PsychologyIcon sx={{ fontSize: 48, color: '#2196F3', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                      Federated Reinforcement Learning
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      Devices learn optimal healing strategies locally while contributing to global intelligence through anonymized model weights.
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <SpeedIcon sx={{ fontSize: 48, color: '#4CAF50', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                      On-Device Execution
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      All AI inference runs locally on Galaxy NPU for maximum speed, efficiency, and user privacy.
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <InfoIcon sx={{ fontSize: 48, color: '#FF9800', mb: 2 }} />
                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 600, mb: 1 }}>
                      Explainable AI Interface
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      Clear, simple notifications build user trust with transparent explanations of healing actions.
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Box>
      </Container>

      {/* Layer Detail Dialog */}
      <Dialog
        open={!!activeLayer}
        onClose={() => setActiveLayer(null)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(0, 0, 0, 0.9)',
            backdropFilter: 'blur(16px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3
          }
        }}
      >
        {activeLayer && (
          <>
            <DialogTitle sx={{ color: 'white', display: 'flex', alignItems: 'center', gap: 2 }}>
              <activeLayer.icon sx={{ color: activeLayer.color }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {activeLayer.name}
              </Typography>
              <IconButton
                onClick={() => setActiveLayer(null)}
                sx={{ color: 'white', ml: 'auto' }}
              >
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 3 }}>
                {activeLayer.description}
              </Typography>
              <Typography variant="h6" sx={{ color: 'white', mb: 2, fontWeight: 600 }}>
                Key Features:
              </Typography>
              <List>
                {activeLayer.features.map((feature, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <CheckCircleIcon sx={{ color: activeLayer.color, fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          {feature}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
              <Box sx={{ mt: 3, p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', borderRadius: 2 }}>
                <Typography variant="subtitle2" sx={{ color: 'white', mb: 1, fontWeight: 600 }}>
                  Current Status:
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {getStatusIcon(activeLayer.status.status)}
                  <Typography variant="body2" sx={{ color: getStatusColor(activeLayer.status.status) }}>
                    {activeLayer.status.status.toUpperCase()}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={activeLayer.status.health}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: activeLayer.color,
                      borderRadius: 4
                    }
                  }}
                />
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)', mt: 1, display: 'block' }}>
                  Health Score: {activeLayer.status.health}%
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions sx={{ p: 3 }}>
              <Button
                onClick={() => setActiveLayer(null)}
                variant="outlined"
                sx={{
                  color: 'white',
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                  '&:hover': {
                    borderColor: 'rgba(255, 255, 255, 0.6)',
                    bgcolor: 'rgba(255, 255, 255, 0.05)'
                  }
                }}
              >
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity="success"
          sx={{ 
            width: '100%',
            backgroundColor: 'rgba(46, 125, 50, 0.9)',
            color: 'white',
            '& .MuiAlert-icon': {
              color: 'white'
            }
          }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
}
