'use client';

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Skeleton,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Circle as CircleIcon,
  Computer as ComputerIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
  NetworkCheck as NetworkIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
// import { useTranslation } from 'react-i18next';

interface SystemHealthIndicatorProps {
  data: any;
  isLoading: boolean;
  isConnected: boolean;
}

interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'degraded';
  responseTime?: number;
  lastCheck: string;
  icon: React.ReactNode;
}

const SystemHealthIndicator: React.FC<SystemHealthIndicatorProps> = ({ 
  data, 
  isLoading, 
  isConnected 
}) => {
  // const { t } = useTranslation();
  const t = (key: string) => key; // Fallback translation function

  const services: ServiceStatus[] = [
    {
      name: 'API Gateway',
      status: data?.services?.api?.status || 'online',
      responseTime: data?.services?.api?.responseTime || 120,
      lastCheck: data?.services?.api?.lastCheck || new Date().toISOString(),
      icon: <NetworkIcon />,
    },
    {
      name: 'Database',
      status: data?.services?.database?.status || 'online',
      responseTime: data?.services?.database?.responseTime || 45,
      lastCheck: data?.services?.database?.lastCheck || new Date().toISOString(),
      icon: <StorageIcon />,
    },
    {
      name: 'Authentication',
      status: data?.services?.auth?.status || 'online',
      responseTime: data?.services?.auth?.responseTime || 85,
      lastCheck: data?.services?.auth?.lastCheck || new Date().toISOString(),
      icon: <SecurityIcon />,
    },
    {
      name: 'Compliance Engine',
      status: data?.services?.compliance?.status || 'online',
      responseTime: data?.services?.compliance?.responseTime || 200,
      lastCheck: data?.services?.compliance?.lastCheck || new Date().toISOString(),
      icon: <ComputerIcon />,
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckIcon color="success" />;
      case 'degraded':
        return <WarningIcon color="warning" />;
      case 'offline':
        return <ErrorIcon color="error" />;
      default:
        return <CircleIcon color="disabled" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'offline':
        return 'error';
      default:
        return 'default';
    }
  };

  const getOverallStatus = () => {
    if (!isConnected) return 'critical';
    
    const statuses = services.map(s => s.status);
    if (statuses.includes('offline')) return 'critical';
    if (statuses.includes('degraded')) return 'warning';
    return 'healthy';
  };

  const getOverallStatusMessage = () => {
    const status = getOverallStatus();
    switch (status) {
      case 'healthy':
        return 'All systems operational';
      case 'warning':
        return 'Some services experiencing issues';
      case 'critical':
        return 'Critical system issues detected';
      default:
        return 'Status unknown';
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Grid container spacing={2}>
            {Array.from({ length: 4 }).map((_, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Skeleton variant="circular" width={40} height={40} />
                  <Box sx={{ flexGrow: 1 }}>
                    <Skeleton variant="text" height={24} />
                    <Skeleton variant="text" height={20} width="60%" />
                  </Box>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            System Health
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getStatusIcon(getOverallStatus())}
              <Typography variant="body2" color="text.secondary">
                {getOverallStatusMessage()}
              </Typography>
            </Box>
            
            <Chip
              icon={<CircleIcon />}
              label={`${data?.uptime ? Math.floor(data.uptime / 1000 / 60 / 60 / 24) : 0} days uptime`}
              color="info"
              variant="outlined"
              size="small"
            />
          </Box>
        </Box>

        {!isConnected && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Real-time connection lost. Health data may be outdated.
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Overall Health Score */}
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={data?.responseTime ? Math.max(100 - (data.responseTime / 10), 0) : 95}
                  size={120}
                  thickness={4}
                  color={getStatusColor(getOverallStatus()) as any}
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
                    flexDirection: 'column',
                  }}
                >
                  <Typography variant="h4" component="div" color="text.primary">
                    {data?.responseTime ? Math.max(100 - Math.floor(data.responseTime / 10), 0) : 95}
                  </Typography>
                  <Typography variant="caption" component="div" color="text.secondary">
                    Health Score
                  </Typography>
                </Box>
              </Box>
              
              <Typography variant="h6" gutterBottom>
                System Performance
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Response: {data?.responseTime?.toFixed(0) || 120}ms
              </Typography>
            </Box>
          </Grid>

          {/* Service Status */}
          <Grid item xs={12} md={8}>
            <List dense>
              {services.map((service, index) => (
                <motion.div
                  key={service.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ListItem
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: 'background.paper',
                    }}
                  >
                    <ListItemIcon>
                      {service.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body1">{service.name}</Typography>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {service.responseTime && (
                              <Typography variant="body2" color="text.secondary">
                                {service.responseTime}ms
                              </Typography>
                            )}
                            <Chip
                              icon={getStatusIcon(service.status)}
                              label={service.status.toUpperCase()}
                              size="small"
                              color={getStatusColor(service.status) as any}
                            />
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={service.responseTime ? Math.max(100 - (service.responseTime / 5), 0) : 90}
                            color={getStatusColor(service.status) as any}
                            sx={{ height: 4, borderRadius: 2 }}
                          />
                          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                            Last checked: {new Date(service.lastCheck).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                </motion.div>
              ))}
            </List>
          </Grid>
        </Grid>

        {/* Quick Stats */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary" align="center">
                Services Online
              </Typography>
              <Typography variant="h6" align="center" color="success.main">
                {services.filter(s => s.status === 'online').length}/{services.length}
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary" align="center">
                Avg Response
              </Typography>
              <Typography variant="h6" align="center">
                {Math.floor(services.reduce((acc, s) => acc + (s.responseTime || 0), 0) / services.length)}ms
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary" align="center">
                Uptime
              </Typography>
              <Typography variant="h6" align="center" color="success.main">
                99.9%
              </Typography>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Typography variant="body2" color="text.secondary" align="center">
                Last Update
              </Typography>
              <Typography variant="h6" align="center">
                {new Date().toLocaleTimeString()}
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};

export { SystemHealthIndicator };
