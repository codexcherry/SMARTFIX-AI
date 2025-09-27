import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  Divider,
  Button,
  Tooltip
} from '@mui/material';
import {
  Accessibility as AccessibilityIcon,
  Close as CloseIcon,
  Mic as MicIcon,
  Keyboard as KeyboardIcon,
  TouchApp as TouchIcon,
  Visibility as VisibilityIcon,
  ZoomIn as ZoomInIcon,
  Contrast as ContrastIcon,
  HighlightAlt as HighlightAltIcon,
  VolumeUp as VolumeUpIcon
} from '@mui/icons-material';

const AccessibilityMenu = ({ onStartGestureControl }) => {
  const [open, setOpen] = useState(false);
  const [settings, setSettings] = useState({
    highContrast: false,
    largeText: false,
    screenReader: false,
    voiceControl: false,
    gestureControl: false,
    keyboardNavigation: true,
    focusHighlight: false
  });

  const toggleDrawer = () => {
    setOpen(!open);
  };

  const handleSettingChange = (setting) => {
    const newSettings = { ...settings };
    newSettings[setting] = !newSettings[setting];
    setSettings(newSettings);
    
    // Special handling for gesture control
    if (setting === 'gestureControl' && newSettings.gestureControl && onStartGestureControl) {
      onStartGestureControl();
    }
  };

  return (
    <>
      <Tooltip title="Accessibility Options">
        <IconButton 
          onClick={toggleDrawer}
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            color: 'white',
            '&:hover': {
              backgroundColor: 'rgba(59, 130, 246, 0.3)',
            },
            zIndex: 1300
          }}
        >
          <AccessibilityIcon />
        </IconButton>
      </Tooltip>

      <Drawer
        anchor="right"
        open={open}
        onClose={toggleDrawer}
        sx={{
          '& .MuiDrawer-paper': {
            width: 320,
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: 'white',
            padding: 2
          }
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography 
            variant="h6" 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              fontFamily: '"Orbitron", sans-serif',
              color: 'white'
            }}
          >
            <AccessibilityIcon sx={{ mr: 1 }} />
            Accessibility Options
          </Typography>
          <IconButton onClick={toggleDrawer} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />

        <List>
          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <ContrastIcon />
            </ListItemIcon>
            <ListItemText 
              primary="High Contrast" 
              secondary="Increase color contrast for better visibility"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.highContrast} 
              onChange={() => handleSettingChange('highContrast')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <ZoomInIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Large Text" 
              secondary="Increase text size for better readability"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.largeText} 
              onChange={() => handleSettingChange('largeText')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <VolumeUpIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Screen Reader" 
              secondary="Read screen content aloud"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.screenReader} 
              onChange={() => handleSettingChange('screenReader')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <MicIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Voice Control" 
              secondary="Control the app with voice commands"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.voiceControl} 
              onChange={() => handleSettingChange('voiceControl')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <TouchIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Gesture Control" 
              secondary="Control using hand gestures and eye tracking"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.gestureControl} 
              onChange={() => handleSettingChange('gestureControl')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <KeyboardIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Keyboard Navigation" 
              secondary="Navigate with keyboard shortcuts"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.keyboardNavigation} 
              onChange={() => handleSettingChange('keyboardNavigation')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>

          <ListItem>
            <ListItemIcon sx={{ color: 'white' }}>
              <HighlightAltIcon />
            </ListItemIcon>
            <ListItemText 
              primary="Focus Highlighting" 
              secondary="Highlight the focused element"
              secondaryTypographyProps={{ color: 'rgba(255, 255, 255, 0.7)' }}
            />
            <Switch 
              checked={settings.focusHighlight} 
              onChange={() => handleSettingChange('focusHighlight')}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#90caf9'
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: 'rgba(59, 130, 246, 0.5)'
                }
              }}
            />
          </ListItem>
        </List>

        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', my: 2 }} />

        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
          If your keyboard or mouse isn't working:
        </Typography>

        <Button
          variant="contained"
          fullWidth
          onClick={() => {
            if (onStartGestureControl) onStartGestureControl();
            setSettings({...settings, gestureControl: true});
          }}
          sx={{
            mb: 1,
            background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
            boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
          }}
        >
          Start Hands-Free Control
        </Button>

        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', display: 'block', textAlign: 'center' }}>
          Use hand gestures and eye blinks to control the app
        </Typography>
      </Drawer>
    </>
  );
};

export default AccessibilityMenu;
