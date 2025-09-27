import React, { useState, useCallback } from 'react';
import { 
  TextField, 
  Button, 
  Typography, 
  Box, 
  CircularProgress,
  Alert,
  Card,
  CardContent
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import ImageIcon from '@mui/icons-material/Image';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';
import { motion } from 'framer-motion';
import { submitImageQuery } from '../services/api';

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

const StyledImageQueryForm = ({ onQueryComplete, setLoading: setParentLoading }) => {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [textQuery, setTextQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setImage(file);
      
      // Create image preview
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif']
    },
    maxFiles: 1
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!image) {
      setError('Please upload an image');
      return;
    }
    
    setLoading(true);
    if (setParentLoading) setParentLoading(true);
    setError('');
    
    try {
      const result = await submitImageQuery(image, textQuery);
      setLoading(false);
      if (setParentLoading) setParentLoading(false);
      
      if (onQueryComplete) {
        onQueryComplete(result);
      }
    } catch (err) {
      setLoading(false);
      if (setParentLoading) setParentLoading(false);
      setError('Error processing your image. Please try again.');
      console.error('Error submitting image query:', err);
    }
  };

  const clearImage = () => {
    setImage(null);
    setImagePreview('');
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
          <ImageIcon sx={{ mr: 1 }} /> Image Analysis
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.7)',
            maxWidth: '800px'
          }}
        >
          Computer vision and visual pattern recognition for troubleshooting
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
            Image Query
          </Typography>
          
          <form onSubmit={handleSubmit}>
            {!imagePreview ? (
              <motion.div
                whileHover={{ scale: 1.01, borderColor: 'rgba(59, 130, 246, 0.5)' }}
              >
                <Box 
                  {...getRootProps()} 
                  sx={{
                    border: '2px dashed rgba(255, 255, 255, 0.2)',
                    borderRadius: 3,
                    p: 4,
                    mb: 3,
                    textAlign: 'center',
                    cursor: 'pointer',
                    backgroundColor: isDragActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      backgroundColor: 'rgba(59, 130, 246, 0.05)',
                      borderColor: 'rgba(59, 130, 246, 0.3)'
                    }
                  }}
                >
                  <input {...getInputProps()} />
                  <ImageIcon sx={{ fontSize: 64, color: 'rgba(255, 255, 255, 0.5)', mb: 2 }} />
                  <Typography sx={{ color: 'white', mb: 1 }}>
                    {isDragActive
                      ? "Drop the image here"
                      : "Drag & drop an image here, or click to select"}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                    Supported formats: JPG, PNG, GIF
                  </Typography>
                </Box>
              </motion.div>
            ) : (
              <Box sx={{ position: 'relative', mb: 3 }}>
                <Box 
                  sx={{ 
                    borderRadius: 3,
                    overflow: 'hidden',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    maxWidth: '100%',
                    maxHeight: '350px',
                    display: 'flex',
                    justifyContent: 'center',
                    backgroundColor: 'rgba(0, 0, 0, 0.3)'
                  }}
                >
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '350px',
                      objectFit: 'contain'
                    }} 
                  />
                </Box>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant="contained"
                    size="small"
                    onClick={clearImage}
                    startIcon={<ClearIcon />}
                    sx={{ 
                      position: 'absolute', 
                      top: 12, 
                      right: 12,
                      backgroundColor: 'rgba(0, 0, 0, 0.7)',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'rgba(244, 67, 54, 0.8)'
                      }
                    }}
                  >
                    Remove
                  </Button>
                </motion.div>
              </Box>
            )}
            
            {error && (
              <Box 
                sx={{ 
                  mb: 3, 
                  p: 2, 
                  bgcolor: 'rgba(244, 67, 54, 0.1)', 
                  borderRadius: 2,
                  border: '1px solid rgba(244, 67, 54, 0.3)'
                }}
              >
                <Typography sx={{ color: '#f44336' }}>
                  {error}
                </Typography>
              </Box>
            )}
            
            <TextField
              fullWidth
              label="Additional description (optional)"
              variant="outlined"
              value={textQuery}
              onChange={(e) => setTextQuery(e.target.value)}
              placeholder="E.g., Error message on my TV screen"
              disabled={loading}
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
                '& .MuiInputLabel-root': {
                  color: 'rgba(255, 255, 255, 0.7)'
                },
                '& .MuiFormHelperText-root': {
                  color: '#f44336'
                }
              }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
                <Button 
                  type="submit" 
                  variant="contained" 
                  disabled={loading || !image}
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

export default StyledImageQueryForm;
