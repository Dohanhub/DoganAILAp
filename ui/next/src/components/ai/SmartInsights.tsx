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
  Button,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Psychology as AiIcon,
  TrendingUp as TrendingUpIcon,
  Lightbulb as InsightIcon,
  Warning as WarningIcon,
  AutoFixHigh as AutoFixIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  SmartToy as SmartIcon,
  Analytics as AnalyticsIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface SmartInsight {
  id: string;
  type: 'trend' | 'anomaly' | 'prediction' | 'recommendation';
  title: string;
  description: string;
  confidence: number;
  impact: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  actionable: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface AIRecommendation {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimated_impact: string;
  implementation_effort: string;
  category: string;
}

const SmartInsights: React.FC = () => {
  const [insights, setInsights] = useState<SmartInsight[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [aiProcessing, setAiProcessing] = useState(false);

  // Generate smart insights using AI-like analysis
  const generateInsights = () => {
    setIsLoading(true);
    setTimeout(() => {
      const newInsights: SmartInsight[] = [
        {
          id: '1',
          type: 'trend',
          title: 'Compliance Score Trending Upward',
          description: 'Your overall compliance score has increased by 12% over the last 30 days, primarily due to improved NCA policy adherence.',
          confidence: 95,
          impact: 'high',
          category: 'Performance',
          actionable: true,
          action: {
            label: 'View Details',
            onClick: () => console.log('View trend details'),
          },
        },
        {
          id: '2',
          type: 'anomaly',
          title: 'Unusual API Response Times Detected',
          description: 'Response times for compliance evaluations have increased by 340% during peak hours (2-4 PM). This may indicate resource constraints.',
          confidence: 87,
          impact: 'medium',
          category: 'Performance',
          actionable: true,
          action: {
            label: 'Optimize',
            onClick: () => console.log('Optimize performance'),
          },
        },
        {
          id: '3',
          type: 'prediction',
          title: 'Potential SAMA Compliance Gap',
          description: 'AI models predict a 78% probability of SAMA banking regulation violations next month based on current vendor configurations.',
          confidence: 78,
          impact: 'critical',
          category: 'Risk Management',
          actionable: true,
          action: {
            label: 'Prevent',
            onClick: () => console.log('Prevent violation'),
          },
        },
        {
          id: '4',
          type: 'recommendation',
          title: 'Automate Routine Checks',
          description: 'Implementation of automated compliance checking could reduce manual effort by 65% and improve accuracy by 23%.',
          confidence: 92,
          impact: 'high',
          category: 'Efficiency',
          actionable: true,
          action: {
            label: 'Implement',
            onClick: () => console.log('Implement automation'),
          },
        },
      ];

      const newRecommendations: AIRecommendation[] = [
        {
          id: '1',
          title: 'Implement Real-time Monitoring',
          description: 'Deploy continuous compliance monitoring for IBM and Oracle integrations to catch violations before they become critical.',
          priority: 'high',
          estimated_impact: '+15% compliance score',
          implementation_effort: '2-3 weeks',
          category: 'Monitoring',
        },
        {
          id: '2',
          title: 'Optimize Database Queries',
          description: 'Database performance analysis reveals 23 slow queries affecting compliance report generation.',
          priority: 'medium',
          estimated_impact: '+45% faster reports',
          implementation_effort: '1 week',
          category: 'Performance',
        },
        {
          id: '3',
          title: 'Update Security Protocols',
          description: 'Current authentication methods are 78% effective. Implementing MFA could increase security by 95%.',
          priority: 'urgent',
          estimated_impact: '+95% security effectiveness',
          implementation_effort: '3-5 days',
          category: 'Security',
        },
      ];

      setInsights(newInsights);
      setRecommendations(newRecommendations);
      setIsLoading(false);
    }, 2000);
  };

  useEffect(() => {
    generateInsights();
  }, []);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'trend':
        return <TrendingUpIcon color="success" />;
      case 'anomaly':
        return <WarningIcon color="warning" />;
      case 'prediction':
        return <AnalyticsIcon color="info" />;
      case 'recommendation':
        return <InsightIcon color="primary" />;
      default:
        return <SmartIcon color="action" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
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

  const runAIAnalysis = () => {
    setAiProcessing(true);
    setTimeout(() => {
      generateInsights();
      setAiProcessing(false);
    }, 3000);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          <AiIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Smart AI Insights
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Run AI Analysis">
            <IconButton 
              onClick={runAIAnalysis} 
              disabled={aiProcessing || isLoading}
              color="primary"
            >
              <AutoFixIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh Insights">
            <IconButton 
              onClick={generateInsights} 
              disabled={isLoading}
              color="primary"
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {aiProcessing && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={20} />
            <Typography>AI is analyzing your data for new insights...</Typography>
          </Box>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Smart Insights */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <InsightIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI-Generated Insights
              </Typography>

              {isLoading ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {Array.from({ length: 3 }).map((_, index) => (
                    <Box key={index} sx={{ p: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                      <LinearProgress sx={{ mb: 1 }} />
                      <Typography variant="body2" color="text.secondary">
                        Analyzing data patterns...
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <List>
                  <AnimatePresence>
                    {insights.map((insight, index) => (
                      <motion.div
                        key={insight.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <ListItem 
                          sx={{ 
                            border: 1, 
                            borderColor: 'divider', 
                            borderRadius: 1, 
                            mb: 2,
                            bgcolor: 'background.paper',
                          }}
                        >
                          <ListItemIcon>
                            {getInsightIcon(insight.type)}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <Typography variant="h6">{insight.title}</Typography>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  <Chip 
                                    label={`${insight.confidence}% confidence`}
                                    size="small"
                                    color="info"
                                    variant="outlined"
                                  />
                                  <Chip 
                                    label={insight.impact}
                                    size="small"
                                    color={getImpactColor(insight.impact) as any}
                                  />
                                </Box>
                              </Box>
                            }
                            secondary={
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="body2" sx={{ mb: 1 }}>
                                  {insight.description}
                                </Typography>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <Chip 
                                    label={insight.category}
                                    size="small"
                                    variant="outlined"
                                  />
                                  {insight.actionable && insight.action && (
                                    <Button 
                                      size="small" 
                                      variant="outlined"
                                      onClick={insight.action.onClick}
                                    >
                                      {insight.action.label}
                                    </Button>
                                  )}
                                </Box>
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

        {/* AI Recommendations */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Recommendations
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {recommendations.map((rec, index) => (
                  <motion.div
                    key={rec.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Accordion>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ width: '100%' }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="body1" fontWeight="medium">
                              {rec.title}
                            </Typography>
                            <Chip 
                              label={rec.priority}
                              size="small"
                              color={getPriorityColor(rec.priority) as any}
                            />
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            {rec.category}
                          </Typography>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Box>
                          <Typography variant="body2" sx={{ mb: 2 }}>
                            {rec.description}
                          </Typography>
                          
                          <Grid container spacing={1}>
                            <Grid item xs={12}>
                              <Typography variant="caption" color="text.secondary">
                                Estimated Impact
                              </Typography>
                              <Typography variant="body2" fontWeight="medium">
                                {rec.estimated_impact}
                              </Typography>
                            </Grid>
                            <Grid item xs={12}>
                              <Typography variant="caption" color="text.secondary">
                                Implementation Time
                              </Typography>
                              <Typography variant="body2" fontWeight="medium">
                                {rec.implementation_effort}
                              </Typography>
                            </Grid>
                          </Grid>

                          <Button 
                            variant="contained" 
                            size="small" 
                            sx={{ mt: 2 }}
                            fullWidth
                          >
                            Implement Recommendation
                          </Button>
                        </Box>
                      </AccordionDetails>
                    </Accordion>
                  </motion.div>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export { SmartInsights };
