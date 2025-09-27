import React, { useState } from 'react';
import {
  Box,
  Typography,
  Divider,
  Chip,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  IconButton,
  Paper,
  Tooltip,
  useTheme
} from '@mui/material';
import {
  CheckCircleOutline,
  ErrorOutline,
  ExpandMore,
  ExpandLess,
  InfoOutlined,
  HelpOutline,
  BookmarkBorder,
  Send,
  ContentCopy,
  Share
} from '@mui/icons-material';

/**
 * Enhanced Diagnosis Panel Component
 * 
 * A comprehensive diagnosis panel that displays detailed troubleshooting steps
 * with confidence indicators and expandable sections
 */
const EnhancedDiagnosisPanel = ({ 
  diagnosisData,
  onSendSolution = () => {},
  onCopySolution = () => {},
  onShareSolution = () => {}
}) => {
  const theme = useTheme();
  const [expandedSteps, setExpandedSteps] = useState({});
  const [expandedCauses, setExpandedCauses] = useState(false);
  const [expandedDetails, setExpandedDetails] = useState(false);

  // Default data if not provided
  const data = diagnosisData || {
    title: "No diagnosis available",
    confidence: 0,
    possibleCauses: [],
    steps: [],
    details: {}
  };

  // Toggle step expansion
  const toggleStep = (stepIndex) => {
    setExpandedSteps({
      ...expandedSteps,
      [stepIndex]: !expandedSteps[stepIndex]
    });
  };

  // Get confidence level color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return theme.palette.success.main;
    if (confidence >= 60) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Get confidence level label
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 80) return "High";
    if (confidence >= 60) return "Medium";
    return "Low";
  };

  return (
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
        <Typography variant="h6" fontWeight="bold">{data.title}</Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ mr: 1 }}>Confidence:</Typography>
          <Chip 
            label={`${data.confidence}% ${getConfidenceLabel(data.confidence)}`}
            size="small"
            sx={{ 
              backgroundColor: getConfidenceColor(data.confidence),
              color: '#fff',
              fontWeight: 'bold'
            }}
          />
        </Box>
      </Box>
      
      <Divider />
      
      {/* Possible Causes */}
      <Box sx={{ p: 2 }}>
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 1,
            cursor: 'pointer'
          }}
          onClick={() => setExpandedCauses(!expandedCauses)}
        >
          <Typography variant="subtitle1" fontWeight="bold">
            Possible Causes:
          </Typography>
          <IconButton size="small">
            {expandedCauses ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedCauses || data.possibleCauses.length <= 3}>
          <List dense disablePadding>
            {data.possibleCauses.map((cause, index) => (
              <ListItem key={index} disableGutters>
                <ListItemIcon sx={{ minWidth: 28 }}>
                  <ErrorOutline fontSize="small" color="warning" />
                </ListItemIcon>
                <ListItemText primary={cause} />
              </ListItem>
            ))}
          </List>
        </Collapse>
      </Box>
      
      <Divider />
      
      {/* Recommended Steps */}
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 2 }}>
          Recommended Steps:
        </Typography>
        
        {data.steps.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
            No steps available for this diagnosis
          </Typography>
        ) : (
          <List sx={{ width: '100%' }}>
            {data.steps.map((step, index) => (
              <React.Fragment key={index}>
                <ListItem 
                  alignItems="flex-start"
                  secondaryAction={
                    step.details && (
                      <IconButton 
                        edge="end" 
                        size="small"
                        onClick={() => toggleStep(index)}
                      >
                        {expandedSteps[index] ? <ExpandLess /> : <ExpandMore />}
                      </IconButton>
                    )
                  }
                  sx={{
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.05)' 
                      : 'rgba(0, 0, 0, 0.03)',
                    borderRadius: 1,
                    mb: 1,
                    '&:hover': {
                      backgroundColor: theme.palette.mode === 'dark' 
                        ? 'rgba(255, 255, 255, 0.08)' 
                        : 'rgba(0, 0, 0, 0.05)',
                    }
                  }}
                >
                  <ListItemIcon>
                    <Box 
                      sx={{ 
                        width: 28, 
                        height: 28, 
                        borderRadius: '50%', 
                        backgroundColor: theme.palette.primary.main,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 'bold'
                      }}
                    >
                      {index + 1}
                    </Box>
                  </ListItemIcon>
                  <ListItemText 
                    primary={step.description}
                    primaryTypographyProps={{ fontWeight: 'medium' }}
                  />
                </ListItem>
                
                {/* Step Details */}
                {step.details && (
                  <Collapse in={expandedSteps[index]} timeout="auto" unmountOnExit>
                    <Box sx={{ pl: 7, pr: 2, pb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {step.details}
                      </Typography>
                      
                      {step.image && (
                        <Box 
                          component="img"
                          src={step.image}
                          alt={`Step ${index + 1}`}
                          sx={{ 
                            maxWidth: '100%',
                            maxHeight: 200,
                            objectFit: 'contain',
                            mt: 1,
                            borderRadius: 1
                          }}
                        />
                      )}
                    </Box>
                  </Collapse>
                )}
              </React.Fragment>
            ))}
          </List>
        )}
      </Box>
      
      {/* Additional Details */}
      {data.details && Object.keys(data.details).length > 0 && (
        <>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: expandedDetails ? 2 : 0,
                cursor: 'pointer'
              }}
              onClick={() => setExpandedDetails(!expandedDetails)}
            >
              <Typography variant="subtitle1" fontWeight="bold">
                Additional Details
              </Typography>
              <IconButton size="small">
                {expandedDetails ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Box>
            
            <Collapse in={expandedDetails}>
              <Box sx={{ 
                backgroundColor: theme.palette.mode === 'dark' 
                  ? 'rgba(255, 255, 255, 0.05)' 
                  : 'rgba(0, 0, 0, 0.03)',
                borderRadius: 1,
                p: 2
              }}>
                {Object.entries(data.details).map(([key, value], index) => (
                  <Box key={index} sx={{ mb: index < Object.keys(data.details).length - 1 ? 1 : 0 }}>
                    <Typography variant="body2" fontWeight="bold" component="span">
                      {key}:
                    </Typography>
                    <Typography variant="body2" component="span" sx={{ ml: 1 }}>
                      {typeof value === 'object' ? JSON.stringify(value) : value.toString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Collapse>
          </Box>
        </>
      )}
      
      {/* Action Buttons */}
      <Box 
        sx={{ 
          p: 2, 
          backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: 1
        }}
      >
        <Tooltip title="Copy solution to clipboard">
          <Button 
            startIcon={<ContentCopy />}
            size="small"
            onClick={onCopySolution}
            variant="outlined"
          >
            Copy
          </Button>
        </Tooltip>
        
        <Tooltip title="Share solution">
          <Button
            startIcon={<Share />}
            size="small"
            onClick={onShareSolution}
            variant="outlined"
          >
            Share
          </Button>
        </Tooltip>
        
        <Tooltip title="Send solution to device">
          <Button
            startIcon={<Send />}
            size="small"
            variant="contained"
            onClick={onSendSolution}
            color="primary"
          >
            Send Solution
          </Button>
        </Tooltip>
      </Box>
    </Paper>
  );
};

export default EnhancedDiagnosisPanel;
