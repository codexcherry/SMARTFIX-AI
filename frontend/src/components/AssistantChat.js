import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Avatar,
  CircularProgress,
  IconButton,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Fade,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AssistantIcon,
  Person as UserIcon,
  Stop as StopIcon,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Lightbulb,
  Psychology,
  AutoAwesome,
  KeyboardArrowDown as ScrollDownIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { queryAssistant, getAssistantStatus } from '../services/assistantApi';

const AssistantChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [assistantStatus, setAssistantStatus] = useState(null);
  const [error, setError] = useState(null);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [suggestions] = useState([
    'How do I fix a blue screen error?',
    'My laptop battery drains too quickly',
    'WiFi keeps disconnecting randomly',
    'Computer is running very slowly'
  ]);

  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  
  useEffect(() => {
    // Check assistant status on component mount
    checkAssistantStatus();
    
    // Add welcome message
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your SmartFix AI Assistant. How can I help you troubleshoot your device today?',
        timestamp: new Date()
      }
    ]);
  }, []);
  
  useEffect(() => {
    // Scroll to bottom when messages change
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add scroll event listener to detect when user scrolls up
    const container = messagesContainerRef.current;
    if (container) {
      const handleScroll = () => {
        const { scrollTop, scrollHeight, clientHeight } = container;
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
        setShowScrollButton(!isNearBottom);
      };

      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  const checkAssistantStatus = async () => {
    try {
      const status = await getAssistantStatus();
      setAssistantStatus(status);
    } catch (err) {
      console.error('Error checking assistant status:', err);
      setError('Unable to connect to the assistant service');
    }
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    
    try {
      // Add typing indicator
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '', isTyping: true }
      ]);
      
      // Get response from assistant
      const response = await queryAssistant(input);
      
      // Remove typing indicator and add real response
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isTyping);
        return [
          ...filtered,
          {
            role: 'assistant',
            content: response.answer,
            solution_steps: response.solution_steps,
            confidence: response.confidence,
            timestamp: new Date()
          }
        ];
      });
    } catch (err) {
      console.error('Error querying assistant:', err);
      setError('Failed to get a response from the assistant');
      
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => !msg.isTyping));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.5) return 'warning';
    return 'error';
  };

  const renderMessage = (message, index) => {
    const isAssistant = message.role === 'assistant';
    
    if (message.isTyping) {
      return (
        <Box
          key="typing"
          sx={{
            display: 'flex',
            justifyContent: isAssistant ? 'flex-start' : 'flex-end',
            mb: 2
          }}
        >
          <Paper
            elevation={1}
            sx={{
              p: 2,
              maxWidth: '80%',
              backgroundColor: isAssistant ? 'background.paper' : 'primary.main',
              color: isAssistant ? 'text.primary' : 'white',
              borderRadius: 2,
              borderTopLeftRadius: isAssistant ? 0 : 2,
              borderTopRightRadius: isAssistant ? 2 : 0
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <Typography variant="body2">Thinking...</Typography>
            </Box>
          </Paper>
        </Box>
      );
    }
    
    return (
      <Box
        key={index}
        sx={{
          display: 'flex',
          justifyContent: isAssistant ? 'flex-start' : 'flex-end',
          mb: 2
        }}
      >
        {isAssistant && (
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              width: 36,
              height: 36,
              mr: 1,
              mt: 1
            }}
          >
            <AssistantIcon fontSize="small" />
          </Avatar>
        )}
        
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          style={{ maxWidth: '80%' }}
        >
          <Paper
            elevation={1}
            sx={{
              p: 2,
              backgroundColor: isAssistant ? 'background.paper' : 'primary.main',
              color: isAssistant ? 'text.primary' : 'white',
              borderRadius: 2,
              borderTopLeftRadius: isAssistant ? 0 : 2,
              borderTopRightRadius: isAssistant ? 2 : 0
            }}
          >
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {message.content}
            </Typography>
            
            {isAssistant && message.solution_steps && message.solution_steps.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ my: 1 }} />
                <Typography variant="subtitle2" sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 0.5,
                  color: 'primary.main',
                  fontWeight: 'bold'
                }}>
                  <Lightbulb fontSize="small" color="primary" />
                  Recommended Solution:
                </Typography>
                <Box sx={{ 
                  mt: 1, 
                  p: 1.5, 
                  bgcolor: 'rgba(25, 118, 210, 0.08)', 
                  borderRadius: 1,
                  border: '1px solid rgba(25, 118, 210, 0.2)'
                }}>
                  <List dense disablePadding>
                    {message.solution_steps.map((step, i) => (
                      <ListItem key={i} disablePadding sx={{ py: 0.5 }}>
                        <ListItemIcon sx={{ minWidth: 28 }}>
                          <CheckCircle fontSize="small" color="success" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={step} 
                          primaryTypographyProps={{ 
                            fontWeight: 500,
                            color: 'text.primary'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </Box>
            )}
            
            {isAssistant && typeof message.confidence === 'number' && (
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                <Tooltip title="Confidence score indicates how certain the assistant is about this answer">
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      Confidence
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={message.confidence * 100}
                      color={getConfidenceColor(message.confidence)}
                      sx={{ width: 100, height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" fontWeight="bold" color={`${getConfidenceColor(message.confidence)}.main`}>
                      {Math.round(message.confidence * 100)}%
                    </Typography>
                  </Box>
                </Tooltip>
              </Box>
            )}
          </Paper>
        </motion.div>
        
        {!isAssistant && (
          <Avatar
            sx={{
              bgcolor: 'grey.400',
              width: 36,
              height: 36,
              ml: 1,
              mt: 1
            }}
          >
            <UserIcon fontSize="small" />
          </Avatar>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Assistant Status */}
      {assistantStatus && (
        <Card sx={{ mb: 2 }}>
          <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AutoAwesome color="primary" sx={{ mr: 1 }} />
                <Typography variant="body2">
                  Assistant Status: {assistantStatus.status}
                </Typography>
              </Box>
              <Chip 
                size="small"
                label={assistantStatus.llm_available ? "LLM Available" : "Basic Mode"}
                color={assistantStatus.llm_available ? "success" : "default"}
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>
      )}
      
      {/* Error Alert */}
      {error && (
        <Fade in={!!error}>
          <Box 
            sx={{ 
              p: 2, 
              mb: 2, 
              bgcolor: 'error.light', 
              color: 'error.contrastText',
              borderRadius: 1
            }}
          >
            <Typography variant="body2">{error}</Typography>
          </Box>
        </Fade>
      )}
      
      {/* Messages Container */}
      <Box
        ref={messagesContainerRef}
        sx={{
          flexGrow: 1,
          overflowY: 'auto',
          p: 2,
          backgroundColor: 'background.default',
          borderRadius: 1,
          mb: 2,
          maxHeight: 'calc(100vh - 300px)',
          position: 'relative',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'rgba(0,0,0,0.1)',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'rgba(0,0,0,0.3)',
            borderRadius: '4px',
            '&:hover': {
              background: 'rgba(0,0,0,0.5)',
            },
          },
        }}
      >
        {messages.map(renderMessage)}
        <div ref={messagesEndRef} />
        
        {/* Scroll to bottom button */}
        {showScrollButton && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            style={{
              position: 'absolute',
              bottom: 16,
              right: 16,
              zIndex: 10
            }}
          >
            <IconButton
              onClick={scrollToBottom}
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                '&:hover': {
                  bgcolor: 'primary.dark',
                  transform: 'scale(1.1)'
                },
                transition: 'all 0.2s ease'
              }}
            >
              <ScrollDownIcon />
            </IconButton>
          </motion.div>
        )}
      </Box>
      
      {/* Suggestions */}
      {messages.length <= 2 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Suggested queries:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {suggestions.map((suggestion, index) => (
              <Chip
                key={index}
                label={suggestion}
                onClick={() => handleSuggestionClick(suggestion)}
                sx={{ 
                  borderRadius: 2,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
                  }
                }}
              />
            ))}
          </Box>
        </Box>
      )}
      
      {/* Input Area */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your question here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          multiline
          maxRows={3}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
            }
          }}
        />
        <Box>
          <Button
            variant="contained"
            color="primary"
            endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
            onClick={handleSend}
            disabled={loading || !input.trim()}
            sx={{ 
              borderRadius: 2,
              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              px: 3
            }}
          >
            {loading ? 'Sending...' : 'Send'}
          </Button>
        </Box>
      </Box>

      {/* Custom CSS for typing indicator */}
      <style jsx="true">{`
        .typing-indicator {
          display: flex;
          align-items: center;
        }
        
        .typing-indicator span {
          height: 8px;
          width: 8px;
          background-color: #3f51b5;
          border-radius: 50%;
          display: inline-block;
          margin-right: 3px;
          animation: bounce 1.5s infinite ease-in-out;
        }
        
        .typing-indicator span:nth-child(1) {
          animation-delay: 0s;
        }
        
        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }
        
        @keyframes bounce {
          0%, 60%, 100% {
            transform: translateY(0);
          }
          30% {
            transform: translateY(-4px);
          }
        }
      `}</style>
    </Box>
  );
};

export default AssistantChat;
