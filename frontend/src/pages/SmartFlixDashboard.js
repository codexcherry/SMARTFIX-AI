"use client"

import React, { useState } from "react";
import { Box, Typography, Container, Button, Card, CardContent, CardHeader, Snackbar, Alert } from '@mui/material';
import { motion, AnimatePresence } from "framer-motion";
import SolutionDisplay from '../components/SolutionDisplay';
import StyledTextQueryForm from '../components/StyledTextQueryForm';
import StyledImageQueryForm from '../components/StyledImageQueryForm';
import StyledLogFileForm from '../components/StyledLogFileForm';
import AccessibilityMenu from '../components/AccessibilityMenu';
import ComputerIcon from '@mui/icons-material/Computer';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import ImageIcon from '@mui/icons-material/Image';
import FileCodeIcon from '@mui/icons-material/Code';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import MicIcon from '@mui/icons-material/Mic';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import CloseIcon from '@mui/icons-material/Close';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { useNavigate } from 'react-router-dom';

// SpotlightHero Component
const SpotlightHero = () => {
  return (
    <Box 
      sx={{
        position: 'relative',
        height: '30vh',
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
            background: 'linear-gradient(to right, #ffffff, #a0aec0)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2
          }}
        >
          SmartFlix <span style={{ fontSize: '0.8em' }}>🤖</span>
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
            fontWeight: 300
          }}
        >
          I'm here to troubleshoot, guide, and fix — what's on your mind
        </Typography>
      </motion.div>
    </Box>
  );
};

// Glass Card Component
const GlassCard = ({ children, onClick, hover = true, ...props }) => {
  return (
    <Card 
      onClick={onClick}
      sx={{
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(16px)',
        borderRadius: 3,
        border: '1px solid rgba(255, 255, 255, 0.1)',
        transition: 'all 0.3s ease',
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        '&:hover': hover ? {
          borderColor: 'rgba(59, 130, 246, 0.9)',
          boxShadow: '0 0 40px rgba(59, 130, 246, 0.8), 0 0 80px rgba(59, 130, 246, 0.6), 0 0 120px rgba(59, 130, 246, 0.4), 0 0 160px rgba(59, 130, 246, 0.2)',
          transform: 'translateY(-8px) scale(1.02)',
          '&::before': {
            opacity: 1
          }
        } : {},
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: -2,
          background: 'transparent',
          borderRadius: 'inherit',
          zIndex: -1,
          opacity: 0,
          transition: 'opacity 0.3s ease'
        },
        ...props.sx
      }}
      {...props}
    >
      {children}
    </Card>
  );
};

