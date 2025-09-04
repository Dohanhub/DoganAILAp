'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Switch,
  FormControlLabel,
  Alert,
  Badge,
  Fab,
  Zoom,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  SmartToy as SmartIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as CheckIcon,
  Settings as SettingsIcon,
  Close as CloseIcon,
  AutoFixHigh as AutoFixIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface SmartAlert {
  id: string;
  type: 'security' | 'compliance' | 'performance' | 'prediction' | 'anomaly';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  timestamp: Date;
  isRead: boolean;
  isAiGenerated: boolean;
  autoResolved: boolean;
  actions?: Array<{
    label: string;
    action: () => void;
    variant?: 'text' | 'outlined' | 'contained';
  }>;
  metadata?: {
    confidence?: number;
    source?: string;
    affectedSystems?: string[];
  };
}

const SmartAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<SmartAlert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<SmartAlert | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [smartAlertsEnabled, setSmartAlertsEnabled] = useState(true);
  const [autoResolveEnabled, setAutoResolveEnabled] = useState(true);
  const [isMonitoring, setIsMonitoring] = useState(true);

  // Generate smart alerts with AI-like intelligence
  const generateSmartAlerts = () => {
    const alertTypes = ['security', 'compliance', 'performance', 'prediction', 'anomaly'] as const;
    const severities = ['low', 'medium', 'high', 'critical'] as const;
    
    const alertTemplates = [
      {
        type: 'security',
        severity: 'critical',
        title: 'Suspicious Login Activity Detected',
        message: 'Multiple failed login attempts from IP 192.168.1.100. AI analysis suggests potential brute force attack.',
        confidence: 94,
        source: 'AI Security Monitor',
      },
      {
        type: 'compliance',
        severity: 'high',
        title: 'SAMA Regulation Violation Imminent',
        message: 'Current IBM configuration will violate SAMA banking regulations in 48 hours based on predictive analysis.',
        confidence: 87,
        source: 'Compliance Predictor',
      },
      {
        type: 'performance',
        severity: 'medium',
        title: 'Database Performance Degradation',
        message: 'Query response times increased by 230%. AI recommends index optimization.',
        confidence: 92,
        source: 'Performance AI',
      },
      {
        type: 'anomaly',
        severity: 'high',
        title: 'Unusual Data Access Pattern',
        message: 'User admin@doganai.com accessing 450% more compliance records than usual. Anomaly detection triggered.',
        confidence: 89,
        source: 'Behavior Analytics',
      },
      {
        type: 'prediction',
        severity: 'medium',
        title: 'Compliance Score Drop Predicted',
        message: 'AI models predict 15% compliance score drop next week due to Oracle policy changes.',
        confidence: 78,
        source: 'Predictive Engine',
      },
    ];

    const newAlert = alertTemplates[Math.floor(Math.random() * alertTemplates.length)];
    
    const alert: SmartAlert = {
      id: Math.random().toString(36).substr(2, 9),
      type: newAlert.type as any,
      severity: newAlert.severity as any,
      title: newAlert.title,
      message: newAlert.message,
      timestamp: new Date(),
      isRead: false,
      isAiGenerated: true,
      autoResolved: false,
      metadata: {
        confidence: newAlert.confidence,
        source: newAlert.source,
        affectedSystems: ['Compliance Engine', 'Database', 'API Gateway'],
      },
      actions: [
        {
          label: 'Auto-Resolve',
          action: () => handleAutoResolve(alert.id),
          variant: 'contained',
        },
        {
          label: 'Investigate',
          action: () => handleInvestigate(alert.id),
          variant: 'outlined',
        },
        {
          label: 'Dismiss',
          action: () => handleDismiss(alert.id),
          variant: 'text',
        },
      ],
    };

    setAlerts(prev => [alert, ...prev.slice(0, 19)]);
  };

  useEffect(() => {
    if (smartAlertsEnabled && isMonitoring) {
      const interval = setInterval(() => {
        if (Math.random() > 0.7) { // 30% chance every 5 seconds
          generateSmartAlerts();
        }
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [smartAlertsEnabled, isMonitoring]);

  const handleAlertClick = (alert: SmartAlert) => {
    setSelectedAlert(alert);
    setDetailsOpen(true);
    
    // Mark as read
    setAlerts(prev =>
      prev.map(a => a.id === alert.id ? { ...a, isRead: true } : a)
    );
  };

  const handleAutoResolve = (alertId: string) => {
    setAlerts(prev =>
      prev.map(alert =>
        alert.id === alertId 
          ? { ...alert, autoResolved: true, isRead: true }
          : alert
      )
    );
  };

  const handleInvestigate = (alertId: string) => {
    console.log('Investigating alert:', alertId);
    // Navigate to investigation view
  };

  const handleDismiss = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const getAlertIcon = (type: string, isAiGenerated: boolean) => {
    const baseIcon = (() => {
      switch (type) {
        case 'security':
          return <SecurityIcon />;
        case 'compliance':
          return <CheckIcon />;
        case 'performance':
          return <InfoIcon />;
        case 'prediction':
          return <SmartIcon />;
        case 'anomaly':
          return <WarningIcon />;
        default:
          return <NotificationsIcon />;
      }
    })();

    return isAiGenerated ? (
      <Badge
        badgeContent={<SmartIcon sx={{ fontSize: 12 }} />}
        color="secondary"
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        {baseIcon}
      </Badge>
    ) : baseIcon;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const unreadCount = alerts.filter(a => !a.isRead).length;
  const criticalCount = alerts.filter(a => a.severity === 'critical' && !a.isRead).length;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          <NotificationsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Smart Alert System
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip 
            label={`${unreadCount} unread`}
            color="primary"
            variant="outlined"
          />
          {criticalCount > 0 && (
            <Chip 
              label={`${criticalCount} critical`}
              color="error"
            />
          )}
          <Tooltip title="Alert Settings">
            <IconButton onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Live Smart Alerts
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={isMonitoring}
                      onChange={(e) => setIsMonitoring(e.target.checked)}
                    />
                  }
                  label="Real-time Monitoring"
                />
              </Box>

              {alerts.length === 0 ? (
                <Alert severity="info">
                  No alerts at the moment. AI monitoring is active and will notify you of any issues.
                </Alert>
              ) : (
                <List>
                  <AnimatePresence>
                    {alerts.map((alert, index) => (
                      <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <ListItem
                          sx={{
                            border: 1,
                            borderColor: alert.isRead ? 'divider' : `${getSeverityColor(alert.severity)}.main`,
                            borderRadius: 1,
                            mb: 1,
                            bgcolor: alert.autoResolved ? 'success.light' : alert.isRead ? 'background.paper' : 'action.hover',
                            cursor: 'pointer',
                            '&:hover': { bgcolor: 'action.selected' },
                          }}
                          onClick={() => handleAlertClick(alert)}
                        >
                          <ListItemIcon>
                            {getAlertIcon(alert.type, alert.isAiGenerated)}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <Typography
                                  variant="body1"
                                  fontWeight={alert.isRead ? 'normal' : 'bold'}
                                >
                                  {alert.title}
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                                  {alert.isAiGenerated && (
                                    <Chip
                                      icon={<SmartIcon />}
                                      label="AI"
                                      size="small"
                                      color="secondary"
                                      variant="outlined"
                                    />
                                  )}
                                  <Chip
                                    label={alert.severity}
                                    size="small"
                                    color={getSeverityColor(alert.severity) as any}
                                  />
                                </Box>
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                  {alert.message}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {alert.timestamp.toLocaleString()}
                                  {alert.metadata?.confidence && (
                                    <> • {alert.metadata.confidence}% confidence</>
                                  )}
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alert Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedAlert && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">{selectedAlert.title}</Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {selectedAlert.isAiGenerated && (
                    <Chip icon={<SmartIcon />} label="AI Generated" size="small" color="secondary" />
                  )}
                  <Chip 
                    label={selectedAlert.severity}
                    color={getSeverityColor(selectedAlert.severity) as any}
                    size="small"
                  />
                  <IconButton onClick={() => setDetailsOpen(false)}>
                    <CloseIcon />
                  </IconButton>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedAlert.message}
                  </Typography>
                </Grid>
                
                {selectedAlert.metadata && (
                  <>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" color="text.secondary">
                        Source
                      </Typography>
                      <Typography variant="body2">
                        {selectedAlert.metadata.source}
                      </Typography>
                    </Grid>
                    
                    {selectedAlert.metadata.confidence && (
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" color="text.secondary">
                          AI Confidence
                        </Typography>
                        <Typography variant="body2">
                          {selectedAlert.metadata.confidence}%
                        </Typography>
                      </Grid>
                    )}
                    
                    {selectedAlert.metadata.affectedSystems && (
                      <Grid item xs={12}>
                        <Typography variant="subtitle2" color="text.secondary">
                          Affected Systems
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          {selectedAlert.metadata.affectedSystems.map((system) => (
                            <Chip key={system} label={system} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </Grid>
                    )}
                  </>
                )}
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body2">
                    {selectedAlert.timestamp.toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              {selectedAlert.actions?.map((action, index) => (
                <Button
                  key={index}
                  variant={action.variant || 'text'}
                  onClick={() => {
                    action.action();
                    setDetailsOpen(false);
                  }}
                >
                  {action.label}
                </Button>
              ))}
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Smart Alert Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={smartAlertsEnabled}
                  onChange={(e) => setSmartAlertsEnabled(e.target.checked)}
                />
              }
              label="Enable Smart AI Alerts"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={autoResolveEnabled}
                  onChange={(e) => setAutoResolveEnabled(e.target.checked)}
                />
              }
              label="Enable Auto-Resolution"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={isMonitoring}
                  onChange={(e) => setIsMonitoring(e.target.checked)}
                />
              }
              label="Real-time Monitoring"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Manual Alert Generation */}
      <Zoom in={smartAlertsEnabled}>
        <Fab
          color="secondary"
          aria-label="generate alert"
          sx={{ position: 'fixed', bottom: 80, right: 24 }}
          onClick={generateSmartAlerts}
        >
          <AutoFixIcon />
        </Fab>
      </Zoom>
    </Box>
  );
};

export { SmartAlerts };
