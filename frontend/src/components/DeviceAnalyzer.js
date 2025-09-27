import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  ThemeProvider,
  createTheme
} from '@mui/material';
import {
  Computer,
  Memory,
  Storage,
  Speed,
  Warning,
  CheckCircle,
  Error as ErrorIcon,
  Refresh,
  Assessment,
  TrendingUp,
  TrendingDown,
  ExpandMore,
  Security,
  NetworkCheck,
  BugReport,
  Timeline,
  Analytics,
  SystemUpdate,
  BatteryAlert,
  Thermostat,
  Dashboard,
  ExpandCircleDown,
  History,
  Report,
  Settings,
  Code
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Create a proper theme with all required color properties
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      dark: '#115293',
      light: '#42a5f5',
    },
    secondary: {
      main: '#dc004e',
      dark: '#9a0036',
      light: '#e33371',
    },
    error: {
      main: '#f44336',
      dark: '#d32f2f',
      light: '#e57373',
    },
    warning: {
      main: '#ff9800',
      dark: '#f57c00',
      light: '#ffb74d',
    },
    info: {
      main: '#2196f3',
      dark: '#1976d2',
      light: '#64b5f6',
    },
    success: {
      main: '#4caf50',
      dark: '#388e3c',
      light: '#81c784',
    },
  },
});

