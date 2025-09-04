'use client';

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Chip,
  Skeleton,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { motion } from 'framer-motion';
// import { useTranslation } from 'react-i18next';

interface PerformanceChartsProps {
  data: any;
}

const PerformanceCharts: React.FC<PerformanceChartsProps> = ({ data }) => {
  // const { t } = useTranslation();
  const t = (key: string) => key; // Fallback translation function

  // Generate mock performance data if not provided
  const generateMockData = () => {
    const now = new Date();
    const timePoints = Array.from({ length: 24 }, (_, i) => {
      const time = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000);
      return {
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        timestamp: time.toISOString(),
        responseTime: Math.floor(Math.random() * 200) + 100,
        throughput: Math.floor(Math.random() * 500) + 300,
        cpu: Math.floor(Math.random() * 40) + 30,
        memory: Math.floor(Math.random() * 30) + 40,
        activeUsers: Math.floor(Math.random() * 50) + 25,
        errorRate: Math.random() * 2,
      };
    });
    return timePoints;
  };

  const performanceData = data?.performanceHistory || generateMockData();

  const complianceBreakdown = [
    { name: 'Compliant', value: 342, color: '#4caf50' },
    { name: 'Warnings', value: 47, color: '#ff9800' },
    { name: 'Critical', value: 12, color: '#f44336' },
    { name: 'Pending', value: 23, color: '#9e9e9e' },
  ];

  const systemLoad = [
    { name: 'API Gateway', load: 65, status: 'good' },
    { name: 'Database', load: 45, status: 'good' },
    { name: 'Auth Service', load: 78, status: 'warning' },
    { name: 'Compliance Engine', load: 56, status: 'good' },
    { name: 'File System', load: 34, status: 'good' },
  ];

  const getLoadColor = (load: number) => {
    if (load > 80) return '#f44336';
    if (load > 60) return '#ff9800';
    return '#4caf50';
  };

  const COLORS = ['#4caf50', '#ff9800', '#f44336', '#9e9e9e'];

  if (!data && !performanceData) {
    return (
      <Grid container spacing={3}>
        {Array.from({ length: 4 }).map((_, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Skeleton variant="text" height={32} sx={{ mb: 2 }} />
                <Skeleton variant="rectangular" height={200} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Response Time & Throughput */}
      <Grid item xs={12} lg={8}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Performance Overview (Last 24 Hours)
              </Typography>
              
              <Box sx={{ height: 300, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time" 
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis yAxisId="left" orientation="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip 
                      formatter={(value: any, name: string) => [
                        `${value}${name === 'responseTime' ? 'ms' : ' req/s'}`,
                        name === 'responseTime' ? 'Response Time' : 'Throughput'
                      ]}
                    />
                    <Legend />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="responseTime" 
                      stroke="#1976d2" 
                      strokeWidth={2}
                      name="Response Time (ms)"
                      dot={false}
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="throughput" 
                      stroke="#2e7d32" 
                      strokeWidth={2}
                      name="Throughput (req/s)"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>

              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Avg Response
                    </Typography>
                    <Typography variant="h6">
                      {Math.floor(performanceData.reduce((acc: number, item: any) => acc + item.responseTime, 0) / performanceData.length)}ms
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Peak Throughput
                    </Typography>
                    <Typography variant="h6">
                      {Math.max(...performanceData.map((item: any) => item.throughput))} req/s
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Avg Error Rate
                    </Typography>
                    <Typography variant="h6" color="error.main">
                      {(performanceData.reduce((acc: number, item: any) => acc + item.errorRate, 0) / performanceData.length).toFixed(2)}%
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper sx={{ p: 1, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Active Users
                    </Typography>
                    <Typography variant="h6" color="success.main">
                      {Math.floor(performanceData.reduce((acc: number, item: any) => acc + item.activeUsers, 0) / performanceData.length)}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>

      {/* Compliance Breakdown */}
      <Grid item xs={12} lg={4}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Compliance Status
              </Typography>
              
              <Box sx={{ height: 200, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={complianceBreakdown}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {complianceBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any) => [`${value} items`, 'Count']} />
                  </PieChart>
                </ResponsiveContainer>
              </Box>

              <Box sx={{ mt: 2 }}>
                {complianceBreakdown.map((item, index) => (
                  <Box key={item.name} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: COLORS[index],
                        }}
                      />
                      <Typography variant="body2">{item.name}</Typography>
                    </Box>
                    <Typography variant="body2" fontWeight="bold">
                      {item.value}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>

      {/* System Load */}
      <Grid item xs={12} lg={6}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                System Load
              </Typography>
              
              <Box sx={{ height: 250, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={systemLoad} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis dataKey="name" type="category" width={100} />
                    <Tooltip formatter={(value: any) => [`${value}%`, 'Load']} />
                    <Bar dataKey="load" fill="#1976d2" radius={[0, 4, 4, 0]}>
                      {systemLoad.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getLoadColor(entry.load)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>

      {/* Resource Usage */}
      <Grid item xs={12} lg={6}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Resource Usage (Last 24h)
              </Typography>
              
              <Box sx={{ height: 250, mt: 2 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time" 
                      tick={{ fontSize: 12 }}
                      interval="preserveStartEnd"
                    />
                    <YAxis domain={[0, 100]} />
                    <Tooltip formatter={(value: any, name: string) => [`${value}%`, name.toUpperCase()]} />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="cpu" 
                      stackId="1" 
                      stroke="#1976d2" 
                      fill="#1976d2" 
                      fillOpacity={0.6}
                      name="CPU"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="memory" 
                      stackId="1" 
                      stroke="#2e7d32" 
                      fill="#2e7d32" 
                      fillOpacity={0.6}
                      name="Memory"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Grid>
    </Grid>
  );
};

export { PerformanceCharts };
