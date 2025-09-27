import React, { useState, useCallback } from 'react';
import { 
  Button, 
  Typography, 
  Box, 
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import DescriptionIcon from '@mui/icons-material/Description';
import SendIcon from '@mui/icons-material/Send';
import ClearIcon from '@mui/icons-material/Clear';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import FileCodeIcon from '@mui/icons-material/Code';
import { motion } from 'framer-motion';
import { submitLogQuery } from '../services/api';

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

const StyledLogFileForm = ({ onQueryComplete, setLoading: setParentLoading }) => {
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
    if (setParentLoading) setParentLoading(true);
    setError('');
    
    try {
      const result = await submitLogQuery(logFile);
      setLoading(false);
      if (setParentLoading) setParentLoading(false);
      
      if (onQueryComplete) {
        onQueryComplete(result);
      }
    } catch (err) {
      setLoading(false);
      if (setParentLoading) setParentLoading(false);
      setError('Error processing your log file. Please try again.');
      console.error('Error submitting log file:', err);
    }
  };

  const clearFile = () => {
    setLogFile(null);
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
          <FileCodeIcon sx={{ mr: 1 }} /> System Logs
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.7)',
            maxWidth: '800px'
          }}
        >
          Log file analysis and error detection for troubleshooting
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
            Log File Analysis
          </Typography>
          
          <form onSubmit={handleSubmit}>
            {!logFile ? (
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
                  <DescriptionIcon sx={{ fontSize: 64, color: 'rgba(255, 255, 255, 0.5)', mb: 2 }} />
                  <Typography sx={{ color: 'white', mb: 1 }}>
                    {isDragActive
                      ? "Drop the log file here"
                      : "Drag & drop a log file here, or click to select"}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                    Supported formats: LOG, TXT, XML, JSON, CSV
                  </Typography>
                </Box>
              </motion.div>
            ) : (
              <Box 
                sx={{ 
                  mb: 3, 
                  p: 2, 
                  borderRadius: 3,
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)'
                }}
              >
                <List>
                  <ListItem
                    secondaryAction={
                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={clearFile}
                          startIcon={<ClearIcon />}
                          sx={{ 
                            borderColor: 'rgba(244, 67, 54, 0.5)',
                            color: '#f44336',
                            '&:hover': {
                              backgroundColor: 'rgba(244, 67, 54, 0.1)',
                              borderColor: 'rgba(244, 67, 54, 0.8)'
                            }
                          }}
                        >
                          Remove
                        </Button>
                      </motion.div>
                    }
                  >
                    <ListItemIcon>
                      <InsertDriveFileIcon sx={{ color: '#90caf9' }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={logFile.name} 
                      secondary={`${(logFile.size / 1024).toFixed(2)} KB`}
                      primaryTypographyProps={{ color: 'white' }}
                      secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
                    />
                  </ListItem>
                </List>
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
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
                <Button 
                  type="submit" 
                  variant="contained" 
                  disabled={loading || !logFile}
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

export default StyledLogFileForm;
