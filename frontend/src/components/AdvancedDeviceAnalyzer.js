import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  CircularProgress,
  Divider,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  useTheme
} from '@mui/material';
import {
  Computer,
  Memory,
  Storage,
  Speed,
  CheckCircle,
  Refresh,
  Assessment,
  Security,
  NetworkCheck,
  BugReport,
  SystemUpdate,
  BatteryAlert,
  Thermostat,
  Analytics
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { getDeviceHealth, performQuickScan, performDeepScan } from '../services/deviceAnalyzerService';

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

// Metric Card Component
const MetricCard = ({ title, value, icon: Icon, status = 'normal', details, loading = false }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'critical':
        return '#f44336';
      case 'warning':
        return '#ff9800';
      case 'good':
        return '#4caf50';
      default:
        return '#2196f3';
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

// Scan Button Component
const ScanButton = ({ icon: Icon, label, color, onClick, disabled = false }) => {
  return (
    <Button
      variant="contained"
      startIcon={<Icon />}
      onClick={onClick}
      disabled={disabled}
      sx={{
        py: 1.5,
        px: 3,
        borderRadius: 2,
        background: `linear-gradient(45deg, ${color[0]} 30%, ${color[1]} 90%)`,
        boxShadow: `0 3px 5px 2px rgba(${color[2]}, .3)`,
        color: 'white',
        textTransform: 'none',
        fontWeight: 500,
        fontSize: '0.9rem',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0 6px 10px rgba(${color[2]}, .4)`,
        },
        '&.Mui-disabled': {
          background: 'rgba(255, 255, 255, 0.12)',
          color: 'rgba(255, 255, 255, 0.3)'
        }
      }}
    >
      {label}
    </Button>
  );
};

const AdvancedDeviceAnalyzer = ({ onQueryComplete, setLoading: setParentLoading }) => {
  const theme = useTheme();
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scanType, setScanType] = useState(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanResults, setScanResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealthData = async () => {
      try {
        setLoading(true);
        const data = await getDeviceHealth();
        setHealthData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching device health:', err);
        setError('Failed to fetch device health data');
      } finally {
        setLoading(false);
      }
    };

    fetchHealthData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleScan = async (type) => {
    try {
      setParentLoading?.(true);
      setScanType(type);
      setScanProgress(0);
      setScanResults(null);
      setError(null);
      
      // Simulate progress
      const progressInterval = setInterval(() => {
        setScanProgress(prev => {
          const newProgress = prev + Math.random() * 10;
          return newProgress >= 100 ? 100 : newProgress;
        });
      }, 300);
      
      // Perform scan based on type
      let results;
      if (type === 'quick') {
        results = await performQuickScan();
      } else if (type === 'deep') {
        results = await performDeepScan();
      } else if (type === 'advanced') {
        // For advanced analysis, we'll use a combination of quick scan with more details
        results = await performQuickScan('advanced_user');
      }
      
      clearInterval(progressInterval);
      setScanProgress(100);
      
      // Check if the results are valid
      if (results && results.success !== false) {
        setScanResults(results);
        
        // Transform the results into the expected format for SolutionDisplay
        const solution = {
          issue: results.overall_status === 'healthy' ? 'System Health Check' : 
                 results.overall_status === 'warning' ? 'System Performance Warning' : 
                 'System Issues Detected',
          possible_causes: results.detected_issues?.map(issue => issue.description) || [],
          recommended_steps: results.recommendations?.map((rec, index) => ({
            step_number: index + 1,
            description: rec
          })) || [],
          external_sources: []
        };
        
        // If there's a callback, call it with the results
        if (onQueryComplete) {
          onQueryComplete({
            solution: solution,
            query_id: `scan_${type}_${Date.now()}`
          });
        }
      } else {
        throw new Error(results?.error || 'Scan failed');
      }
      
    } catch (err) {
      console.error(`Error performing ${type} scan:`, err);
      setError(`Failed to complete ${type} scan: ${err.message}`);
      setScanProgress(0);
    } finally {
      setParentLoading?.(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const data = await getDeviceHealth();
      setHealthData(data);
      setError(null);
    } catch (err) {
      console.error('Error refreshing device health:', err);
      setError('Failed to refresh device health data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Title Section */}
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontFamily: '"Orbitron", sans-serif',
            fontWeight: 700,
            color: '#3b82f6',
            mb: 1
          }}
        >
          Advanced Device Health Analyzer
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'rgba(255, 255, 255, 0.7)',
            maxWidth: '800px'
          }}
        >
          Comprehensive system diagnostics with advanced failure analysis and security scanning
        </Typography>
      </Box>

      {/* Real-time Health Status */}
      <GlassCard 
        sx={{ 
          mb: 4, 
          background: 'linear-gradient(to right, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.1))',
          overflow: 'hidden'
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography 
              variant="h6" 
              sx={{ 
                fontFamily: '"Orbitron", sans-serif',
                color: 'white',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <Analytics sx={{ mr: 1 }} /> Real-time Health Status
            </Typography>
            
            <Box>
              <Tooltip title="Refresh">
                <IconButton 
                  onClick={handleRefresh} 
                  disabled={loading}
                  sx={{ 
                    color: 'white',
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.1)'
                    }
                  }}
                >
                  <Refresh />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Detailed Metrics">
                <IconButton 
                  sx={{ 
                    ml: 1,
                    color: 'white',
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                    '&:hover': {
                      bgcolor: 'rgba(255, 255, 255, 0.1)'
                    }
                  }}
                >
                  <Assessment />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          {loading ? (
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <CircularProgress size={28} sx={{ color: '#3b82f6', mb: 1 }} />
              <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Loading health status...
              </Typography>
            </Box>
          ) : error ? (
            <Box 
              sx={{ 
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
          ) : healthData ? (
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard 
                  title="CPU Usage" 
                  value={`${healthData.metrics?.cpu_usage?.toFixed(1) || 0}%`}
                  icon={Speed}
                  status={healthData.metrics?.cpu_usage > 80 ? 'critical' : 
                          healthData.metrics?.cpu_usage > 60 ? 'warning' : 'good'}
                  details="Current processor utilization"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard 
                  title="Memory Usage" 
                  value={`${healthData.metrics?.memory_usage?.toFixed(1) || 0}%`}
                  icon={Memory}
                  status={healthData.metrics?.memory_usage > 85 ? 'critical' : 
                          healthData.metrics?.memory_usage > 70 ? 'warning' : 'good'}
                  details="RAM utilization"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard 
                  title="Disk Usage" 
                  value={`${healthData.metrics?.disk_usage?.toFixed(1) || 0}%`}
                  icon={Storage}
                  status={healthData.metrics?.disk_usage > 90 ? 'critical' : 
                          healthData.metrics?.disk_usage > 75 ? 'warning' : 'good'}
                  details="Storage space used"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard 
                  title="System Status" 
                  value={healthData.status?.toUpperCase() || 'UNKNOWN'}
                  icon={Computer}
                  status={healthData.status === 'healthy' ? 'good' : 
                          healthData.status === 'warning' ? 'warning' : 'critical'}
                  details="Overall health assessment"
                />
              </Grid>
            </Grid>
          ) : (
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              No health data available
            </Typography>
          )}
        </CardContent>
      </GlassCard>

      {/* Diagnostic Scans */}
      <GlassCard sx={{ mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h6" 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              mb: 3,
              fontFamily: '"Orbitron", sans-serif',
              color: 'white'
            }}
          >
            <BugReport sx={{ mr: 1 }} /> Diagnostic Scans
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <ScanButton 
                icon={Speed} 
                label="QUICK SCAN" 
                color={['#4caf50', '#81c784', '76, 175, 80']}
                onClick={() => handleScan('quick')}
                disabled={scanType && scanProgress < 100}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <ScanButton 
                icon={Assessment} 
                label="ADVANCED ANALYSIS" 
                color={['#2196f3', '#64b5f6', '33, 150, 243']}
                onClick={() => handleScan('advanced')}
                disabled={scanType && scanProgress < 100}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <ScanButton 
                icon={Security} 
                label="DEEP DIAGNOSTIC" 
                color={['#ff9800', '#ffb74d', '255, 152, 0']}
                onClick={() => handleScan('deep')}
                disabled={scanType && scanProgress < 100}
              />
            </Grid>
          </Grid>
          
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.7)',
              mb: 1
            }}
          >
            Select a scan type based on your needs. Quick scans take seconds, while deep diagnostics provide comprehensive analysis.
          </Typography>
          
          <AnimatePresence>
            {scanType && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Box 
                  sx={{ 
                    mt: 3, 
                    p: 2, 
                    borderRadius: 2,
                    bgcolor: 'rgba(59, 130, 246, 0.1)',
                    border: '1px solid rgba(59, 130, 246, 0.2)'
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography 
                      sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        color: '#90caf9',
                        fontWeight: 500
                      }}
                    >
                      {scanType === 'quick' && <Speed sx={{ mr: 1 }} fontSize="small" />}
                      {scanType === 'advanced' && <Assessment sx={{ mr: 1 }} fontSize="small" />}
                      {scanType === 'deep' && <Security sx={{ mr: 1 }} fontSize="small" />}
                      {scanType.charAt(0).toUpperCase() + scanType.slice(1)} Scan {scanProgress < 100 ? 'in progress' : 'complete'}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontFamily: '"JetBrains Mono", monospace',
                        color: '#90caf9'
                      }}
                    >
                      {Math.round(scanProgress)}%
                    </Typography>
                  </Box>
                  
                  <LinearProgress 
                    variant="determinate" 
                    value={scanProgress} 
                    sx={{ 
                      height: 6, 
                      borderRadius: 3,
                      bgcolor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 3,
                        background: 'linear-gradient(90deg, #2196f3, #90caf9)'
                      }
                    }}
                  />
                  
                  {scanProgress === 100 && scanResults && (
                    <Box sx={{ mt: 2 }}>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#4caf50',
                          display: 'flex',
                          alignItems: 'center',
                          fontWeight: 500
                        }}
                      >
                        <CheckCircle sx={{ mr: 1 }} fontSize="small" />
                        Scan completed successfully
                      </Typography>
                    </Box>
                  )}
                </Box>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </GlassCard>
    </Box>
  );
};

export default AdvancedDeviceAnalyzer;
