'use client';

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Chip,
  Alert,
  Collapse,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Speed as SpeedIcon,
  CloudSync as CloudSyncIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
// import { useTranslation } from 'react-i18next';
import { useComplianceData } from '@/hooks/useComplianceData';

const QuickActions: React.FC = () => {
  // const { t } = useTranslation();
  const t = (key: string) => key; // Fallback translation function
  const { evaluateCompliance, refetch } = useComplianceData();
  const [expandedActions, setExpandedActions] = useState(false);
  const [actionStatus, setActionStatus] = useState<{[key: string]: 'idle' | 'loading' | 'success' | 'error'}>({});

  const quickActions = [
    {
      id: 'quick-evaluation',
      title: 'Quick Compliance Check',
      description: 'Run a fast compliance evaluation',
      icon: <SpeedIcon />,
      color: 'primary',
      action: async () => {
        setActionStatus(prev => ({ ...prev, 'quick-evaluation': 'loading' }));
        try {
          await evaluateCompliance.mutateAsync({ 
            type: 'quick', 
            vendor: 'auto-detect',
            policy: 'all' 
          });
          setActionStatus(prev => ({ ...prev, 'quick-evaluation': 'success' }));
        } catch (error) {
          setActionStatus(prev => ({ ...prev, 'quick-evaluation': 'error' }));
        }
      },
    },
    {
      id: 'refresh-data',
      title: 'Refresh Dashboard',
      description: 'Update all dashboard data',
      icon: <RefreshIcon />,
      color: 'secondary',
      action: async () => {
        setActionStatus(prev => ({ ...prev, 'refresh-data': 'loading' }));
        try {
          await refetch();
          setActionStatus(prev => ({ ...prev, 'refresh-data': 'success' }));
        } catch (error) {
          setActionStatus(prev => ({ ...prev, 'refresh-data': 'error' }));
        }
      },
    },
    {
      id: 'download-report',
      title: 'Download Report',
      description: 'Export compliance report',
      icon: <DownloadIcon />,
      color: 'success',
      action: async () => {
        setActionStatus(prev => ({ ...prev, 'download-report': 'loading' }));
        try {
          // Simulate download
          await new Promise(resolve => setTimeout(resolve, 2000));
          const link = document.createElement('a');
          link.href = 'data:text/plain;charset=utf-8,Sample Compliance Report';
          link.download = `compliance-report-${new Date().toISOString().split('T')[0]}.txt`;
          link.click();
          setActionStatus(prev => ({ ...prev, 'download-report': 'success' }));
        } catch (error) {
          setActionStatus(prev => ({ ...prev, 'download-report': 'error' }));
        }
      },
    },
  ];

  const additionalActions = [
    {
      id: 'full-audit',
      title: 'Full System Audit',
      description: 'Comprehensive compliance audit',
      icon: <AssessmentIcon />,
      color: 'warning',
    },
    {
      id: 'security-scan',
      title: 'Security Scan',
      description: 'Run security vulnerability scan',
      icon: <SecurityIcon />,
      color: 'error',
    },
    {
      id: 'sync-policies',
      title: 'Sync Policies',
      description: 'Update compliance policies',
      icon: <CloudSyncIcon />,
      color: 'info',
    },
    {
      id: 'system-settings',
      title: 'System Settings',
      description: 'Configure system parameters',
      icon: <SettingsIcon />,
      color: 'default',
    },
  ];

  const recentActivities = [
    {
      id: '1',
      title: 'NCA Policy Updated',
      description: 'Commercial authorization requirements',
      timestamp: '2 minutes ago',
      status: 'success',
    },
    {
      id: '2',
      title: 'SAMA Compliance Check',
      description: 'Banking regulations verification',
      timestamp: '15 minutes ago',
      status: 'warning',
    },
    {
      id: '3',
      title: 'Security Alert Resolved',
      description: 'Authentication system alert',
      timestamp: '1 hour ago',
      status: 'success',
    },
  ];

  const handleAction = async (actionId: string, actionFn?: () => Promise<void>) => {
    if (actionFn) {
      await actionFn();
    } else {
      setActionStatus(prev => ({ ...prev, [actionId]: 'loading' }));
      setTimeout(() => {
        setActionStatus(prev => ({ ...prev, [actionId]: 'success' }));
      }, 1500);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getActionButtonProps = (actionId: string) => {
    const status = actionStatus[actionId];
    switch (status) {
      case 'loading':
        return { disabled: true, children: 'Running...' };
      case 'success':
        return { color: 'success' as const, children: 'Completed' };
      case 'error':
        return { color: 'error' as const, children: 'Failed' };
      default:
        return { children: 'Run' };
    }
  };

  return (
    <Box>
      {/* Quick Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Actions
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {quickActions.map((action, index) => (
              <motion.div
                key={action.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    p: 2,
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1,
                        bgcolor: `${action.color}.light`,
                        color: `${action.color}.contrastText`,
                      }}
                    >
                      {action.icon}
                    </Box>
                    <Box>
                      <Typography variant="body1" fontWeight="medium">
                        {action.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {action.description}
                      </Typography>
                    </Box>
                  </Box>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleAction(action.id, action.action)}
                    startIcon={<PlayIcon />}
                    {...getActionButtonProps(action.id)}
                  />
                </Box>
              </motion.div>
            ))}
          </Box>

          {/* More Actions */}
          <Box sx={{ mt: 2 }}>
            <Button
              onClick={() => setExpandedActions(!expandedActions)}
              endIcon={expandedActions ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              size="small"
            >
              {expandedActions ? 'Fewer' : 'More'} Actions
            </Button>
            
            <Collapse in={expandedActions}>
              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                {additionalActions.map((action) => (
                  <Box
                    key={action.id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 1.5,
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      bgcolor: 'background.default',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ color: `${action.color}.main` }}>
                        {action.icon}
                      </Box>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {action.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {action.description}
                        </Typography>
                      </Box>
                    </Box>
                    <Button
                      variant="text"
                      size="small"
                      onClick={() => handleAction(action.id)}
                      {...getActionButtonProps(action.id)}
                    />
                  </Box>
                ))}
              </Box>
            </Collapse>
          </Box>
        </CardContent>
      </Card>

      {/* Recent Activities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <NotificationsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Recent Activities
          </Typography>
          
          <List dense>
            {recentActivities.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <ListItem sx={{ px: 0 }}>
                  <ListItemIcon>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: `${getStatusColor(activity.status)}.main`,
                      }}
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="body2" fontWeight="medium">
                          {activity.title}
                        </Typography>
                        <Chip
                          label={activity.status}
                          size="small"
                          color={getStatusColor(activity.status) as any}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {activity.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {activity.timestamp}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              </motion.div>
            ))}
          </List>

          {recentActivities.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No recent activities to display.
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export { QuickActions };