export default function SmartFlixDashboard() {
  const [activeCard, setActiveCard] = useState(null);
  const [solution, setSolution] = useState(null);
  const [queryId, setQueryId] = useState(null);
  // We need loading state for the component props, even though we don't use it directly
  const [loading, setLoading] = useState(false); // eslint-disable-line no-unused-vars
  const [gestureControlActive, setGestureControlActive] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const navigate = useNavigate();
  
  const handleStartGestureControl = () => {
    try {
      // Use fetch to make a POST request to start the gesture control
      fetch('/api/start-gesture-control', {
        method: 'POST',
      })
      .then(response => {
        if (response.ok) {
          setGestureControlActive(true);
          setSnackbarMessage('Gesture control started. Use hand movements and eye blinks to control the app.');
          setSnackbarOpen(true);
        } else {
          console.error('Failed to start gesture control');
          setSnackbarMessage('Failed to start gesture control. Make sure Python dependencies are installed.');
          setSnackbarOpen(true);
        }
      })
      .catch(error => {
        console.error('Error starting gesture control:', error);
        // Fallback for development - show success message even if backend is not available
        setGestureControlActive(true);
        setSnackbarMessage('Gesture control started in simulation mode. In production, this would activate camera tracking.');
        setSnackbarOpen(true);
      });
    } catch (error) {
      console.error('Error starting gesture control:', error);
      setSnackbarMessage('Error starting gesture control: ' + error.message);
      setSnackbarOpen(true);
    }
  };

  const handleQueryComplete = (result) => {
    setSolution(result.solution);
    setQueryId(result.query_id);
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const clearSolution = () => {
    setSolution(null);
    setQueryId(null);
    setActiveCard(null);
  };

  const featureCards = [
    {
      id: "device",
      title: "Device Analysis",
      description: "Neural network diagnostics and system analysis",
      icon: ComputerIcon,
      path: '/device-analyzer',
    },
    {
      id: "text",
      title: "Text Processing",
      description: "Advanced natural language processing and analysis",
      icon: TextFieldsIcon,
      component: StyledTextQueryForm,
    },
    {
      id: "image",
      title: "Image Analysis",
      description: "Computer vision and visual pattern recognition",
      icon: ImageIcon,
      component: StyledImageQueryForm,
    },
    {
      id: "logs",
      title: "System Logs",
      description: "Log file analysis and error detection",
      icon: FileCodeIcon,
      component: StyledLogFileForm,
    },
    {
      id: "ai-assistant",
      title: "AI Assistant",
      description: "Intelligent conversational AI interface",
      icon: SmartToyIcon,
      component: null,
      path: '/assistant'
    },
    {
      id: "voice",
      title: "Voice Assistant",
      description: "Voice synthesis and audio processing",
      icon: MicIcon,
      component: null,
      path: '/voice-assistant'
    },
    {
      id: "galaxy-autopilot",
      title: "Galaxy Autopilot",
      description: "Multi-Layer AI Self-Healing System",
      icon: AutoFixHighIcon,
      component: null,
      path: '/galaxy-autopilot'
    },
  ];

  return (
    <Box className="min-h-screen" sx={{
      minHeight: '100vh',
      bgcolor: '#000000',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <Box sx={{
        position: 'absolute',
        inset: 0,
        opacity: 0.05,
        background: 'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 70%)'
      }} />

      <SpotlightHero />
      
      {/* Accessibility Menu */}
      <AccessibilityMenu onStartGestureControl={handleStartGestureControl} />
      
      {/* Notification Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity={gestureControlActive ? "success" : "error"}
          sx={{ 
            width: '100%',
            backgroundColor: gestureControlActive ? 'rgba(46, 125, 50, 0.9)' : 'rgba(211, 47, 47, 0.9)',
            color: 'white',
            '& .MuiAlert-icon': {
              color: 'white'
            }
          }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>

      <Container maxWidth="xl" sx={{ pb: 8, px: { xs: 2, sm: 3, md: 6 }, position: 'relative', zIndex: 10 }}>
        <Box sx={{ maxWidth: '1400px', mx: 'auto' }}>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { 
              xs: '1fr', 
              lg: solution ? '7fr 5fr' : '1fr' 
            },
            gap: 4
          }}>
            <Box>
              <AnimatePresence>
                {solution && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    style={{ marginBottom: '24px' }}
                  >
                    <Button
                      onClick={clearSolution}
                      variant="contained"
                      color="error"
                      size="small"
                      startIcon={<CloseIcon />}
                      sx={{
                        background: 'rgba(0, 0, 0, 0.85)',
                        backdropFilter: 'blur(12px)',
                        border: '1px solid rgba(255, 255, 255, 0.15)',
                        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6)',
                        borderRadius: 2,
                        '&:hover': {
                          background: 'rgba(239, 68, 68, 0.2)'
                        }
                      }}
                    >
                      Close
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>

              {!activeCard ? (
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                    gap: '32px'
                  }}
                >
                  {featureCards.map((card, index) => (
                    <motion.div
                      key={card.id}
                      initial={{ opacity: 0, y: 30 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <GlassCard 
                        onClick={() => {
                          if (card.path) {
                            navigate(card.path);
                          } else {
                            setActiveCard(card);
                          }
                        }}
                      >
                        <CardHeader
                          sx={{ pb: 1 }}
                          title={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                              <Box 
                                sx={{ 
                                  p: 2, 
                                  borderRadius: 3, 
                                  bgcolor: 'rgba(255, 255, 255, 0.05)', 
                                  border: '1px solid rgba(255, 255, 255, 0.1)',
                                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
                                  transition: 'all 0.3s ease',
                                  '.MuiCard-root:hover &': {
                                    bgcolor: 'rgba(255, 255, 255, 0.1)'
                                  }
                                }}
                              >
                                <card.icon sx={{ fontSize: 32, color: 'white' }} />
                              </Box>
                              <ChevronRightIcon sx={{ 
                                color: 'rgba(255, 255, 255, 0.6)',
                                transition: 'all 0.3s ease',
                                '.MuiCard-root:hover &': {
                                  transform: 'translateX(4px)',
                                  color: 'white'
                                }
                              }} />
                            </Box>
                          }
                        />
                        <CardContent>
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              color: 'white', 
                              fontWeight: 600,
                              mb: 1,
                              fontFamily: '"Orbitron", sans-serif'
                            }}
                          >
                            {card.title}
                          </Typography>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              color: 'rgba(255, 255, 255, 0.7)',
                              lineHeight: 1.6
                            }}
                          >
                            {card.description}
                          </Typography>
                        </CardContent>
                      </GlassCard>
                    </motion.div>
                  ))}
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4 }}
                >
                  <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Button
                      onClick={() => setActiveCard(null)}
                      variant="outlined"
                      startIcon={<ChevronLeftIcon />}
                      sx={{
                        color: 'white',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        '&:hover': {
                          borderColor: 'rgba(255, 255, 255, 0.4)',
                          bgcolor: 'rgba(255, 255, 255, 0.05)'
                        }
                      }}
                    >
                      Back
                    </Button>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box 
                        sx={{ 
                          p: 1.5, 
                          borderRadius: 2, 
                          bgcolor: 'rgba(255, 255, 255, 0.1)',
                          border: '1px solid rgba(255, 255, 255, 0.2)'
                        }}
                      >
                        <activeCard.icon sx={{ fontSize: 24, color: 'white' }} />
                      </Box>
                      <Typography 
                        variant="h5" 
                        sx={{ 
                          color: 'white', 
                          fontWeight: 700,
                          fontFamily: '"Orbitron", sans-serif'
                        }}
                      >
                        {activeCard.title}
                      </Typography>
                    </Box>
                  </Box>

                  <GlassCard hover={false} sx={{ p: 2 }}>
                    <CardContent sx={{ p: 3 }}>
                      {activeCard.component ? (
                        <activeCard.component onQueryComplete={handleQueryComplete} setLoading={setLoading} />
                      ) : (
                        <Box sx={{ textAlign: 'center', py: 6 }}>
                          <activeCard.icon sx={{ fontSize: 64, color: 'rgba(255, 255, 255, 0.3)', mx: 'auto', mb: 2 }} />
                          <Typography variant="h6" sx={{ color: 'white', mb: 1, fontWeight: 600 }}>
                            Coming Soon
                          </Typography>
                          <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                            This feature is under development in our neural labs.
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </GlassCard>
                </motion.div>
              )}
            </Box>

            <AnimatePresence>
              {solution && (
                <motion.div
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 30 }}
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                >
                  <SolutionDisplay solution={solution} queryId={queryId} />
                </motion.div>
              )}
            </AnimatePresence>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}