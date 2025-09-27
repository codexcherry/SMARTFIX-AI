import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Badge,
  Alert,
  AlertTitle,
  Button,
  Tab,
  Tabs
} from '@mui/material';
import {
  Computer,
  Memory,
  Storage,
  Speed,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Assessment,
  Security,
  NetworkCheck,
  BugReport,
  SystemUpdate,
  BatteryAlert,
  Thermostat,
  Analytics,
  ExpandMore,
  Refresh,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Memory as MemoryIcon,
  NetworkCheck as NetworkIcon,
  Security as SecurityIcon,
  Hardware as HardwareIcon,
  Monitor as MonitorIcon,
  DeveloperBoard as DeveloperBoardIcon,
  Dashboard as DashboardIcon,
  Timeline as TimelineIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { getDeviceHealth, performQuickScan, performDeepScan } from '../services/deviceAnalyzerService';

// Glass Card Component
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
        } : {},
        ...props.sx
      }}
      {...props}
    >
      {children}
    </Card>
  );
};

// Metric Card Component
const MetricCard = ({ title, value, icon: Icon, status = 'normal', details, loading = false, color = '#2196f3' }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'critical':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      case 'good':
        return '#4caf50';
      default:
        return color;
    }
  };

  return (
    <GlassCard hover={true}>
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.7)',
              fontFamily: '"Orbitron", sans-serif',
              fontSize: '0.75rem',
              textTransform: 'uppercase',
              letterSpacing: '0.1em'
            }}
          >
            {title}
          </Typography>
          <Box 
            sx={{ 
              p: 0.75, 
              borderRadius: 1.5, 
              bgcolor: 'rgba(255, 255, 255, 0.05)',
              display: 'flex'
            }}
          >
            <Icon fontSize="small" sx={{ color: getStatusColor() }} />
          </Box>
        </Box>
        
        {loading ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 1 }}>
            <CircularProgress size={24} sx={{ color: getStatusColor() }} />
          </Box>
        ) : (
          <>
            <Typography 
              variant="h5" 
              sx={{ 
                fontWeight: 'bold', 
                color: 'white',
                fontFamily: '"JetBrains Mono", monospace',
              }}
            >
              {value}
            </Typography>
            
            {details && (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontSize: '0.75rem',
                  mt: 0.5
                }}
              >
                {details}
              </Typography>
            )}
          </>
        )}
      </CardContent>
    </GlassCard>
  );
};

