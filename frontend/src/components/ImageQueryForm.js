import React, { useState, useCallback } from 'react';
import { 
  TextField, 
  Button, 
  Paper, 
  Typography, 
  Box, 
  CircularProgress,
  Alert
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import ImageIcon from '@mui/icons-material/Image';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';

import { submitImageQuery } from '../services/api';

const ImageQueryForm = ({ onQueryComplete }) => {
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
    setError('');
    
    try {
      const result = await submitImageQuery(image, textQuery);
      setLoading(false);
      
      if (onQueryComplete) {
        onQueryComplete(result);
      }
    } catch (err) {
      setLoading(false);
      setError('Error processing your image. Please try again.');
      console.error('Error submitting image query:', err);
    }
  };

  const clearImage = () => {
    setImage(null);
    setImagePreview('');
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Image Query
      </Typography>
      
      <form onSubmit={handleSubmit}>
        {!imagePreview ? (
          <Box 
            {...getRootProps()} 
            sx={{
              border: '2px dashed #cccccc',
              borderRadius: 2,
              p: 3,
              mb: 2,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive ? '#f0f0f0' : 'transparent',
              '&:hover': {
                backgroundColor: '#f0f0f0'
              }
            }}
          >
            <input {...getInputProps()} />
            <ImageIcon sx={{ fontSize: 48, color: '#999', mb: 1 }} />
            <Typography>
              {isDragActive
                ? "Drop the image here"
                : "Drag & drop an image here, or click to select"}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: JPG, PNG, GIF
            </Typography>
          </Box>
        ) : (
          <Box sx={{ position: 'relative', mb: 2 }}>
            <img 
              src={imagePreview} 
              alt="Preview" 
              style={{ 
                maxWidth: '100%', 
                maxHeight: '300px',
                borderRadius: '8px'
              }} 
            />
            <Button
              variant="contained"
              color="error"
              size="small"
              onClick={clearImage}
              startIcon={<ClearIcon />}
              sx={{ 
                position: 'absolute', 
                top: 8, 
                right: 8,
                opacity: 0.8,
                '&:hover': {
                  opacity: 1
                }
              }}
            >
              Remove
            </Button>
          </Box>
        )}
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <TextField
          fullWidth
          label="Additional description (optional)"
          variant="outlined"
          value={textQuery}
          onChange={(e) => setTextQuery(e.target.value)}
          placeholder="E.g., Error message on my TV screen"
          disabled={loading}
          sx={{ mb: 2 }}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || !image}
            endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
          >
            {loading ? 'Processing...' : 'Submit'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default ImageQueryForm;
