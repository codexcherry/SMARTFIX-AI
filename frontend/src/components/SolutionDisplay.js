import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Stepper, 
  Step, 
  StepLabel, 
  StepContent,
  Button,
  Chip,
  Divider,
  Link,
  Card,
  CardContent,
  CardActions,
  Collapse,
  IconButton,
  Alert,
  TextField,
  Paper,
  Avatar,
  Tooltip,
  LinearProgress,
  Grid,
  Stack
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import SmsIcon from '@mui/icons-material/Sms';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ShareIcon from '@mui/icons-material/Share';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { motion } from 'framer-motion';

const SolutionDisplay = ({ solution, queryId }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [expandedSources, setExpandedSources] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [notificationSent, setNotificationSent] = useState(false);
  const [notificationLoading, setNotificationLoading] = useState(false);
  const [notificationError, setNotificationError] = useState('');
  const [bookmarked, setBookmarked] = useState(false);


  if (!solution) {
    return null;
  }

  const { issue, possible_causes = [], recommended_steps = [], external_sources = [] } = solution;

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
  };

  const handleExpandSources = () => {
    setExpandedSources(!expandedSources);
  };

  const handleSendSMS = async () => {
    if (!phoneNumber) {
      setNotificationError('Please enter a phone number');
      return;
    }

    setNotificationLoading(true);
    setNotificationError('');

    try {
      const message = `SmartFix-AI Solution: ${issue}\n\nTop recommendation: ${recommended_steps[0]?.description || 'No specific steps available'}`;
      
      const response = await fetch('http://localhost:8000/api/v1/query/notify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'test_user',
          notification_type: 'sms',
          message,
          to_contact: phoneNumber
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to send notification');
      }
      
      setNotificationSent(true);
      setNotificationLoading(false);
    } catch (err) {
      setNotificationError('Failed to send notification. Please try again.');
      setNotificationLoading(false);
    }
  };




  return (
    <Paper 
      elevation={0} 
      sx={{ 
        borderRadius: 4,
        overflow: 'hidden',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid rgba(255,255,255,0.1)',
        background: 'linear-gradient(135deg, rgba(33,150,243,0.05) 0%, rgba(33,203,243,0.05) 100%)',
      }}
    >
      <Box 
        sx={{ 
          p: 3, 
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          background: 'linear-gradient(135deg, rgba(33,150,243,0.1) 0%, rgba(33,203,243,0.1) 100%)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <Typography variant="h5" sx={{ fontWeight: 500 }}>
          Diagnosis
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title={bookmarked ? "Remove bookmark" : "Bookmark solution"}>
            <IconButton onClick={() => setBookmarked(!bookmarked)} color={bookmarked ? "primary" : "default"}>
              {bookmarked ? <BookmarkIcon /> : <BookmarkBorderIcon />}
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Share solution">
            <IconButton>
              <ShareIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Box sx={{ p: 3, flexGrow: 1, overflow: 'auto' }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
              {issue}
            </Typography>
            

            
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 500, mt: 3 }}>
              Possible Causes:
            </Typography>
            <Box sx={{ mb: 3 }}>
              {possible_causes.map((cause, index) => (
                <Chip 
                  key={index}
                  label={cause}
                  variant="outlined"
                  sx={{ 
                    mr: 1, 
                    mb: 1,
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
          
          <Divider sx={{ my: 3 }} />
          
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
              Recommended Steps:
            </Typography>
            
            <Stepper activeStep={activeStep} orientation="vertical" sx={{ 
              mb: 3,
              '& .MuiStepLabel-root': {
                padding: 1
              },
              '& .MuiStepContent-root': {
                borderLeft: '1px solid rgba(255,255,255,0.1)',
                marginLeft: 1,
                paddingLeft: 2
              }
            }}>
              {recommended_steps.map((step, index) => (
                <Step key={index}>
                  <StepLabel>
                    <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                      Step {step.step_number}
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Typography sx={{ mb: 2 }}>{step.description}</Typography>
                    {step.image_url && (
                      <Box sx={{ mt: 2, mb: 2 }}>
                        <img 
                          src={step.image_url} 
                          alt={`Step ${step.step_number}`} 
                          style={{ maxWidth: '100%', borderRadius: 8 }} 
                        />
                      </Box>
                    )}
                    <Box sx={{ mb: 2, mt: 2 }}>
                      <Stack direction="row" spacing={1}>
                        <Button
                          variant="contained"
                          onClick={handleNext}
                          sx={{
                            background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                          }}
                        >
                          {index === recommended_steps.length - 1 ? 'Finish' : 'Continue'}
                        </Button>
                        <Button
                          disabled={index === 0}
                          onClick={handleBack}
                          variant="outlined"
                        >
                          Back
                        </Button>
                      </Stack>
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
            
            {activeStep === recommended_steps.length && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Paper 
                  elevation={0} 
                  sx={{ 
                    p: 3, 
                    backgroundColor: 'rgba(76, 175, 80, 0.1)', 
                    borderRadius: 3,
                    border: '1px solid rgba(76, 175, 80, 0.3)'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CheckCircleOutlineIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6" sx={{ fontWeight: 500 }}>
                      All steps completed!
                    </Typography>
                  </Box>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    You've successfully completed all the troubleshooting steps. Is your issue resolved?
                  </Typography>
                  <Stack direction="row" spacing={1}>
                    <Button onClick={handleReset} variant="outlined">
                      Review Steps Again
                    </Button>
                    <Button 
                      variant="contained" 
                      color="success"
                      sx={{ color: 'white' }}
                    >
                      Issue Resolved
                    </Button>
                  </Stack>
                </Paper>
              </motion.div>
            )}
          </Box>
          
          {external_sources && external_sources.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Box 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  cursor: 'pointer',
                  p: 2,
                  borderRadius: 2,
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  '&:hover': { 
                    backgroundColor: 'rgba(255,255,255,0.08)'
                  },
                }}
                onClick={handleExpandSources}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                  External Resources ({external_sources.length})
                </Typography>
                <IconButton
                  sx={{
                    transform: expandedSources ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: '0.3s'
                  }}
                >
                  <ExpandMoreIcon />
                </IconButton>
              </Box>
              
              <Collapse in={expandedSources} timeout={500}>
                <Box sx={{ mt: 2 }}>
                  <Grid container spacing={2}>
                    {external_sources.map((source, index) => (
                      <Grid item xs={12} key={index}>
                        <Card 
                          variant="outlined" 
                          sx={{ 
                            mb: 2,
                            transition: 'all 0.3s ease',
                            '&:hover': {
                              transform: 'translateY(-2px)',
                              boxShadow: '0 8px 16px rgba(0,0,0,0.2)'
                            }
                          }}
                        >
                          <CardContent>
                            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 500 }}>
                              {source.title}
                            </Typography>
                            {source.snippet && (
                              <Typography variant="body2" color="text.secondary">
                                {source.snippet}
                              </Typography>
                            )}
                          </CardContent>
                          <CardActions>
                            <Button 
                              size="small" 
                              component={Link} 
                              href={source.url} 
                              target="_blank"
                              rel="noopener"
                              endIcon={<ExpandMoreIcon sx={{ transform: 'rotate(-90deg)' }} />}
                              sx={{ 
                                textTransform: 'none',
                                fontWeight: 500
                              }}
                            >
                              Visit Source
                            </Button>
                          </CardActions>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Collapse>
            </Box>
          )}
          
          <Divider sx={{ my: 4 }} />
          
          <Box>
            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 500 }}>
              Send this solution to your phone:
            </Typography>
            
            {notificationSent ? (
              <Alert 
                icon={<CheckCircleIcon fontSize="inherit" />} 
                severity="success"
                sx={{ mb: 2, borderRadius: 2 }}
              >
                Solution sent successfully!
              </Alert>
            ) : (
              <Box sx={{ display: 'flex', alignItems: 'flex-start', flexWrap: 'wrap' }}>
                <TextField
                  label="Phone Number"
                  variant="outlined"
                  placeholder="+1234567890"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  size="small"
                  sx={{ mr: 2, mb: 2, flexGrow: 1, maxWidth: 200 }}
                  error={!!notificationError}
                  helperText={notificationError}
                />
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<SmsIcon />}
                    onClick={handleSendSMS}
                    disabled={notificationLoading || !phoneNumber}
                    sx={{
                      background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    }}
                  >
                    {notificationLoading ? 'Sending...' : 'SMS'}
                  </Button>
                  
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<WhatsAppIcon />}
                    disabled={true} // Enable when WhatsApp is configured
                  >
                    WhatsApp
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        </motion.div>
      </Box>
    </Paper>
  );
};

export default SolutionDisplay;