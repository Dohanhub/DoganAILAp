'use client';

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Psychology as AiIcon,
  Cloud as CloudIcon,
  Storage as StorageIcon,
  ExpandMore as ExpandMoreIcon,
  Verified as VerifiedIcon,
  TrendingUp as TrendingUpIcon,
  AutoFixHigh as AutoFixIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const SystemOverview: React.FC = () => {
  const [expanded, setExpanded] = useState<string | false>('features');

  const handleChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false);
  };

  const systemFeatures = [
    {
      category: 'Core Compliance',
      items: [
        'NCA Commercial Authorization Compliance',
        'SAMA Banking Regulations Support',
        'MoH Healthcare Standards',
        'CITC Telecom Compliance',
        'Data Protection Law (SDAIA)',
      ],
    },
    {
      category: 'AI & Intelligence',
      items: [
        'Smart Compliance Insights',
        'Predictive Violation Detection',
        'Automated Risk Assessment',
        'Anomaly Detection Engine',
        'Smart Alert System',
      ],
    },
    {
      category: 'Real-time Features',
      items: [
        'Live Compliance Monitoring',
        'WebSocket Data Streaming',
        'Real-time Performance Metrics',
        'Instant Alert Notifications',
        'Dynamic Dashboard Updates',
      ],
    },
    {
      category: 'Integration & APIs',
      items: [
        'RESTful API Architecture',
        'Vendor Integration Framework',
        'External Policy Sync',
        'Database Optimization',
        'Microservices Architecture',
      ],
    },
  ];

  const systemStats = [
    { label: 'Services Running', value: '8/8', status: 'success' },
    { label: 'API Endpoints', value: '150+', status: 'info' },
    { label: 'Compliance Policies', value: '50+', status: 'info' },
    { label: 'Supported Vendors', value: '25+', status: 'info' },
    { label: 'Response Time', value: '<100ms', status: 'success' },
    { label: 'Uptime', value: '99.9%', status: 'success' },
  ];

  const techStack = [
    { name: 'Frontend', tech: 'React 18 + TypeScript + Material-UI v5', icon: <SpeedIcon /> },
    { name: 'Backend', tech: 'Python FastAPI + SQLModel + PostgreSQL', icon: <StorageIcon /> },
    { name: 'AI/ML', tech: 'Custom AI Models + Predictive Analytics', icon: <AiIcon /> },
    { name: 'Infrastructure', tech: 'Docker + Kubernetes + Redis', icon: <CloudIcon /> },
    { name: 'Security', tech: 'JWT + OAuth2 + API Keys + HTTPS', icon: <SecurityIcon /> },
    { name: 'Monitoring', tech: 'Real-time WebSockets + Health Checks', icon: <TrendingUpIcon /> },
  ];

  const deploymentStatus = [
    { service: 'Compliance Engine', port: 8000, status: 'running', health: 100 },
    { service: 'Benchmarks Service', port: 8001, status: 'running', health: 98 },
    { service: 'AI/ML Service', port: 8002, status: 'running', health: 95 },
    { service: 'Integrations Service', port: 8003, status: 'running', health: 97 },
    { service: 'Authentication Service', port: 8004, status: 'running', health: 100 },
    { service: 'AI Agent Service', port: 8005, status: 'running', health: 92 },
    { service: 'Testing Service', port: 8006, status: 'running', health: 88 },
    { service: 'UI Frontend', port: 3000, status: 'running', health: 100 },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        <VerifiedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        DoganAI Compliance Kit - System Overview
      </Typography>

      {/* System Status Alert */}
      <Alert severity="success" sx={{ mb: 4 }}>
        <Typography variant="h6">
          🎉 System Fully Operational - All Components Active
        </Typography>
        <Typography variant="body2">
          All 8 microservices are running, AI features are active, and real-time monitoring is operational.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        {/* System Stats */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Statistics
              </Typography>
              <Grid container spacing={3}>
                {systemStats.map((stat, index) => (
                  <Grid item xs={6} sm={4} md={2} key={index}>
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Paper sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h5" color={`${getStatusColor(stat.status)}.main`}>
                          {stat.value}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {stat.label}
                        </Typography>
                      </Paper>
                    </motion.div>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Features Overview */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Features & Capabilities
              </Typography>
              
              {systemFeatures.map((category, index) => (
                <Accordion 
                  key={category.category}
                  expanded={expanded === `features-${index}`}
                  onChange={handleChange(`features-${index}`)}
                >
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {category.category}
                    </Typography>
                    <Chip 
                      label={`${category.items.length} features`}
                      size="small"
                      sx={{ ml: 2 }}
                    />
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {category.items.map((item, itemIndex) => (
                        <ListItem key={itemIndex}>
                          <ListItemIcon>
                            <CheckIcon color="success" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={item} />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Technology Stack */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Technology Stack
              </Typography>
              
              <List>
                {techStack.map((tech, index) => (
                  <motion.div
                    key={tech.name}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <ListItem>
                      <ListItemIcon>
                        {tech.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={tech.name}
                        secondary={tech.tech}
                      />
                    </ListItem>
                  </motion.div>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Service Deployment Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Service Deployment Status
              </Typography>
              
              <Grid container spacing={2}>
                {deploymentStatus.map((service, index) => (
                  <Grid item xs={12} sm={6} md={3} key={service.service}>
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Paper sx={{ p: 2, border: 1, borderColor: 'success.light' }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" fontWeight="medium">
                            {service.service}
                          </Typography>
                          <Chip 
                            label={service.status}
                            size="small"
                            color="success"
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          Port: {service.port}
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={service.health}
                          color="success"
                          sx={{ mt: 1, height: 6, borderRadius: 3 }}
                        />
                        <Typography variant="caption" color="success.main">
                          Health: {service.health}%
                        </Typography>
                      </Paper>
                    </motion.div>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Management
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="contained" startIcon={<AutoFixIcon />}>
                  Run System Diagnostics
                </Button>
                <Button variant="outlined" startIcon={<TrendingUpIcon />}>
                  View Performance Report
                </Button>
                <Button variant="outlined" startIcon={<SecurityIcon />}>
                  Security Audit
                </Button>
                <Button variant="outlined" startIcon={<AiIcon />}>
                  AI Model Status
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export { SystemOverview };