const DeviceAnalyzer = () => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingHealth, setIsLoadingHealth] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [scanHistory, setScanHistory] = useState([]);
  const [scanDialogOpen, setScanDialogOpen] = useState(false);
  const [scanType, setScanType] = useState('quick');
  const [scanProgress, setScanProgress] = useState(0);
  const [scanStep, setScanStep] = useState(0);
  const [detailedMetrics, setDetailedMetrics] = useState(null);

  // Auto-refresh health status every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (!isAnalyzing) {
        fetchHealthStatus();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isAnalyzing]);

  // Load scan history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('deviceScanHistory');
    if (savedHistory) {
      try {
        setScanHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Error parsing scan history:', e);
        setScanHistory([]);
      }
    }
  }, []);

  const fetchHealthStatus = async () => {
    setIsLoadingHealth(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/query/device/health');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setHealthStatus(data);
      } else {
        setError(data.error || 'Failed to fetch health status');
      }
    } catch (err) {
      console.error('Error fetching health status:', err);
      setError('Failed to fetch health status. Please check if the server is running.');
    } finally {
      setIsLoadingHealth(false);
    }
  };

  const fetchDetailedMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/query/device/detailed-metrics');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setDetailedMetrics(data);
      }
    } catch (err) {
      console.error('Error fetching detailed metrics:', err);
      setError('Failed to fetch detailed metrics. Please check if the server is running.');
    }
  };

  const performQuickScan = async () => {
    setIsAnalyzing(true);
    setError(null);
    setScanType('quick');
    setScanDialogOpen(true);
    setScanProgress(0);
    setScanStep(0);
    
    try {
      // Simulate quick scan with progress
      const steps = ['Initializing', 'Checking system status', 'Completing scan'];
      
      for (let i = 0; i < steps.length; i++) {
        setScanStep(i + 1);
        setScanProgress(((i + 1) / steps.length) * 100);
        await new Promise(resolve => setTimeout(resolve, 800));
      }

      // Call the real backend API
      const response = await fetch('http://localhost:8000/api/v1/query/device/analyze/quick', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scan_type: 'quick',
          user_id: 'device_analyzer_user'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setAnalysisResult(result);
        addToScanHistory(result, 'Quick Scan');
      } else {
        throw new Error(result.error || 'Failed to perform quick scan');
      }
      
      setTimeout(() => {
        setScanDialogOpen(false);
        setIsAnalyzing(false);
      }, 1000);
      
    } catch (err) {
      setError('Failed to perform quick scan. Please try again.');
      console.error('Error performing quick scan:', err);
      setScanDialogOpen(false);
      setIsAnalyzing(false);
    }
  };

  const performAdvancedScan = async () => {
    setScanType('advanced');
    setScanDialogOpen(true);
    setScanProgress(0);
    setScanStep(0);
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const steps = [
        'Collecting system information',
        'Analyzing performance metrics',
        'Running security checks',
        'Diagnosing hardware',
        'Analyzing failure patterns',
        'Compiling results'
      ];
      
      for (let i = 0; i < steps.length; i++) {
        setScanStep(i + 1);
        setScanProgress(((i + 1) / steps.length) * 100);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      // Call the real backend API for advanced scan
      const response = await fetch('http://localhost:8000/api/v1/query/device/analyze/deep', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scan_type: 'advanced',
          user_id: 'device_analyzer_user',
          include_security: true,
          include_hardware: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setAnalysisResult(result);
        addToScanHistory(result, 'Advanced Scan');
      } else {
        throw new Error(result.error || 'Failed to perform advanced scan');
      }
      
      setTimeout(() => {
        setScanDialogOpen(false);
        setIsAnalyzing(false);
      }, 1000);
      
    } catch (err) {
      setError('Failed to perform advanced scan. Please try again.');
      console.error('Error performing advanced scan:', err);
      setScanDialogOpen(false);
      setIsAnalyzing(false);
    }
  };

  const performDeepScan = async () => {
    setScanType('deep');
    setScanDialogOpen(true);
    setScanProgress(0);
    setScanStep(0);
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const steps = [
        'Initializing deep scan',
        'Checking system integrity',
        'Analyzing performance history',
        'Scanning for hardware faults',
        'Checking network stability',
        'Analyzing system logs',
        'Running diagnostic tests',
        'Compiling results'
      ];
      
      for (let i = 0; i < steps.length; i++) {
        setScanStep(i + 1);
        setScanProgress(((i + 1) / steps.length) * 100);
        await new Promise(resolve => setTimeout(resolve, 1500));
      }
      
      // Call the real backend API for deep scan
      const response = await fetch('http://localhost:8000/api/v1/query/device/analyze/deep', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scan_type: 'deep',
          user_id: 'device_analyzer_user',
          include_security: true,
          include_hardware: true,
          include_failure_analysis: true,
          include_performance_history: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setAnalysisResult(result);
        addToScanHistory(result, 'Deep Scan');
      } else {
        throw new Error(result.error || 'Failed to perform deep scan');
      }
      
      setTimeout(() => {
        setScanDialogOpen(false);
        setIsAnalyzing(false);
      }, 1000);
      
    } catch (err) {
      setError('Failed to perform deep scan. Please try again.');
      console.error('Error performing deep scan:', err);
      setScanDialogOpen(false);
      setIsAnalyzing(false);
    }
  };

  const addToScanHistory = (result, scanType) => {
    const newHistory = [
      {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: scanType,
        status: result.overall_status || 'unknown',
        issues: (result.detected_issues ? result.detected_issues.length : 0) + 
               (result.security_issues ? result.security_issues.length : 0)
      },
      ...scanHistory.slice(0, 9)
    ];
    
    setScanHistory(newHistory);
    localStorage.setItem('deviceScanHistory', JSON.stringify(newHistory));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle color="success" />;
      case 'warning': return <Warning color="warning" />;
      case 'critical': return <ErrorIcon color="error" />;
      default: return <Computer />;
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes || bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatGB = (bytes) => {
    if (!bytes || bytes === 0) return '0 GB';
    return (bytes / (1024 ** 3)).toFixed(2) + ' GB';
  };

  const renderScanDialog = () => {
    const scanSteps = {
      quick: ['Initializing', 'Checking system status', 'Completing scan'],
      advanced: [
        'Collecting system information',
        'Analyzing performance metrics',
        'Running security checks',
        'Diagnosing hardware',
        'Analyzing failure patterns',
        'Compiling results'
      ],
      deep: [
        'Initializing deep scan',
        'Checking system integrity',
        'Analyzing performance history',
        'Scanning for hardware faults',
        'Checking network stability',
        'Analyzing system logs',
        'Running diagnostic tests',
        'Compiling results'
      ]
    };

    const currentSteps = scanSteps[scanType] || scanSteps.quick;

    return (
      <Dialog open={scanDialogOpen} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <Assessment sx={{ mr: 1 }} />
            {scanType === 'quick' ? 'Quick Scan' : scanType === 'advanced' ? 'Advanced System Analysis' : 'Deep Diagnostic Scan'}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Stepper activeStep={scanStep} orientation="vertical">
              {currentSteps.map((label, index) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
            
            <Box sx={{ mt: 3 }}>
              <LinearProgress 
                variant="determinate" 
                value={scanProgress} 
                sx={{ height: 10, borderRadius: 5 }}
              />
              <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                {Math.round(scanProgress)}% Complete
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setScanDialogOpen(false);
              setIsAnalyzing(false);
            }}
            disabled={scanProgress >= 100}
          >
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  const renderFailureAnalysis = () => {
    if (!analysisResult?.failure_analysis) return null;

    return (
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom color="error">
              <BugReport sx={{ mr: 1, verticalAlign: 'middle' }} />
              Failure Analysis
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Recent System Errors
                </Typography>
                <List dense>
                  {analysisResult.failure_analysis.recent_errors && analysisResult.failure_analysis.recent_errors.map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <ErrorIcon color="error" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={error.message} 
                        secondary={`Time: ${new Date(error.timestamp).toLocaleString()}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Performance Degradation
                </Typography>
                {analysisResult.failure_analysis.performance_degradation && (
                  <Box>
                    <Typography variant="body2">
                      CPU Performance: {analysisResult.failure_analysis.performance_degradation.cpu}% compared to baseline
                    </Typography>
                    <Typography variant="body2">
                      Memory Performance: {analysisResult.failure_analysis.performance_degradation.memory}% compared to baseline
                    </Typography>
                    <Typography variant="body2">
                      Disk Performance: {analysisResult.failure_analysis.performance_degradation.disk}% compared to baseline
                    </Typography>
                  </Box>
                )}
                
                <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                  Resource Exhaustion Patterns
                </Typography>
                {analysisResult.failure_analysis.resource_exhaustion && (
                  <Box>
                    <Typography variant="body2">
                      Memory Exhaustion: {analysisResult.failure_analysis.resource_exhaustion.memory} times in last 24h
                    </Typography>
                    <Typography variant="body2">
                      CPU Saturation: {analysisResult.failure_analysis.resource_exhaustion.cpu} times in last 24h
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
            
            <Accordion sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>Root Cause Analysis</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {analysisResult.failure_analysis.root_cause && (
                  <Box>
                    <Typography variant="body2" paragraph>
                      {analysisResult.failure_analysis.root_cause.description}
                    </Typography>
                    <Typography variant="subtitle2">
                      Probability: {analysisResult.failure_analysis.root_cause.probability}%
                    </Typography>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          </CardContent>
        </Card>
      </Grid>
    );
  };

  const renderHardwareDiagnostics = () => {
    if (!analysisResult?.hardware_status) return null;

    return (
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <Memory sx={{ mr: 1, verticalAlign: 'middle' }} />
              Hardware Diagnostics
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Storage Health
                </Typography>
                {analysisResult.hardware_status.storage && analysisResult.hardware_status.storage.map((disk, index) => (
                  <Box key={index} sx={{ mb: 2, p: 1, border: '1px solid #eee', borderRadius: 1 }}>
                    <Typography variant="body2" fontWeight="bold">
                      {disk.device} ({disk.type})
                    </Typography>
                    <Typography variant="body2">
                      Health: {disk.health_status} ({disk.temperature}°C)
                    </Typography>
                    <Typography variant="body2">
                      Power On Hours: {disk.power_on_hours}
                    </Typography>
                    <LinearProgress 
                      variant="determinate" 
                      value={disk.life_remaining} 
                      color={disk.life_remaining > 80 ? 'success' : disk.life_remaining > 50 ? 'warning' : 'error'}
                      sx={{ height: 8, borderRadius: 4, mt: 1 }}
                    />
                    <Typography variant="caption" display="block">
                      Life Remaining: {disk.life_remaining}%
                    </Typography>
                  </Box>
                ))}
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Battery Status
                </Typography>
                {analysisResult.hardware_status.battery && (
                  <Box sx={{ p: 1, border: '1px solid #eee', borderRadius: 1 }}>
                    <Typography variant="body2">
                      Health: {analysisResult.hardware_status.battery.health}%
                    </Typography>
                    <Typography variant="body2">
                      Cycle Count: {analysisResult.hardware_status.battery.cycle_count}
                    </Typography>
                    <Typography variant="body2">
                      Current Capacity: {analysisResult.hardware_status.battery.capacity}%
                    </Typography>
                  </Box>
                )}
                
                <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
                  Thermal Status
                </Typography>
                {analysisResult.hardware_status.thermal && (
                  <Box sx={{ p: 1, border: '1px solid #eee', borderRadius: 1 }}>
                    <Typography variant="body2">
                      CPU Temperature: {analysisResult.hardware_status.thermal.cpu}°C
                    </Typography>
                    <Typography variant="body2">
                      GPU Temperature: {analysisResult.hardware_status.thermal.gpu}°C
                    </Typography>
                    <Typography variant="body2">
                      System Temperature: {analysisResult.hardware_status.thermal.system}°C
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    );
  };

  const renderSecurityIssues = () => {
    if (!analysisResult?.security_issues || analysisResult.security_issues.length === 0) return null;

    return (
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom color="warning.main">
              <Security sx={{ mr: 1, verticalAlign: 'middle' }} />
              Security Issues ({analysisResult.security_issues.length})
            </Typography>
            
            <List>
              {analysisResult.security_issues.map((issue, index) => (
                <ListItem key={index} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, mb: 1 }}>
                  <ListItemIcon>
                    {issue.severity === 'high' ? <ErrorIcon color="error" /> : <Warning color="warning" />}
                  </ListItemIcon>
                  <ListItemText
                    primary={issue.title}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {issue.description}
                        </Typography>
                        <Typography variant="body2" color="error.main" sx={{ mt: 1 }}>
                          Impact: {issue.impact}
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <Chip 
                            label={issue.severity.toUpperCase()} 
                            color={issue.severity === 'high' ? 'error' : 'warning'}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Chip 
                            label={issue.category} 
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 3 }}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
            Advanced Device Health Analyzer
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Comprehensive system diagnostics with advanced failure analysis and security scanning
          </Typography>
        </motion.div>

        {/* Quick Health Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Real-time Health Status
                  </Typography>
                  {healthStatus ? (
                    <Box>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        {getStatusIcon(healthStatus.status)}
                        <Typography variant="body1">
                          Status: {healthStatus.status?.toUpperCase() || 'UNKNOWN'}
                        </Typography>
                      </Box>
                      <Grid container spacing={2}>
                        <Grid item xs={4}>
                          <Typography variant="body2">CPU: {healthStatus.metrics?.cpu_usage?.toFixed(1) || 0}%</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2">Memory: {healthStatus.metrics?.memory_usage?.toFixed(1) || 0}%</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2">Disk: {healthStatus.metrics?.disk_usage?.toFixed(1) || 0}%</Typography>
                        </Grid>
                      </Grid>
                    </Box>
                  ) : (
                    <Typography variant="body2">Loading health status...</Typography>
                  )}
                </Box>
                <Box>
                  <Button
                    variant="contained"
                    startIcon={<Refresh />}
                    onClick={fetchHealthStatus}
                    disabled={isLoadingHealth}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }, mr: 1 }}
                  >
                    {isLoadingHealth ? <CircularProgress size={20} /> : 'Refresh'}
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Analytics />}
                    onClick={fetchDetailedMetrics}
                    sx={{ bgcolor: 'rgba(255,255,255,0.2)', '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' } }}
                  >
                    Detailed Metrics
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </motion.div>

        {/* Scan History */}
        {scanHistory.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <History sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Recent Scans
                </Typography>
                <Grid container spacing={1}>
                  {scanHistory.slice(0, 5).map((scan) => (
                    <Grid item xs={12} sm={6} md={2.4} key={scan.id}>
                      <Paper 
                        elevation={1} 
                        sx={{ 
                          p: 1, 
                          textAlign: 'center',
                          borderLeft: `4px solid ${
                            scan.status === 'healthy' ? '#4caf50' : 
                            scan.status === 'warning' ? '#ff9800' : '#f44336'
                          }`
                        }}
                      >
                        <Typography variant="body2" noWrap>
                          {scan.type}
                        </Typography>
                        <Typography variant="caption" display="block">
                          {new Date(scan.timestamp).toLocaleTimeString()}
                        </Typography>
                        <Chip 
                          label={scan.status} 
                          size="small"
                          color={getStatusColor(scan.status)}
                          sx={{ mt: 0.5 }}
                        />
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                          {scan.issues} issues
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Analysis Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                Diagnostic Scans
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                <Button
                  variant="contained"
                  startIcon={<Speed />}
                  onClick={performQuickScan}
                  disabled={isAnalyzing}
                  sx={{ 
                    background: 'linear-gradient(45deg, #4caf50 30%, #8bc34a 90%)',
                    '&:hover': { background: 'linear-gradient(45deg, #4caf50 40%, #8bc34a 100%)' }
                  }}
                >
                  Quick Scan
                </Button>
                
                <Button
                  variant="contained"
                  startIcon={<Analytics />}
                  onClick={performAdvancedScan}
                  disabled={isAnalyzing}
                  sx={{ 
                    background: 'linear-gradient(45deg, #2196f3 30%, #21cbf3 90%)',
                    '&:hover': { background: 'linear-gradient(45deg, #2196f3 40%, #21cbf3 100%)' }
                  }}
                >
                  Advanced Analysis
                </Button>
                
                <Button
                  variant="contained"
                  startIcon={<BugReport />}
                  onClick={performDeepScan}
                  disabled={isAnalyzing}
                  sx={{ 
                    background: 'linear-gradient(45deg, #ff9800 30%, #ff5722 90%)',
                    '&:hover': { background: 'linear-gradient(45deg, #ff9800 40%, #ff5722 100%)' }
                  }}
                >
                  Deep Diagnostic
                </Button>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Select a scan type based on your needs. Quick scans take seconds, while deep diagnostics provide comprehensive analysis.
              </Typography>
            </CardContent>
          </Card>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          </motion.div>
        )}

        {/* Scan Progress Dialog */}
        {renderScanDialog()}

        {/* Analysis Results */}
        {analysisResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
              <Tab label="Overview" icon={<Dashboard />} iconPosition="start" />
              <Tab label="Performance" icon={<TrendingUp />} iconPosition="start" />
              <Tab label="Hardware" icon={<Memory />} iconPosition="start" />
              <Tab label="Security" icon={<Security />} iconPosition="start" />
              <Tab label="Failures" icon={<BugReport />} iconPosition="start" />
            </Tabs>
            
            {activeTab === 0 && (
              <Grid container spacing={3}>
                {/* Overall Status */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={2} mb={2}>
                        {getStatusIcon(analysisResult.overall_status || 'healthy')}
                        <Typography variant="h5">
                          Overall System Status: {(analysisResult.overall_status || 'healthy').toUpperCase()}
                        </Typography>
                        <Chip 
                          label={`Scan Type: ${analysisResult.scan_type || 'Standard'}`}
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                      
                      <Grid container spacing={2}>
                        <Grid item xs={3}>
                          <Typography variant="body2" color="text.secondary">Total Issues</Typography>
                          <Typography variant="h6">
                            {(analysisResult.detected_issues ? analysisResult.detected_issues.length : 0) + 
                             (analysisResult.security_issues ? analysisResult.security_issues.length : 0)}
                          </Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="body2" color="text.secondary">Critical Issues</Typography>
                          <Typography variant="h6" color="error.main">
                            {analysisResult.detected_issues ? 
                              analysisResult.detected_issues.filter(issue => issue.severity === 'high' || issue.severity === 'critical').length : 0}
                          </Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="body2" color="text.secondary">Performance Score</Typography>
                          <Typography variant="h6" color={
                            analysisResult.performance_metrics?.score > 80 ? 'success.main' : 
                            analysisResult.performance_metrics?.score > 60 ? 'warning.main' : 'error.main'
                          }>
                            {analysisResult.performance_metrics?.score || 'N/A'}%
                          </Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="body2" color="text.secondary">Analysis Time</Typography>
                          <Typography variant="h6">
                            {new Date(analysisResult.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>

                {/* System Information */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <Computer sx={{ mr: 1, verticalAlign: 'middle' }} />
                        System Information
                      </Typography>
                      <List dense>
                        <ListItem>
                          <ListItemIcon><Computer /></ListItemIcon>
                          <ListItemText 
                            primary="Platform" 
                            secondary={analysisResult.system_info?.platform || 'Unknown'} 
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><Memory /></ListItemIcon>
                          <ListItemText 
                            primary="Processor" 
                            secondary={analysisResult.system_info?.processor || 'Unknown'} 
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon><Storage /></ListItemIcon>
                          <ListItemText 
                            primary="Memory" 
                            secondary={formatGB(analysisResult.system_info?.memory_total)} 
                          />
                        </ListItem>
                      </List>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Detected Issues */}
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <Warning sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Detected Issues ({analysisResult.detected_issues?.length || 0})
                      </Typography>
                      {analysisResult.detected_issues && analysisResult.detected_issues.length > 0 ? (
                        <List dense>
                          {analysisResult.detected_issues.slice(0, 3).map((issue, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                {issue.severity === 'critical' || issue.severity === 'high' ? 
                                  <ErrorIcon color="error" /> : <Warning color="warning" />}
                              </ListItemIcon>
                              <ListItemText 
                                primary={issue.description}
                                secondary={issue.details}
                              />
                            </ListItem>
                          ))}
                        </List>
                      ) : (
                        <Typography variant="body2" color="success.main">
                          No critical issues detected
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {/* Recommendations */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <SystemUpdate sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Recommendations
                      </Typography>
                      {analysisResult.recommendations && analysisResult.recommendations.length > 0 ? (
                        <List>
                          {analysisResult.recommendations.map((recommendation, index) => (
                            <ListItem key={index}>
                              <ListItemIcon>
                                <CheckCircle color="primary" />
                              </ListItemIcon>
                              <ListItemText primary={recommendation} />
                            </ListItem>
                          ))}
                        </List>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No specific recommendations at this time
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {activeTab === 1 && (
              <Grid container spacing={3}>
                {/* Performance Metrics */}
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Performance Analysis
                      </Typography>
                      
                      <Grid container spacing={3}>
                        <Grid item xs={12} md={4}>
                          <Box textAlign="center">
                            <Typography variant="h3" color={
                              analysisResult.performance_metrics?.cpu?.usage_percent > 90 ? 'error.main' :
                              analysisResult.performance_metrics?.cpu?.usage_percent > 70 ? 'warning.main' : 'success.main'
                            }>
                              {analysisResult.performance_metrics?.cpu?.usage_percent || 0}%
                            </Typography>
                            <Typography variant="h6">CPU Usage</Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={analysisResult.performance_metrics?.cpu?.usage_percent || 0}
                              color={
                                analysisResult.performance_metrics?.cpu?.usage_percent > 90 ? 'error' :
                                analysisResult.performance_metrics?.cpu?.usage_percent > 70 ? 'warning' : 'success'
                              }
                              sx={{ mt: 1, height: 8, borderRadius: 4 }}
                            />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Temperature: {analysisResult.performance_metrics?.cpu?.temperature || 'N/A'}°C
                            </Typography>
                          </Box>
                        </Grid>

                        <Grid item xs={12} md={4}>
                          <Box textAlign="center">
                            <Typography variant="h3" color={
                              analysisResult.performance_metrics?.memory?.usage_percent > 90 ? 'error.main' :
                              analysisResult.performance_metrics?.memory?.usage_percent > 70 ? 'warning.main' : 'success.main'
                            }>
                              {analysisResult.performance_metrics?.memory?.usage_percent || 0}%
                            </Typography>
                            <Typography variant="h6">Memory Usage</Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={analysisResult.performance_metrics?.memory?.usage_percent || 0}
                              color={
                                analysisResult.performance_metrics?.memory?.usage_percent > 90 ? 'error' :
                                analysisResult.performance_metrics?.memory?.usage_percent > 70 ? 'warning' : 'success'
                              }
                              sx={{ mt: 1, height: 8, borderRadius: 4 }}
                            />
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                              Available: {formatBytes(analysisResult.performance_metrics?.memory?.available)}
                            </Typography>
                          </Box>
                        </Grid>

                        <Grid item xs={12} md={4}>
                          <Box textAlign="center">
                            <Typography variant="h3" color={
                              analysisResult.performance_metrics?.disk?.usage_percent > 90 ? 'error.main' :
                              analysisResult.performance_metrics?.disk?.usage_percent > 70 ? 'warning.main' : 'success.main'
                            }>
                              {analysisResult.performance_metrics?.disk?.usage_percent || 0}%
                            </Typography>
                            <Typography variant="h6">Disk Usage</Typography>
                            <LinearProgress 
                              variant="determinate" 
                              value={analysisResult.performance_metrics?.disk?.usage_percent || 0}
                              color={
                                analysisResult.performance_metrics?.disk?.usage_percent > 90 ? 'error' :
                                analysisResult.performance_metrics?.disk?.usage_percent > 70 ? 'warning' : 'success'
                              }
                              sx={{ mt: 1, height: 8, borderRadius: 4 }}
                            />
                          </Box>
                        </Grid>
                      </Grid>

                      <Divider sx={{ my: 3 }} />

                      <Typography variant="h6" gutterBottom>
                        Performance Score: {analysisResult.performance_metrics?.score || 'N/A'}%
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={analysisResult.performance_metrics?.score || 0}
                        color={
                          analysisResult.performance_metrics?.score > 80 ? 'success' :
                          analysisResult.performance_metrics?.score > 60 ? 'warning' : 'error'
                        }
                        sx={{ height: 12, borderRadius: 6 }}
                      />
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {activeTab === 2 && renderHardwareDiagnostics()}
            {activeTab === 3 && renderSecurityIssues()}
            {activeTab === 4 && renderFailureAnalysis()}
          </motion.div>
        )}
      </Box>
    </ThemeProvider>
  );
};

export default DeviceAnalyzer;