'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Skeleton,
} from '@mui/material';
import {
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Refresh as RefreshIcon,
  Assignment as AssignmentIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend } from 'recharts';
// import { useTranslation } from 'react-i18next';

import { useComplianceData } from '@/hooks/useComplianceData';
import { formatNumber, formatPercentage } from '@/utils/formatters';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'primary' | 'success' | 'warning' | 'error';
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  isLoading?: boolean;
  onClick?: () => void;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color,
  trend,
  isLoading,
  onClick,
}) => {
  const cardVariants = {
    hover: { 
      scale: 1.02,
      boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
      transition: { duration: 0.2 }
    },
    tap: { scale: 0.98 }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Skeleton variant="text" height={24} sx={{ mb: 1 }} />
          <Skeleton variant="text" height={32} sx={{ mb: 1 }} />
          <Skeleton variant="text" height={20} width="60%" />
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      variants={cardVariants}
      whileHover="hover"
      whileTap="tap"
      style={{ height: '100%' }}
    >
      <Card 
        sx={{ 
          height: '100%', 
          cursor: onClick ? 'pointer' : 'default',
          borderLeft: 4,
          borderLeftColor: `${color}.main`,
          position: 'relative',
          overflow: 'hidden',
        }}
        onClick={onClick}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                bgcolor: `${color}.light`,
                color: `${color}.contrastText`,
                mr: 2,
              }}
            >
              {icon}
            </Box>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {title}
              </Typography>
              <Typography variant="h4" fontWeight="bold" color={`${color}.main`}>
                {typeof value === 'number' ? formatNumber(value) : value}
              </Typography>
            </Box>
          </Box>

          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              {subtitle}
            </Typography>
          )}

          {trend && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {trend.direction === 'up' ? (
                <TrendingUpIcon color="success" fontSize="small" />
              ) : (
                <TrendingDownIcon color="error" fontSize="small" />
              )}
              <Typography
                variant="body2"
                color={trend.direction === 'up' ? 'success.main' : 'error.main'}
                fontWeight="medium"
              >
                {trend.value > 0 ? '+' : ''}{formatPercentage(trend.value)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                from last period
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

interface ComplianceScore {
  score: number;
  label: string;
  color: string;
}

const ComplianceScoreChart: React.FC<{ data: ComplianceScore[] }> = ({ data }) => {
  const COLORS = ['#4caf50', '#ff9800', '#f44336', '#9e9e9e'];

  return (
    <Card sx={{ height: 300 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Compliance Score Distribution
        </Typography>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={40}
              outerRadius={80}
              paddingAngle={5}
              dataKey="score"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <RechartsTooltip 
              formatter={(value: any) => [formatNumber(value), 'Score']}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

const ComplianceTrendChart: React.FC<{ data: any[] }> = ({ data }) => (
  <Card sx={{ height: 300 }}>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Compliance Trend (Last 7 Days)
      </Typography>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <RechartsTooltip 
            formatter={(value: any) => [formatPercentage(value), 'Compliance %']}
          />
          <Legend />
          <Bar dataKey="compliance" fill="#1976d2" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </CardContent>
  );
};

export const ComplianceMetrics: React.FC = () => {
  // const { t } = useTranslation();
  const t = (key: string) => {
    const translations: {[key: string]: string} = {
      'dashboard.complianceMetrics': 'Compliance Metrics',
      'dashboard.refresh': 'Refresh',
      'metrics.totalCompliance': 'Total Compliance',
      'metrics.criticalIssues': 'Critical Issues',
      'metrics.warningItems': 'Warning Items',
      'metrics.passedControls': 'Passed Controls',
      'dashboard.recentActivities': 'Recent Activities',
      'dashboard.noRecentActivities': 'No recent activities',
    };
    return translations[key] || key;
  };
  const { 
    data: complianceData, 
    isLoading, 
    refetch,
    isRefetching 
  } = useComplianceData();
  
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null);

  const handleRefresh = () => {
    refetch();
  };

  const handleMetricClick = (metricId: string) => {
    setSelectedMetric(metricId);
  };

  if (isLoading) {
    return (
      <Grid container spacing={3}>
        {Array.from({ length: 6 }).map((_, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <MetricCard
              title=""
              value=""
              icon={<SecurityIcon />}
              color="primary"
              isLoading
            />
          </Grid>
        ))}
      </Grid>
    );
  }

  const metrics = complianceData?.metrics || {};
  const trends = complianceData?.trends || [];
  const distribution = complianceData?.distribution || [];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="bold">
          {t('dashboard.complianceMetrics')}
        </Typography>
        <Tooltip title={t('dashboard.refresh')}>
          <IconButton onClick={handleRefresh} disabled={isRefetching}>
            <motion.div
              animate={{ rotate: isRefetching ? 360 : 0 }}
              transition={{ duration: 1, repeat: isRefetching ? Infinity : 0 }}
            >
              <RefreshIcon />
            </motion.div>
          </IconButton>
        </Tooltip>
      </Box>

      {/* Main Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title={t('metrics.totalCompliance')}
            value={formatPercentage(metrics.totalCompliance || 0)}
            subtitle={`${metrics.compliantItems || 0} of ${metrics.totalItems || 0} requirements`}
            icon={<SecurityIcon />}
            color="primary"
            trend={{
              value: metrics.complianceTrend || 0,
              direction: (metrics.complianceTrend || 0) >= 0 ? 'up' : 'down'
            }}
            onClick={() => handleMetricClick('compliance')}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title={t('metrics.criticalIssues')}
            value={metrics.criticalIssues || 0}
            subtitle="Requiring immediate attention"
            icon={<ErrorIcon />}
            color="error"
            trend={{
              value: metrics.criticalTrend || 0,
              direction: (metrics.criticalTrend || 0) <= 0 ? 'up' : 'down'
            }}
            onClick={() => handleMetricClick('critical')}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title={t('metrics.warningItems')}
            value={metrics.warningItems || 0}
            subtitle="Potential compliance gaps"
            icon={<WarningIcon />}
            color="warning"
            trend={{
              value: metrics.warningTrend || 0,
              direction: (metrics.warningTrend || 0) <= 0 ? 'up' : 'down'
            }}
            onClick={() => handleMetricClick('warnings')}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title={t('metrics.passedControls')}
            value={metrics.passedControls || 0}
            subtitle="Successfully validated"
            icon={<CheckCircleIcon />}
            color="success"
            trend={{
              value: metrics.passedTrend || 0,
              direction: (metrics.passedTrend || 0) >= 0 ? 'up' : 'down'
            }}
            onClick={() => handleMetricClick('passed')}
          />
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <ComplianceScoreChart data={distribution} />
        </Grid>
        <Grid item xs={12} md={6}>
          <ComplianceTrendChart data={trends} />
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AssignmentIcon />
            {t('dashboard.recentActivities')}
          </Typography>
          
          <List>
            <AnimatePresence>
              {(complianceData?.recentActivities || []).map((activity: any, index: number) => (
                <motion.div
                  key={activity.id || index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <ListItem>
                    <ListItemIcon>
                      {activity.type === 'success' && <CheckCircleIcon color="success" />}
                      {activity.type === 'warning' && <WarningIcon color="warning" />}
                      {activity.type === 'error' && <ErrorIcon color="error" />}
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.title}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            {activity.description}
                          </Typography>
                          <Chip 
                            label={activity.timestamp} 
                            size="small" 
                            variant="outlined" 
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>
          </List>
          
          {(!complianceData?.recentActivities || complianceData.recentActivities.length === 0) && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body2" color="text.secondary">
                {t('dashboard.noRecentActivities')}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
