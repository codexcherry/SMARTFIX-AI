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
  HelpOutline
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
            background: 'linear-gradient(to right, #6B73FF, #000DFF)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mb: 2
          }}
        >
          AI Assistant <span style={{ fontSize: '0.8em' }}>🤖</span>
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

const AssistantPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [showInfo, setShowInfo] = useState(!isMobile);

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
          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <GlassCard sx={{ 
              height: '70vh',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              mb: 4
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
                  <AssistantIcon sx={{ mr: 1 }} fontSize="small" />
                  Chat with Assistant
                </Typography>
              </Box>
              
              <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 1 }}>
                <SmartAssistantChat />
              </Box>
            </GlassCard>
          </motion.div>

        </Box>
      </Container>
    </Box>
  );
};

export default AssistantPage;