import React, { useState } from 'react';
import { 
  TextField, 
  Button, 
  Typography, 
  Box, 
  CircularProgress,
  IconButton,
  Tooltip,
  Chip,
  Card,
  CardContent
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TextFieldsIcon from '@mui/icons-material/TextFields';
import { motion } from 'framer-motion';

// Glass Card Component (reused from SmartFlixDashboard)
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
        '&:hover': hover ? {
          borderColor: 'rgba(59, 130, 246, 0.3)',
          boxShadow: '0 0 20px rgba(59, 130, 246, 0.3), 0 0 40px rgba(59, 130, 246, 0.2)',
          transform: 'translateY(-5px)',
          '&::before': {
            opacity: 1
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
        ...props.sx
      }}
      {...props}
    >
      {children}
    </Card>
  );
};

const StyledTextQueryForm = ({ onQueryComplete, setLoading: setParentLoading }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [suggestions] = useState([
    'My TV screen is flickering',
    'WiFi keeps disconnecting',
    'Smartphone battery drains quickly',
    'Laptop overheating issue'
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }
    
    setLoading(true);
    setError('');
    if (setParentLoading) setParentLoading(true);
    
    try {
      // Import the API service
      const { submitTextQuery } = await import('../services/api');
      
      // Use the API service instead of direct fetch
      const result = await submitTextQuery(query, 'test_user');
      setLoading(false);
      if (setParentLoading) setParentLoading(false);
      
      
      if (onQueryComplete) {
        onQueryComplete(result);
      }
      
      setQuery('');
    } catch (err) {
      setLoading(false);
      if (setParentLoading) setParentLoading(false);
      setError('Error processing your query. Please try again.');
      console.error('Error submitting text query:', err);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
  };

  const handleClear = () => {
    setQuery('');
    setError('');
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontFamily: '"Orbitron", sans-serif',
            fontWeight: 700,
            color: '#3b82f6',
            mb: 1,
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <TextFieldsIcon sx={{ mr: 1 }} /> Text Processing
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.7)',
            maxWidth: '800px'
          }}
        >
          Advanced natural language processing and analysis for troubleshooting
        </Typography>
      </Box>
      
      <GlassCard sx={{ p: 3 }}>
        <CardContent>
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: '"Orbitron", sans-serif',
              color: 'white',
              mb: 3
            }}
          >
            What issue are you experiencing?
          </Typography>
          
          <form onSubmit={handleSubmit}>
            <Box sx={{ position: 'relative' }}>
              <TextField
                fullWidth
                variant="outlined"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Describe your issue in detail..."
                error={!!error}
                helperText={error}
                disabled={loading}
                multiline
                rows={3}
                sx={{ 
                  mb: 3,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.08)',
                      borderColor: 'rgba(59, 130, 246, 0.3)',
                    },
                    '&.Mui-focused': {
                      backgroundColor: 'rgba(255, 255, 255, 0.08)',
                      borderColor: 'rgba(59, 130, 246, 0.5)',
                    }
                  },
                  '& .MuiFormHelperText-root': {
                    color: '#f44336'
                  }
                }}
                InputProps={{
                  endAdornment: query && (
                    <IconButton 
                      size="small" 
                      onClick={handleClear}
                      sx={{ 
                        position: 'absolute', 
                        top: 8, 
                        right: 8,
                        color: 'rgba(255, 255, 255, 0.7)'
                      }}
                    >
                      <ClearIcon fontSize="small" />
                    </IconButton>
                  )
                }}
              />
            </Box>
            
            <Box sx={{ mb: 3 }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)',
                  mb: 1,
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <AutoAwesomeIcon fontSize="small" sx={{ mr: 1, color: '#90caf9' }} />
                Suggested queries:
              </Typography>
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {suggestions.map((suggestion, index) => (
                  <motion.div
                    key={index}
                    whileHover={{ y: -3, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Chip
                      label={suggestion}
                      onClick={() => handleSuggestionClick(suggestion)}
                      sx={{ 
                        borderRadius: 2,
                        bgcolor: 'rgba(59, 130, 246, 0.1)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        color: '#90caf9',
                        '&:hover': {
                          bgcolor: 'rgba(59, 130, 246, 0.2)',
                        }
                      }}
                    />
                  </motion.div>
                ))}
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
                <Button 
                  type="submit" 
                  variant="contained" 
                  disabled={loading || !query.trim()}
                  endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
                  sx={{ 
                    px: 4,
                    py: 1.2,
                    borderRadius: 2,
                    background: 'linear-gradient(45deg, #3b82f6 30%, #60a5fa 90%)',
                    boxShadow: '0 3px 5px 2px rgba(59, 130, 246, .3)',
                    color: 'white',
                    textTransform: 'none',
                    fontSize: '1rem',
                    fontWeight: 500,
                    '&.Mui-disabled': {
                      background: 'rgba(255, 255, 255, 0.12)',
                      color: 'rgba(255, 255, 255, 0.3)'
                    }
                  }}
                >
                  {loading ? 'Processing...' : 'Submit'}
                </Button>
              </motion.div>
            </Box>
          </form>
        </CardContent>
      </GlassCard>
    </Box>
  );
};

export default StyledTextQueryForm;
