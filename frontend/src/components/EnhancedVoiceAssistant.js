import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Paper,
  IconButton,
  LinearProgress,
  Chip,
  Fade,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  useTheme,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Mic,
  MicOff,
  VolumeUp,
  Screenshot,
  Memory,
  Wifi,
  Computer,
  Check,
  Close,
  SettingsVoice,
  Hearing,
  QuestionAnswer
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Import API services
import { assistantApi } from '../services/assistantApi';

/**
 * Enhanced Voice Assistant Component
 * 
 * A comprehensive voice assistant with visual feedback, confidence indicators,
 * and confirmation for low-confidence transcriptions
 */
const EnhancedVoiceAssistant = ({ onSpeechResult = () => {} }) => {
  const theme = useTheme();
  const [isListening, setIsListening] = useState(false);
  const [processingCommand, setProcessingCommand] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [assistantResponse, setAssistantResponse] = useState(null);
  const [confidenceScore, setConfidenceScore] = useState(0);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationOptions, setConfirmationOptions] = useState([]);
  const [systemStatus, setSystemStatus] = useState('ready');
  const [visualFeedback, setVisualFeedback] = useState(null);
  const [animateWave, setAnimateWave] = useState(false);
  const waveRef = useRef(null);

  // Simulate microphone levels for visualization
  const [micLevels, setMicLevels] = useState([]);
  const micLevelInterval = useRef(null);

  // Toggle listening state
  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Start listening for voice commands
  const startListening = () => {
    setIsListening(true);
    setSystemStatus('listening');
    setAnimateWave(true);
    setTranscription('');
    setAssistantResponse(null);
    
    // Simulate microphone levels
    micLevelInterval.current = setInterval(() => {
      const newLevels = Array.from({ length: 20 }, () => 
        Math.floor(Math.random() * 100)
      );
      setMicLevels(newLevels);
    }, 100);
    
    // Simulate speech recognition after a delay
    setTimeout(() => {
      // This would be replaced with actual speech recognition
      simulateSpeechRecognition();
    }, 2000);
  };

  // Stop listening for voice commands
  const stopListening = () => {
    setIsListening(false);
    setAnimateWave(false);
    setSystemStatus('processing');
    
    if (micLevelInterval.current) {
      clearInterval(micLevelInterval.current);
    }
  };

  // Simulate speech recognition (would be replaced with actual implementation)
  const simulateSpeechRecognition = () => {
    // Example low-confidence transcription that needs confirmation
    const exampleTranscription = "I fell resolution for your issue with laptop extra";
    const exampleConfidence = 0.4; // Low confidence score
    
    setTranscription(exampleTranscription);
    setConfidenceScore(exampleConfidence);
    stopListening();
    
    // Show confirmation dialog for low confidence
    if (exampleConfidence < 0.6) {
      setConfirmationOptions([
        exampleTranscription,
        "I need resolution for your issue with laptop extra",
        "I have a resolution for your issue with laptop external monitor"
      ]);
      setShowConfirmation(true);
    } else {
      processCommand(exampleTranscription);
    }
  };

  // Process the voice command
  const processCommand = async (command) => {
    setProcessingCommand(true);
    setSystemStatus('processing');
    
    try {
      // This would call your backend API
      // For now, simulate a response after a delay
      setTimeout(() => {
        const simulatedResponse = {
          success: true,
          response: "I've found a solution for your issue with Laptop external monitor not detected. Most common symptoms: second monitor not recognized, no display output. Confidence: 88%. Here are the recommended steps to fix it:",
          steps: [
            { step_number: 1, description: "Check cable connections", details: "Ensure the cable is firmly connected to both the laptop and monitor." },
            { step_number: 2, description: "Try different ports", details: "If your laptop has multiple display ports, try connecting to a different one." },
            { step_number: 3, description: "Update graphics drivers", details: "Download and install the latest drivers for your graphics card." },
            { step_number: 4, description: "Use Windows key + P", details: "Press Windows+P to open display projection settings and select 'Extend' or 'Duplicate'." },
            { step_number: 5, description: "Test with different monitor", details: "If possible, try connecting a different monitor to isolate the issue." }
          ],
          type: "technical_solution",
          confidence: 88
        };
        
        setAssistantResponse(simulatedResponse);
        setProcessingCommand(false);
        setSystemStatus('ready');
        
        // Pass the result to the parent component
        onSpeechResult(simulatedResponse);
      }, 2000);
    } catch (error) {
      console.error("Error processing command:", error);
      setProcessingCommand(false);
      setSystemStatus('error');
      setAssistantResponse({
        success: false,
        response: "Sorry, I encountered an error processing your request.",
        type: "error",
        confidence: 0
      });
    }
  };

  // Handle confirmation selection
  const handleConfirmOption = (option) => {
    setShowConfirmation(false);
    setTranscription(option);
    processCommand(option);
  };

  // Cancel confirmation dialog
  const handleCancelConfirmation = () => {
    setShowConfirmation(false);
    setSystemStatus('ready');
    setTranscription('');
  };

  // Get status color
  const getStatusColor = () => {
    switch (systemStatus) {
      case 'listening':
        return theme.palette.success.main;
      case 'processing':
        return theme.palette.warning.main;
      case 'error':
        return theme.palette.error.main;
      default:
        return theme.palette.primary.main;
    }
  };

  // Get confidence level color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return theme.palette.success.main;
    if (confidence >= 0.6) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Get confidence level label
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return "High";
    if (confidence >= 0.6) return "Medium";
    return "Low";
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (micLevelInterval.current) {
        clearInterval(micLevelInterval.current);
      }
    };
  }, []);

  return (
    <Box sx={{ width: '100%' }}>
      {/* Main Voice Assistant Card */}
      <Paper 
        elevation={3}
        sx={{
          borderRadius: 2,
          overflow: 'hidden',
          backgroundColor: theme.palette.mode === 'dark' ? '#1a2027' : '#f5f5f5',
          border: '1px solid',
          borderColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        }}
      >
        {/* Header */}
        <Box 
          sx={{ 
            p: 2, 
            backgroundColor: theme.palette.mode === 'dark' ? '#0d1117' : '#e3f2fd',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <SettingsVoice sx={{ mr: 1 }} />
            <Typography variant="h6" fontWeight="bold">SmartFix Voice Assistant</Typography>
          </Box>
          
          <Chip 
            label={systemStatus.toUpperCase()}
            size="small"
            sx={{ 
              backgroundColor: getStatusColor(),
              color: '#fff',
              fontWeight: 'bold'
            }}
          />
        </Box>
        
        {/* Voice Visualization Area */}
        <Box 
          sx={{ 
            p: 3,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            height: 120,
            backgroundColor: theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.05)',
          }}
        >
          {/* Voice Waveform Visualization */}
          <Box 
            ref={waveRef}
            sx={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              width: '100%',
            }}
          >
            {animateWave && micLevels.map((level, index) => (
              <Box
                key={index}
                component={motion.div}
                animate={{ 
                  height: `${Math.max(10, level)}%`,
                  backgroundColor: level > 70 ? '#ff5722' : level > 40 ? '#2196f3' : '#90caf9'
                }}
                transition={{ duration: 0.1 }}
                sx={{
                  width: 4,
                  height: '10%',
                  mx: 0.5,
                  borderRadius: 1,
                  backgroundColor: theme.palette.primary.main,
                }}
              />
            ))}
            
            {!animateWave && !processingCommand && (
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{ fontStyle: 'italic' }}
              >
                Click the microphone to start speaking
              </Typography>
            )}
            
            {processingCommand && (
              <Box sx={{ display: 'flex', alignItems: 'center', flexDirection: 'column' }}>
                <CircularProgress size={24} sx={{ mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  Processing your request...
                </Typography>
              </Box>
            )}
          </Box>
          
          {/* Microphone Button */}
          <IconButton
            color={isListening ? "error" : "primary"}
            sx={{
              position: 'absolute',
              bottom: -20,
              width: 56,
              height: 56,
              backgroundColor: theme.palette.background.paper,
              boxShadow: theme.shadows[4],
              '&:hover': {
                backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.04)',
              },
              zIndex: 1
            }}
            onClick={toggleListening}
            disabled={processingCommand}
          >
            {isListening ? <MicOff /> : <Mic />}
          </IconButton>
        </Box>
        
        {/* Transcription Display */}
        <Box sx={{ p: 2, mt: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Listening...
          </Typography>
          
          <Box 
            sx={{ 
              p: 2, 
              backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)',
              borderRadius: 1,
              minHeight: 60,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {transcription ? (
              <Box sx={{ width: '100%' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body1" fontWeight="medium">
                    {transcription}
                  </Typography>
                  
                  <Chip 
                    label={`${Math.round(confidenceScore * 100)}% ${getConfidenceLabel(confidenceScore)}`}
                    size="small"
                    sx={{ 
                      backgroundColor: getConfidenceColor(confidenceScore),
                      color: '#fff',
                      fontSize: '0.7rem'
                    }}
                  />
                </Box>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                {isListening ? "I'm listening..." : "No speech detected"}
              </Typography>
            )}
          </Box>
        </Box>
        
        {/* Assistant Response */}
        {assistantResponse && (
          <Box sx={{ p: 2 }}>
            <Divider sx={{ mb: 2 }} />
            
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Assistant Response
            </Typography>
            
            <Box 
              sx={{ 
                p: 2, 
                backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)',
                borderRadius: 1,
              }}
            >
              <Typography variant="body1" paragraph>
                {assistantResponse.response}
              </Typography>
              
              {assistantResponse.steps && assistantResponse.steps.length > 0 && (
                <List dense>
                  {assistantResponse.steps.map((step, index) => (
                    <ListItem key={index} disableGutters>
                      <ListItemText 
                        primary={`${step.step_number}. ${step.description}`} 
                        secondary={step.details}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              {assistantResponse.confidence && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                    Solution confidence:
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={assistantResponse.confidence} 
                    sx={{ 
                      width: 100,
                      height: 8,
                      borderRadius: 1,
                      backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: getConfidenceColor(assistantResponse.confidence / 100)
                      }
                    }}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    {assistantResponse.confidence}%
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>
        )}
        
        {/* Quick Action Buttons */}
        <Box 
          sx={{ 
            p: 2, 
            backgroundColor: theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.2)' : 'rgba(0, 0, 0, 0.03)',
            display: 'flex',
            justifyContent: 'center',
            gap: 2
          }}
        >
          <Tooltip title="Take Screenshot">
            <IconButton color="primary" size="small">
              <Screenshot />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Check System">
            <IconButton color="primary" size="small">
              <Computer />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Check Network">
            <IconButton color="primary" size="small">
              <Wifi />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Check Performance">
            <IconButton color="primary" size="small">
              <Memory />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
      
      {/* Confirmation Dialog for Low Confidence */}
      <Dialog
        open={showConfirmation}
        onClose={handleCancelConfirmation}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Confirm what you said
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            I'm not completely sure what you said. Did you mean:
          </Typography>
          <List>
            {confirmationOptions.map((option, index) => (
              <ListItem 
                key={index} 
                button 
                onClick={() => handleConfirmOption(option)}
                sx={{
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': {
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.08)' 
                      : 'rgba(0, 0, 0, 0.04)',
                  }
                }}
              >
                <ListItemText primary={option} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelConfirmation} color="primary">
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EnhancedVoiceAssistant;
