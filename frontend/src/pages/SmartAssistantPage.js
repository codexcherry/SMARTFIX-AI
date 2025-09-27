import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  SmartToy as AssistantIcon,
  Psychology,
  Memory,
  Lightbulb,
  Settings,
  Info as InfoIcon,
  HelpOutline,
  Wifi,
  WifiOff,
  CloudDone,
  CloudOff
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import SmartAssistantChat from '../components/SmartAssistantChat';
import NetworkStatusIndicator from '../components/NetworkStatusIndicator';

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
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          borderRadius: 'inherit',
          padding: '1px',
          background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(147, 51, 234, 0.3))',
          mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          maskComposite: 'xor',
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
        }
      }}
      {...props}
    >
      {children}
    </Card>
  );
};

const SmartAssistantPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        position: 'relative',
        overflow: 'auto'
      }}
    >
      {/* Animated Background Elements */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: 'hidden',
          zIndex: 0
        }}
      >
        {/* Floating orbs */}
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            animate={{
              x: [0, 100, 0],
              y: [0, -100, 0],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 20 + i * 5,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              position: 'absolute',
              top: `${20 + i * 15}%`,
              left: `${10 + i * 15}%`,
              width: 60 + i * 20,
              height: 60 + i * 20,
              borderRadius: '50%',
              background: `radial-gradient(circle, rgba(59, 130, 246, ${0.1 - i * 0.01}) 0%, transparent 70%)`,
              filter: 'blur(40px)'
            }}
          />
        ))}
      </Box>

      <Container maxWidth="xl" sx={{ position: 'relative', zIndex: 1, py: 4 }}>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography
              variant="h2"
              sx={{
                fontFamily: '"Orbitron", sans-serif',
                fontWeight: 'bold',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2,
                fontSize: { xs: '2rem', md: '3rem' }
              }}
            >
              Smart Assistant
            </Typography>
            <Typography
              variant="h5"
              sx={{
                color: 'rgba(255, 255, 255, 0.8)',
                fontWeight: 300,
                mb: 3
              }}
            >
              Network-Aware AI Troubleshooting Assistant
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: 'rgba(255, 255, 255, 0.6)',
                maxWidth: '600px',
                mx: 'auto',
                lineHeight: 1.6
              }}
            >
              Experience intelligent technical support that automatically adapts to your network conditions.
              Get instant help whether you're online or offline.
            </Typography>
          </Box>
        </motion.div>

        <Grid container spacing={3}>
          {/* Main Chat Interface */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            style={{ width: '100%' }}
          >
            <Grid item xs={12} lg={8}>
              <GlassCard sx={{ 
                height: '120vh', 
                minHeight: '900px', 
                maxHeight: '1200px',
                maxWidth: '70%',
                mx: 'auto',
                display: 'flex', 
                flexDirection: 'column',
                overflow: 'hidden'
              }}>
                <SmartAssistantChat />
              </GlassCard>
            </Grid>
          </motion.div>

          {/* Status and Info Panel */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            style={{ width: '100%' }}
          >
            <Grid item xs={12} lg={4}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Status Card */}
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
                        <InfoIcon fontSize="small" />
                      </Box>
                      Smart Assistant Status
                    </Typography>
                    
                    <NetworkStatusIndicator />
                    
                    <Typography 
                      variant="body2" 
                      paragraph
                      sx={{ color: 'rgba(255, 255, 255, 0.8)', mt: 2 }}
                    >
                      The assistant automatically switches between online (Gemini AI) and offline modes based on network availability.
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      <Chip 
                        size="small" 
                        label="Network-Aware" 
                        color="primary" 
                        variant="outlined"
                      />
                      <Chip 
                        size="small" 
                        label="Auto-Switch" 
                        color="secondary" 
                        variant="outlined"
                      />
                      <Chip 
                        size="small" 
                        label="Context-Aware" 
                        color="success" 
                        variant="outlined"
                      />
                    </Box>
                  </CardContent>
                </GlassCard>

                {/* Features Card */}
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
                        <Lightbulb fontSize="small" />
                      </Box>
                      Key Features
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Wifi color="primary" fontSize="small" />
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          Online: Gemini AI with device logs
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <WifiOff color="secondary" fontSize="small" />
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          Offline: Local templates & LLM
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Psychology color="primary" fontSize="small" />
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          Smart intent detection
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Memory color="secondary" fontSize="small" />
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          1000+ troubleshooting solutions
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </GlassCard>

                {/* Quick Tips Card */}
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
                        <HelpOutline fontSize="small" />
                      </Box>
                      Quick Tips
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        • Say "hi" for a friendly greeting
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        • Describe your issue clearly
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        • Include device type and symptoms
                      </Typography>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        • System data is collected automatically
                      </Typography>
                    </Box>
                  </CardContent>
                </GlassCard>
              </Box>
            </Grid>
          </motion.div>
        </Grid>
      </Container>
    </Box>
  );
};

export default SmartAssistantPage;