// System Info Card Component
const SystemInfoCard = ({ title, icon: Icon, data, color = '#2196f3' }) => {
  return (
    <GlassCard>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box 
            sx={{ 
              p: 1, 
              borderRadius: 2, 
              bgcolor: `${color}20`, 
              display: 'flex',
              mr: 1
            }}
          >
            <Icon fontSize="small" sx={{ color: color }} />
          </Box>
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: '"Orbitron", sans-serif',
              color: 'white'
            }}
          >
            {title}
          </Typography>
        </Box>
        
        {data && (
          <Box>
            {Object.entries(data).map(([key, value]) => (
              <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                </Typography>
                <Typography variant="body2" sx={{ color: 'white', fontFamily: '"JetBrains Mono", monospace' }}>
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </GlassCard>
  );
};

// Performance Score Component
const PerformanceScore = ({ score, title, color = '#2196f3' }) => {
  const getScoreColor = (score) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  return (
    <GlassCard>
      <CardContent sx={{ textAlign: 'center' }}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: '"Orbitron", sans-serif',
            color: 'white',
            mb: 2
          }}
        >
          {title}
        </Typography>
        
        <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
          <CircularProgress
            variant="determinate"
            value={score}
            size={120}
            thickness={4}
            sx={{
              color: getScoreColor(score),
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }}
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography
              variant="h4"
              component="div"
              sx={{
                fontFamily: '"JetBrains Mono", monospace',
                fontWeight: 'bold',
                color: getScoreColor(score)
              }}
            >
              {Math.round(score)}
            </Typography>
          </Box>
        </Box>
        
        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
          {score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs Improvement'}
        </Typography>
      </CardContent>
    </GlassCard>
  );
};

// Issues List Component
const IssuesList = ({ issues, title, icon: Icon, color = '#f44336' }) => {
  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon sx={{ color: '#f44336' }} />;
      case 'warning':
        return <Warning sx={{ color: '#ff9800' }} />;
      default:
        return <InfoIcon sx={{ color: '#2196f3' }} />;
    }
  };

  return (
    <GlassCard>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box 
            sx={{ 
              p: 1, 
              borderRadius: 2, 
              bgcolor: `${color}20`, 
              display: 'flex',
              mr: 1
            }}
          >
            <Icon fontSize="small" sx={{ color: color }} />
          </Box>
          <Typography 
            variant="h6" 
            sx={{ 
              fontFamily: '"Orbitron", sans-serif',
              color: 'white'
            }}
          >
            {title}
          </Typography>
        </Box>

        {issues && issues.length > 0 ? (
          <List dense>
            {issues.slice(0, 5).map((issue, index) => (
              <ListItem key={index} sx={{ px: 0 }}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {getSeverityIcon(issue.severity)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ color: 'white' }}>
                      {issue.description}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                      {issue.details}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
            {issues.length > 5 && (
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', ml: 6 }}>
                +{issues.length - 5} more issues
              </Typography>
            )}
          </List>
        ) : (
          <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
            <CheckCircle sx={{ color: '#4caf50', mr: 1 }} />
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              No issues detected
            </Typography>
          </Box>
        )}
      </CardContent>
    </GlassCard>
  );
};

// Process Table Component
const ProcessTable = ({ processes, title }) => {
  return (
    <GlassCard>
      <CardContent>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: '"Orbitron", sans-serif',
            color: 'white',
            mb: 2
          }}
        >
          {title}
        </Typography>
        
        {processes && processes.length > 0 ? (
          <TableContainer component={Box} sx={{ maxHeight: 300 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.75rem' }}>Process</TableCell>
                  <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.75rem' }} align="right">CPU %</TableCell>
                  <TableCell sx={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.75rem' }} align="right">Memory %</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {processes.slice(0, 10).map((process, index) => (
                  <TableRow key={index} hover>
                    <TableCell sx={{ color: 'white', fontSize: '0.75rem' }}>
                      <Tooltip title={process.name}>
                        <span>{process.name.length > 20 ? `${process.name.substring(0, 20)}...` : process.name}</span>
                      </Tooltip>
                    </TableCell>
                    <TableCell sx={{ color: 'white', fontSize: '0.75rem' }} align="right">
                      {process.cpu_percent.toFixed(1)}%
                    </TableCell>
                    <TableCell sx={{ color: 'white', fontSize: '0.75rem' }} align="right">
                      {process.memory_percent.toFixed(1)}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center', py: 2 }}>
            No processes data available
          </Typography>
        )}
      </CardContent>
    </GlassCard>
  );
};

// Recommendation List Component
const RecommendationList = ({ recommendations, title }) => {
  return (
    <GlassCard>
      <CardContent>
        <Typography 
          variant="h6" 
          sx={{ 
            fontFamily: '"Orbitron", sans-serif',
            color: 'white',
            mb: 2
          }}
        >
          {title}
        </Typography>
        
        {recommendations && recommendations.length > 0 ? (
          <List dense>
            {recommendations.slice(0, 5).map((recommendation, index) => (
              <ListItem key={index} sx={{ px: 0 }}>
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <CheckCircle sx={{ color: '#4caf50' }} />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ color: 'white' }}>
                      {recommendation}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
            {recommendations.length > 5 && (
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', ml: 4 }}>
                +{recommendations.length - 5} more recommendations
              </Typography>
            )}
          </List>
        ) : (
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center', py: 2 }}>
            No recommendations available
          </Typography>
        )}
      </CardContent>
    </GlassCard>
  );
};

// DeviceAnalyzerDashboard Component
const DeviceAnalyzerDashboard = () => {
  const [deviceData, setDeviceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadDeviceData = async (scanType = 'quick') => {
    try {
      setScanning(true);
      let data;
      
      if (scanType === 'quick') {
        data = await performQuickScan();
      } else if (scanType === 'deep') {
        data = await performDeepScan();
      } else {
        data = await getDeviceHealth();
      }
      
      setDeviceData(data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading device data:', error);
    } finally {
      setLoading(false);
      setScanning(false);
    }
  };

  useEffect(() => {
    loadDeviceData();
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleRefresh = (scanType = 'quick') => {
    loadDeviceData(scanType);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress size={60} thickness={4} sx={{ color: '#2196f3' }} />
      </Box>
    );
  }

  const {
    system_info = {},
    health_metrics = {},
    detected_issues = [],
    recommendations = [],
    benchmark_results = {},
    summary = {}
  } = deviceData || {};

  const cpuMetrics = health_metrics.cpu || {};
  const memoryMetrics = health_metrics.memory || {};
  const diskMetrics = health_metrics.disk || {};
  const networkMetrics = health_metrics.network || {};
  const processes = health_metrics.processes || {};

  return (
    <Box sx={{ p: 3, background: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2a 100%)', minHeight: '100vh' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <DeveloperBoardIcon sx={{ fontSize: 40, color: '#2196f3', mr: 2 }} />
          <Box>
            <Typography 
              variant="h4" 
              sx={{ 
                fontFamily: '"Orbitron", sans-serif',
                color: 'white',
                fontWeight: 'bold'
              }}
            >
              Device Analyzer
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Comprehensive system diagnostics and health monitoring
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {lastUpdated && (
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', mr: 2 }}>
              Last updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
          )}
          <Tooltip title="Quick Scan">
            <IconButton 
              onClick={() => handleRefresh('quick')} 
              disabled={scanning}
              sx={{ color: 'rgba(255, 255, 255, 0.7)', '&:hover': { color: '#2196f3' } }}
            >
              <Refresh sx={{ transform: scanning ? 'rotate(360deg)' : 'none', transition: 'transform 1s' }} />
            </IconButton>
          </Tooltip>
          <Tooltip title="Deep Scan">
            <IconButton 
              onClick={() => handleRefresh('deep')} 
              disabled={scanning}
              sx={{ color: 'rgba(255, 255, 255, 0.7)', '&:hover': { color: '#2196f3' } }}
            >
              <Assessment />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Status Alert */}
      {deviceData && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Alert 
            severity={
              summary?.critical_issues > 0 ? 'error' : 
              summary?.warning_issues > 0 ? 'warning' : 'success'
            }
            sx={{ 
              mb: 3, 
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}
          >
            <AlertTitle>
              System Status: {deviceData.overall_status?.toUpperCase()}
            </AlertTitle>
            {summary?.critical_issues > 0 ? (
              <>{summary.critical_issues} critical issues detected that require immediate attention.</>
            ) : summary?.warning_issues > 0 ? (
              <>{summary.warning_issues} warnings detected. System performance may be affected.</>
            ) : (
              <>No critical issues detected. Your system is running optimally.</>
            )}
          </Alert>
        </motion.div>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'rgba(255, 255, 255, 0.1)', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} textColor="secondary" indicatorColor="secondary">
          <Tab 
            icon={<DashboardIcon />} 
            label="Dashboard" 
            sx={{ color: 'rgba(255, 255, 255, 0.7)', '&.Mui-selected': { color: '#2196f3' } }} 
          />
          <Tab 
            icon={<TimelineIcon />} 
            label="Performance" 
            sx={{ color: 'rgba(255, 255, 255, 0.7)', '&.Mui-selected': { color: '#2196f3' } }} 
          />
          <Tab 
            icon={<SecurityIcon />} 
            label="Security" 
            sx={{ color: 'rgba(255, 255, 255, 0.7)', '&.Mui-selected': { color: '#2196f3' } }} 
          />
          <Tab 
            icon={<InfoIcon />} 
            label="System Info" 
            sx={{ color: 'rgba(255, 255, 255, 0.7)', '&.Mui-selected': { color: '#2196f3' } }} 
          />
        </Tabs>
      </Box>

      {/* Dashboard Tab */}
      {activeTab === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Grid container spacing={3}>
            {/* Performance Scores */}
            <Grid item xs={12} md={4}>
              <PerformanceScore 
                score={summary?.system_health_score || 0} 
                title="Health Score" 
                color="#2196f3"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <PerformanceScore 
                score={benchmark_results?.overall_score || 0} 
                title="Performance Score" 
                color="#4caf50"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <GlassCard>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 2
                    }}
                  >
                    System Status
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-around', mb: 2 }}>
                    <Box sx={{ textAlign: 'center' }}>
                      <ErrorIcon sx={{ color: '#f44336', fontSize: 30 }} />
                      <Typography variant="h6" sx={{ color: '#f44336' }}>
                        {summary?.critical_issues || 0}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Critical
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Warning sx={{ color: '#ff9800', fontSize: 30 }} />
                      <Typography variant="h6" sx={{ color: '#ff9800' }}>
                        {summary?.warning_issues || 0}
                      </Typography>
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                        Warnings
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    {deviceData?.overall_status?.toUpperCase() || 'UNKNOWN'}
                  </Typography>
                </CardContent>
              </GlassCard>
            </Grid>

            {/* System Metrics */}
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="CPU Usage"
                value={`${cpuMetrics.usage_percent?.toFixed(1) || 0}%`}
                icon={SpeedIcon}
                status={
                  cpuMetrics.usage_percent > 90 ? 'critical' : 
                  cpuMetrics.usage_percent > 80 ? 'warning' : 'good'
                }
                details={`${system_info.cpu_count || 0} cores`}
                loading={scanning}
                color="#2196f3"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Memory Usage"
                value={`${memoryMetrics.usage_percent?.toFixed(1) || 0}%`}
                icon={MemoryIcon}
                status={
                  memoryMetrics.usage_percent > 90 ? 'critical' : 
                  memoryMetrics.usage_percent > 80 ? 'warning' : 'good'
                }
                details={`${(memoryMetrics.used_gb || 0).toFixed(1)}/${(memoryMetrics.total_gb || 0).toFixed(1)} GB`}
                loading={scanning}
                color="#4caf50"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Disk Usage"
                value={`${diskMetrics.usage_percent?.toFixed(1) || 0}%`}
                icon={StorageIcon}
                status={
                  diskMetrics.usage_percent > 90 ? 'critical' : 
                  diskMetrics.usage_percent > 80 ? 'warning' : 'good'
                }
                details={`${(diskMetrics.used_gb || 0).toFixed(1)}/${(diskMetrics.total_gb || 0).toFixed(1)} GB`}
                loading={scanning}
                color="#ff9800"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <MetricCard
                title="Network Activity"
                value={`${((networkMetrics.bytes_recv || 0) / 1024 / 1024).toFixed(1)} MB`}
                icon={NetworkIcon}
                status="normal"
                details={`${((networkMetrics.bytes_sent || 0) / 1024 / 1024).toFixed(1)} MB sent`}
                loading={scanning}
                color="#9c27b0"
              />
            </Grid>

            {/* Comprehensive Analysis Cards */}
            <Grid item xs={12} md={6}>
              <GlassCard>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 2,
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <BugReport sx={{ mr: 1, color: '#f44336' }} />
                    System Analysis Summary
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Overall System Status
                    </Typography>
                    <Chip 
                      label={deviceData?.overall_status?.toUpperCase() || 'UNKNOWN'} 
                      color={
                        deviceData?.overall_status === 'healthy' ? 'success' : 
                        deviceData?.overall_status === 'warning' ? 'warning' : 'error'
                      }
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Resource Utilization
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip 
                        label={`CPU: ${cpuMetrics.usage_percent?.toFixed(1) || 0}%`}
                        color={cpuMetrics.usage_percent > 80 ? 'error' : cpuMetrics.usage_percent > 60 ? 'warning' : 'success'}
                        size="small"
                      />
                      <Chip 
                        label={`RAM: ${memoryMetrics.usage_percent?.toFixed(1) || 0}%`}
                        color={memoryMetrics.usage_percent > 80 ? 'error' : memoryMetrics.usage_percent > 60 ? 'warning' : 'success'}
                        size="small"
                      />
                      <Chip 
                        label={`Disk: ${diskMetrics.usage_percent?.toFixed(1) || 0}%`}
                        color={diskMetrics.usage_percent > 80 ? 'error' : diskMetrics.usage_percent > 60 ? 'warning' : 'success'}
                        size="small"
                      />
                    </Box>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Process Analysis
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      Total Processes: {processes.total_processes || 0}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      High CPU Processes: {processes.high_cpu_processes?.length || 0}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      High Memory Processes: {processes.high_memory_processes?.length || 0}
                    </Typography>
                  </Box>

                  {detected_issues && detected_issues.length > 0 && (
                    <Box>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                        Critical Issues Detected
                      </Typography>
                      {detected_issues.slice(0, 3).map((issue, index) => (
                        <Box key={index} sx={{ mb: 1, p: 1, bgcolor: 'rgba(244, 67, 54, 0.1)', borderRadius: 1 }}>
                          <Typography variant="body2" sx={{ color: '#f44336', fontWeight: 'bold' }}>
                            {issue.description}
                          </Typography>
                          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                            {issue.details}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </GlassCard>
            </Grid>

            <Grid item xs={12} md={6}>
              <GlassCard>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 2,
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <CheckCircle sx={{ mr: 1, color: '#4caf50' }} />
                    Performance Insights
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Hardware Information
                    </Typography>
                    {deviceData?.hardware_info?.gpus && deviceData.hardware_info.gpus.length > 0 && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                          GPU: {deviceData.hardware_info.gpus[0].name}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                          GPU Memory: {deviceData.hardware_info.gpus[0].memory_used}MB / {deviceData.hardware_info.gpus[0].memory_total}MB
                        </Typography>
                      </Box>
                    )}
                    
                    {deviceData?.hardware_info?.disks && deviceData.hardware_info.disks.length > 0 && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                          Storage: {deviceData.hardware_info.disks[0].device} ({deviceData.hardware_info.disks[0].fstype})
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                          Free Space: {((deviceData.hardware_info.disks[0].free / 1024**3)).toFixed(1)}GB
                        </Typography>
                      </Box>
                    )}

                    {deviceData?.hardware_info?.battery && Object.keys(deviceData.hardware_info.battery).length > 0 && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                          Battery: {deviceData.hardware_info.battery.percent}% 
                          {deviceData.hardware_info.battery.power_plugged ? ' (Charging)' : ' (Discharging)'}
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Network Status
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      Hostname: {deviceData?.network_info?.hostname || 'Unknown'}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      IP Address: {deviceData?.network_info?.ip_address || 'Unknown'}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      Data Received: {((networkMetrics.bytes_recv || 0) / 1024 / 1024).toFixed(1)} MB
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      Data Sent: {((networkMetrics.bytes_sent || 0) / 1024 / 1024).toFixed(1)} MB
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
                      Security Status
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      Firewall: {deviceData?.security_info?.firewall_status || 'Unknown'}
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontSize: '0.9rem' }}>
                      Open Ports: {deviceData?.security_info?.open_ports?.length || 0}
                    </Typography>
                  </Box>
                </CardContent>
              </GlassCard>
            </Grid>

            {/* Comprehensive Device Summary */}
            <Grid item xs={12}>
              <GlassCard>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 3,
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <DeveloperBoardIcon sx={{ mr: 1, color: '#2196f3' }} />
                    Complete Device Analysis Summary
                  </Typography>
                  
                  <Grid container spacing={3}>
                    {/* System Information */}
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(33, 150, 243, 0.1)', borderRadius: 2 }}>
                        <Typography variant="subtitle1" sx={{ color: '#2196f3', fontWeight: 'bold', mb: 1 }}>
                          System Information
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Platform: {system_info.platform || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Architecture: {system_info.architecture || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Processor: {system_info.processor || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          CPU Cores: {system_info.cpu_count || 0} ({system_info.cpu_count_logical || 0} logical)
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Total RAM: {((system_info.memory_total || 0) / 1024**3).toFixed(1)} GB
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Hostname: {system_info.hostname || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Boot Time: {system_info.boot_time ? new Date(system_info.boot_time).toLocaleString() : 'Unknown'}
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Performance Metrics */}
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
                        <Typography variant="subtitle1" sx={{ color: '#4caf50', fontWeight: 'bold', mb: 1 }}>
                          Performance Metrics
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          CPU Usage: {cpuMetrics.usage_percent?.toFixed(1) || 0}%
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Memory Usage: {memoryMetrics.usage_percent?.toFixed(1) || 0}%
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Disk Usage: {diskMetrics.usage_percent?.toFixed(1) || 0}%
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Available Memory: {(memoryMetrics.available_gb || 0).toFixed(1)} GB
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Free Disk Space: {(diskMetrics.free_gb || 0).toFixed(1)} GB
                        </Typography>
                        {cpuMetrics.temperature && (
                          <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                            CPU Temperature: {cpuMetrics.temperature}°C
                          </Typography>
                        )}
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Total Processes: {processes.total_processes || 0}
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Hardware & Network */}
                    <Grid item xs={12} md={4}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(255, 152, 0, 0.1)', borderRadius: 2 }}>
                        <Typography variant="subtitle1" sx={{ color: '#ff9800', fontWeight: 'bold', mb: 1 }}>
                          Hardware & Network
                        </Typography>
                        
                        {deviceData?.hardware_info?.gpus && deviceData.hardware_info.gpus.length > 0 && (
                          <>
                            <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                              GPU: {deviceData.hardware_info.gpus[0].name}
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                              GPU Memory: {deviceData.hardware_info.gpus[0].memory_used}MB / {deviceData.hardware_info.gpus[0].memory_total}MB
                            </Typography>
                          </>
                        )}
                        
                        {deviceData?.hardware_info?.disks && deviceData.hardware_info.disks.length > 0 && (
                          <>
                            <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                              Storage: {deviceData.hardware_info.disks[0].device}
                            </Typography>
                            <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                              Free Space: {((deviceData.hardware_info.disks[0].free / 1024**3)).toFixed(1)}GB
                            </Typography>
                          </>
                        )}

                        {deviceData?.hardware_info?.battery && Object.keys(deviceData.hardware_info.battery).length > 0 && (
                          <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                            Battery: {deviceData.hardware_info.battery.percent}% 
                            {deviceData.hardware_info.battery.power_plugged ? ' (Charging)' : ' (Discharging)'}
                          </Typography>
                        )}
                        
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Network: {deviceData?.network_info?.hostname || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          IP: {deviceData?.network_info?.ip_address || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Data RX: {((networkMetrics.bytes_recv || 0) / 1024 / 1024).toFixed(1)} MB
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Data TX: {((networkMetrics.bytes_sent || 0) / 1024 / 1024).toFixed(1)} MB
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Security & Issues */}
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(244, 67, 54, 0.1)', borderRadius: 2 }}>
                        <Typography variant="subtitle1" sx={{ color: '#f44336', fontWeight: 'bold', mb: 1 }}>
                          Security & Issues
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Firewall: {deviceData?.security_info?.firewall_status || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Open Ports: {deviceData?.security_info?.open_ports?.length || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Critical Issues: {summary?.critical_issues || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Warning Issues: {summary?.warning_issues || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          High CPU Processes: {processes.high_cpu_processes?.length || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          High Memory Processes: {processes.high_memory_processes?.length || 0}
                        </Typography>
                      </Box>
                    </Grid>

                    {/* Benchmark Results */}
                    <Grid item xs={12} md={6}>
                      <Box sx={{ p: 2, bgcolor: 'rgba(156, 39, 176, 0.1)', borderRadius: 2 }}>
                        <Typography variant="subtitle1" sx={{ color: '#9c27b0', fontWeight: 'bold', mb: 1 }}>
                          Benchmark Results
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Overall Score: {benchmark_results?.overall_score || 0}/100
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          CPU Score: {benchmark_results?.cpu_score || 0}/100
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Memory Score: {benchmark_results?.memory_score || 0}/100
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Disk Score: {benchmark_results?.disk_score || 0}/100
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Health Score: {summary?.system_health_score || 0}/100
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'white', mb: 0.5 }}>
                          Performance Score: {summary?.performance_score || 0}/100
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </GlassCard>
            </Grid>

            {/* Process Monitoring */}
            <Grid item xs={12} md={6}>
              <ProcessTable
                processes={processes.high_cpu_processes || []}
                title="High CPU Processes"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <ProcessTable
                processes={processes.high_memory_processes || []}
                title="High Memory Processes"
              />
            </Grid>
          </Grid>
        </motion.div>
      )}

      {/* Performance Tab */}
      {activeTab === 1 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="CPU Details"
                icon={SpeedIcon}
                data={cpuMetrics}
                color="#2196f3"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Memory Details"
                icon={MemoryIcon}
                data={memoryMetrics}
                color="#4caf50"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Disk Details"
                icon={StorageIcon}
                data={diskMetrics}
                color="#ff9800"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Network Details"
                icon={NetworkIcon}
                data={networkMetrics}
                color="#9c27b0"
              />
            </Grid>
            <Grid item xs={12}>
              <GlassCard>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 2
                    }}
                  >
                    Benchmark Results
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <CircularProgress
                          variant="determinate"
                          value={benchmark_results?.cpu_score || 0}
                          size={80}
                          thickness={4}
                          sx={{ color: '#2196f3', mb: 1 }}
                        />
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          CPU Score
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#2196f3' }}>
                          {benchmark_results?.cpu_score || 0}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <CircularProgress
                          variant="determinate"
                          value={benchmark_results?.disk_score || 0}
                          size={80}
                          thickness={4}
                          sx={{ color: '#4caf50', mb: 1 }}
                        />
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          Disk Score
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#4caf50' }}>
                          {benchmark_results?.disk_score || 0}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center' }}>
                        <CircularProgress
                          variant="determinate"
                          value={benchmark_results?.memory_score || 0}
                          size={80}
                          thickness={4}
                          sx={{ color: '#ff9800', mb: 1 }}
                        />
                        <Typography variant="body2" sx={{ color: 'white' }}>
                          Memory Score
                        </Typography>
                        <Typography variant="h6" sx={{ color: '#ff9800' }}>
                          {benchmark_results?.memory_score || 0}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </GlassCard>
            </Grid>
          </Grid>
        </motion.div>
      )}

      {/* Security Tab */}
      {activeTab === 2 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Security Status"
                icon={SecurityIcon}
                data={deviceData?.security_info || {}}
                color="#f44336"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <GlassCard>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 2
                    }}
                  >
                    Security Recommendations
                  </Typography>
                  <List dense>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle sx={{ color: '#4caf50' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary="Enable firewall protection"
                        primaryTypographyProps={{ sx: { color: 'white', fontSize: '0.9rem' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle sx={{ color: '#4caf50' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary="Install and update antivirus software"
                        primaryTypographyProps={{ sx: { color: 'white', fontSize: '0.9rem' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle sx={{ color: '#4caf50' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary="Run regular system updates"
                        primaryTypographyProps={{ sx: { color: 'white', fontSize: '0.9rem' } }}
                      />
                    </ListItem>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle sx={{ color: '#4caf50' }} />
                      </ListItemIcon>
                      <ListItemText
                        primary="Use strong, unique passwords"
                        primaryTypographyProps={{ sx: { color: 'white', fontSize: '0.9rem' } }}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </GlassCard>
            </Grid>
            <Grid item xs={12}>
              <GlassCard>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontFamily: '"Orbitron", sans-serif',
                      color: 'white',
                      mb: 2
                    }}
                  >
                    Open Ports Scan
                  </Typography>
                  {deviceData?.security_info?.open_ports && deviceData.security_info.open_ports.length > 0 ? (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {deviceData.security_info.open_ports.map((port, index) => (
                        <Chip
                          key={index}
                          label={`Port ${port}`}
                          color="warning"
                          variant="outlined"
                          size="small"
                        />
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                      No open ports detected or scan not available.
                    </Typography>
                  )}
                </CardContent>
              </GlassCard>
            </Grid>
          </Grid>
        </motion.div>
      )}

      {/* System Info Tab */}
      {activeTab === 3 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="System Information"
                icon={Computer}
                data={system_info}
                color="#2196f3"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Hardware Information"
                icon={HardwareIcon}
                data={deviceData?.hardware_info || {}}
                color="#4caf50"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Network Information"
                icon={NetworkIcon}
                data={deviceData?.network_info || {}}
                color="#9c27b0"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SystemInfoCard
                title="Process Information"
                icon={MonitorIcon}
                data={processes}
                color="#ff9800"
              />
            </Grid>
          </Grid>
        </motion.div>
      )}
    </Box>
  );
};

export default DeviceAnalyzerDashboard;