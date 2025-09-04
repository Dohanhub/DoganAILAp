'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  LinearProgress,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Refresh as RefreshIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  Signal as SignalIcon,
  NetworkCheck as NetworkIcon,
  Speed as SpeedIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Notifications as NotificationsIcon,
  TrendingUp as TrendingUpIcon,
  Computer as ComputerIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
// import { useTranslation } from 'react-i18next';

interface RealTimeMonitoringProps {
  data: any;
  isConnected: boolean;
}

interface SystemMetric {
  name: string;
  value: number;
  unit: string;
  status: 'good' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
}

interface LiveEvent {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: Date;
  source: string;
}

const RealTimeMonitoring: React.FC<RealTimeMonitoringProps> = ({ data, isConnected }) => {
  // const { t } = useTranslation();
  const t = (key: string) => key; // Fallback translation function
  const [isPaused, setIsPaused] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [liveEvents, setLiveEvents] = useState<LiveEvent[]>([]);
  const [performanceHistory, setPerformanceHistory] = useState<any[]>([]);

  // Generate mock live events
  useEffect(() => {
    if (!autoRefresh || isPaused) return;

    const interval = setInterval(() => {
      const eventTypes = ['info', 'warning', 'error', 'success'] as const;
      const sources = ['Compliance Engine', 'API Gateway', 'Database', 'Authentication', 'File System'];
      const messages = [
        'Compliance check completed successfully',
        'High memory usage detected',
        'Connection timeout on external API',
        'New vendor registration processed',
        'Database query optimization applied',
        'Security alert: Multiple failed login attempts',
        'Backup process completed',
        'System health check passed',
      ];

      const newEvent: LiveEvent = {
        id: Math.random().toString(36).substr(2, 9),
        type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
        message: messages[Math.floor(Math.random() * messages.length)],
        timestamp: new Date(),
        source: sources[Math.floor(Math.random() * sources.length)],
      };

      setLiveEvents(prev => [newEvent, ...prev.slice(0, 19)]); // Keep last 20 events

      // Update performance history
      const timestamp = new Date().toLocaleTimeString();
      const newDataPoint = {
        time: timestamp,
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        responseTime: Math.random() * 500 + 100,
        throughput: Math.random() * 1000 + 500,
      };

      setPerformanceHistory(prev => [...prev.slice(-19), newDataPoint]); // Keep last 20 points
    }, 2000);

    return () => clearInterval(interval);
  }, [autoRefresh, isPaused]);

  const systemMetrics: SystemMetric[] = [
    {
      name: 'CPU Usage',
      value: data?.metrics?.cpu || Math.random() * 100,
      unit: '%',
      status: (data?.metrics?.cpu || Math.random() * 100) > 80 ? 'critical' : 'good',
      trend: 'stable',
    },
    {
      name: 'Memory Usage',
      value: data?.metrics?.memory || Math.random() * 100,
      unit: '%',
      status: (data?.metrics?.memory || Math.random() * 100) > 75 ? 'warning' : 'good',
      trend: 'up',
    },
    {
      name: 'Response Time',
      value: data?.metrics?.responseTime || Math.random() * 500 + 100,
      unit: 'ms',
      status: (data?.metrics?.responseTime || Math.random() * 500 + 100) > 300 ? 'warning' : 'good',
      trend: 'down',
    },
    {
      name: 'Throughput',
      value: data?.metrics?.throughput || Math.random() * 1000 + 500,
      unit: 'req/s',
      status: 'good',
      trend: 'up',
    },
    {
      name: 'Active Connections',
      value: data?.metrics?.connections || Math.floor(Math.random() * 100) + 50,
      unit: '',
      status: 'good',
      trend: 'stable',
    },
    {
      name: 'Error Rate',
      value: data?.metrics?.errorRate || Math.random() * 5,
      unit: '%',
      status: (data?.metrics?.errorRate || Math.random() * 5) > 2 ? 'critical' : 'good',
      trend: 'down',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <NotificationsIcon color="info" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUpIcon color="success" fontSize="small" />;
      case 'down':
        return <TrendingUpIcon color="error" fontSize="small" sx={{ transform: 'rotate(180deg)' }} />;
      default:
        return <SignalIcon color="info" fontSize="small" />;
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Real-Time Monitoring
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
            }
            label="Auto Refresh"
          />
          
          <Tooltip title={isPaused ? 'Resume' : 'Pause'}>
            <IconButton onClick={() => setIsPaused(!isPaused)}>
              {isPaused ? <PlayIcon /> : <PauseIcon />}
            </IconButton>
          </Tooltip>

          <Chip
            icon={<NetworkIcon />}
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            variant="outlined"
          />
        </Box>
      </Box>

      {!isConnected && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Real-time connection lost. Showing cached data and attempting to reconnect...
        </Alert>
      )}

      {/* System Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {systemMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={metric.name}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {metric.name}
                    </Typography>
                    {getTrendIcon(metric.trend)}
                  </Box>
                  
                  <Typography variant="h4" color={`${getStatusColor(metric.status)}.main`}>
                    {metric.value.toFixed(metric.name === 'Response Time' ? 0 : 1)}
                    <Typography component="span" variant="body2" color="text.secondary">
                      {metric.unit}
                    </Typography>
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={metric.name.includes('Time') ? Math.min((metric.value / 500) * 100, 100) : 
                           metric.name === 'Error Rate' ? metric.value * 20 : 
                           metric.value}
                    color={getStatusColor(metric.status) as any}
                    sx={{ mt: 1, height: 6, borderRadius: 3 }}
                  />

                  <Chip
                    label={metric.status.toUpperCase()}
                    size="small"
                    color={getStatusColor(metric.status) as any}
                    sx={{ mt: 1 }}
                  />
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Performance Charts */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Performance Metrics
              </Typography>
              
              <Box sx={{ height: 300, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip 
                      formatter={(value: any, name: string) => [
                        `${value.toFixed(1)}${name === 'responseTime' ? 'ms' : name === 'throughput' ? ' req/s' : '%'}`,
                        name.charAt(0).toUpperCase() + name.slice(1)
                      ]}
                    />
                    <Area type="monotone" dataKey="cpu" stackId="1" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                    <Area type="monotone" dataKey="memory" stackId="1" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>

              <Box sx={{ height: 200, mt: 3 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip 
                      formatter={(value: any, name: string) => [
                        `${value.toFixed(1)}${name === 'responseTime' ? 'ms' : ' req/s'}`,
                        name === 'responseTime' ? 'Response Time' : 'Throughput'
                      ]}
                    />
                    <Line type="monotone" dataKey="responseTime" stroke="#ff7300" strokeWidth={2} />
                    <Line type="monotone" dataKey="throughput" stroke="#00ff00" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Live Events */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <ComputerIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Live Events
                </Typography>
                {isPaused && <CircularProgress size={16} />}
              </Box>

              <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                <AnimatePresence>
                  {liveEvents.map((event, index) => (
                    <motion.div
                      key={event.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ListItem>
                        <ListItemIcon>
                          {getEventIcon(event.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={event.message}
                          secondary={
                            <Box>
                              <Typography variant="caption" display="block">
                                {event.source}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {event.timestamp.toLocaleTimeString()}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </List>

              {liveEvents.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No recent events
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export { RealTimeMonitoring };
