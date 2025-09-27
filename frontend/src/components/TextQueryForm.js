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
  Fade
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

const TextQueryForm = ({ onQueryComplete, setLoading: setParentLoading }) => {
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
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 500, mb: 2 }}>
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
              mb: 2,
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                },
                '&.Mui-focused': {
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                }
              }
            }}
            InputProps={{
              endAdornment: query && (
                <IconButton 
                  size="small" 
                  onClick={handleClear}
                  sx={{ position: 'absolute', top: 8, right: 8 }}
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              )
            }}
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <AutoAwesomeIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
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
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || !query.trim()}
            endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
            sx={{ 
              px: 4,
              py: 1,
              borderRadius: 2,
              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
            }}
          >
            {loading ? 'Processing...' : 'Submit'}
          </Button>
        </Box>
      </form>
    </Box>
  );
};

export default TextQueryForm;