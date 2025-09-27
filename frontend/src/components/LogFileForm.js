import React, { useState, useCallback } from 'react';
import { 
  Button, 
  Paper, 
  Typography, 
  Box, 
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import DescriptionIcon from '@mui/icons-material/Description';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

import { submitLogQuery } from '../services/api';

const LogFileForm = ({ onQueryComplete }) => {
  const [logFile, setLogFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setLogFile(file);
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.log', '.txt', '.xml', '.json', '.csv'],
      'application/json': ['.json'],
      'application/xml': ['.xml']
    },
    maxFiles: 1
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!logFile) {
      setError('Please upload a log file');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const result = await submitLogQuery(logFile);
      setLoading(false);
      
      if (onQueryComplete) {
        onQueryComplete(result);
      }
    } catch (err) {
      setLoading(false);
      setError('Error processing your log file. Please try again.');
      console.error('Error submitting log file:', err);
    }
  };

  const clearFile = () => {
    setLogFile(null);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Log File Analysis
      </Typography>
      
      <form onSubmit={handleSubmit}>
        {!logFile ? (
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
            <DescriptionIcon sx={{ fontSize: 48, color: '#999', mb: 1 }} />
            <Typography>
              {isDragActive
                ? "Drop the log file here"
                : "Drag & drop a log file here, or click to select"}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Supported formats: LOG, TXT, XML, JSON, CSV
            </Typography>
          </Box>
        ) : (
          <Box sx={{ mb: 2 }}>
            <List>
              <ListItem
                secondaryAction={
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={clearFile}
                    startIcon={<ClearIcon />}
                  >
                    Remove
                  </Button>
                }
              >
                <ListItemIcon>
                  <InsertDriveFileIcon />
                </ListItemIcon>
                <ListItemText 
                  primary={logFile.name} 
                  secondary={`${(logFile.size / 1024).toFixed(2)} KB`} 
                />
              </ListItem>
            </List>
          </Box>
        )}
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || !logFile}
            endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
          >
            {loading ? 'Processing...' : 'Submit'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default LogFileForm;
