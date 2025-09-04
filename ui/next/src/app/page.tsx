'use client';

import { Suspense, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Fab,
  Zoom,
  Alert,
  Skeleton
} from '@mui/material';
import { 
  AnimatedPage, 
  AnimatedCard, 
  StaggerContainer, 
  StaggerItem 
} from '@/components/enhanced/AnimationSystem';
import {
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  Refresh as RefreshIcon,
  Language as LanguageIcon,
  NotificationsActive as NotificationsIcon
} from '@mui/icons-material';

import { MainLayout } from '@/components/layouts/MainLayout';
import { ComplianceMetrics } from '@/components/dashboard/ComplianceMetrics';
import { ComplianceEvaluation } from '@/components/dashboard/ComplianceEvaluation';
import { AuditLogs } from '@/components/dashboard/AuditLogs';
import { RealTimeMonitoring } from '@/components/dashboard/RealTimeMonitoring';
import { PerformanceCharts } from '@/components/dashboard/PerformanceCharts';
import { SystemHealthIndicator } from '@/components/dashboard/SystemHealthIndicator';
import { LanguageSwitch } from '@/components/common/LanguageSwitch';
import { SearchBar } from '@/components/common/SearchBar';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { NotificationCenter } from '@/components/common/NotificationCenter';
import { SmartInsights } from '@/components/ai/SmartInsights';
import { SmartAlerts } from '@/components/advanced/SmartAlerts';
import { SystemOverview } from '@/components/system/SystemOverview';

import { useGlobalStore } from '@/stores/GlobalStore';
import { useHealthCheck } from '@/hooks/useHealthCheck';
import { useRealtimeData } from '@/hooks/useRealtimeData';
// Temporarily disabled i18n
// import { useTranslation } from 'react-i18next';

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  in: { opacity: 1, y: 0 },
  out: { opacity: 0, y: -20 }
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.5
};

interface DashboardTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const DashboardTabs: React.FC<DashboardTabsProps> = ({ activeTab, onTabChange }) => {
  // const { t } = useTranslation();
  
  const tabs = [
    { id: 'overview', label: 'Dashboard Overview', icon: <DashboardIcon /> },
    { id: 'compliance', label: 'Compliance Management', icon: <SecurityIcon /> },
    { id: 'evaluation', label: 'Evaluation Center', icon: <AssessmentIcon /> },
    { id: 'monitoring', label: 'Real-time Monitoring', icon: <TimelineIcon /> },
    { id: 'ai-insights', label: 'AI Insights', icon: <LanguageIcon /> },
    { id: 'smart-alerts', label: 'Smart Alerts', icon: <NotificationsIcon /> },
    { id: 'system', label: 'System Overview', icon: <DashboardIcon /> },
  ];

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
      <Grid container spacing={1}>
        {tabs.map((tab) => (
          <Grid item xs={12} sm={6} md={4} lg={2} key={tab.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                bgcolor: activeTab === tab.id ? 'primary.main' : 'background.paper',
                color: activeTab === tab.id ? 'primary.contrastText' : 'text.primary',
                transition: 'all 0.3s ease',
                transform: activeTab === tab.id ? 'scale(1.02)' : 'scale(1)',
                '&:hover': {
                  transform: 'scale(1.02)',
                  boxShadow: 6
                }
              }}
              onClick={() => onTabChange(tab.id)}
            >
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Box sx={{ mb: 1 }}>{tab.icon}</Box>
                <Typography variant="body2" fontWeight="medium">
                  {tab.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

const LoadingSkeleton: React.FC = () => (
  <Grid container spacing={3}>
    {Array.from({ length: 6 }).map((_, index) => (
      <Grid item xs={12} md={6} lg={4} key={index}>
        <Card>
          <CardContent>
            <Skeleton variant="rectangular" height={120} sx={{ mb: 2 }} />
            <Skeleton variant="text" height={24} sx={{ mb: 1 }} />
            <Skeleton variant="text" height={20} width="60%" />
          </CardContent>
        </Card>
      </Grid>
    ))}
  </Grid>
);

export default function Dashboard() {
  // const { t } = useTranslation();
  const { language, theme } = useGlobalStore();
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  
  const { data: healthData, isLoading: healthLoading, refetch: refetchHealth } = useHealthCheck();
  const { data: realtimeData, isConnected } = useRealtimeData();

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetchHealth();
    setTimeout(() => setRefreshing(false), 1000);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <motion.div
            key="overview"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <SystemHealthIndicator 
                  data={healthData} 
                  isLoading={healthLoading}
                  isConnected={isConnected}
                />
              </Grid>
              
              <Grid item xs={12} lg={8}>
                <ComplianceMetrics />
              </Grid>
              
              <Grid item xs={12} lg={4}>
                <QuickActions />
              </Grid>
              
              <Grid item xs={12}>
                <PerformanceCharts data={realtimeData} />
              </Grid>
            </Grid>
          </motion.div>
        );
        
      case 'compliance':
        return (
          <motion.div
            key="compliance"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <ComplianceEvaluation />
          </motion.div>
        );
        
      case 'evaluation':
        return (
          <motion.div
            key="evaluation"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <AuditLogs />
          </motion.div>
        );
        
      case 'monitoring':
        return (
          <motion.div
            key="monitoring"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <RealTimeMonitoring data={realtimeData} isConnected={isConnected} />
          </motion.div>
        );

      case 'ai-insights':
        return (
          <motion.div
            key="ai-insights"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <SmartInsights />
          </motion.div>
        );

      case 'smart-alerts':
        return (
          <motion.div
            key="smart-alerts"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <SmartAlerts />
          </motion.div>
        );

      case 'system':
        return (
          <motion.div
            key="system"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <SystemOverview />
          </motion.div>
        );
        
      default:
        return null;
    }
  };

  return (
    <MainLayout>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography 
                variant="h3" 
                component="h1" 
                fontWeight="bold"
                sx={{ 
                  background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  mb: 1
                }}
              >
                🇸🇦 DoganAI Compliance Kit
              </Typography>
              <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                World-Class AI-Powered Compliance Management Platform
              </Typography>
              
              {/* Status Indicators */}
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  icon={<SecurityIcon />}
                  label="Security: Active"
                  color="success"
                  variant="outlined"
                />
                <Chip 
                  icon={<NotificationsIcon />}
                  label={`${realtimeData?.notifications || 0} Alerts`}
                  color={realtimeData?.notifications > 0 ? 'warning' : 'default'}
                />
                <Chip 
                  icon={<LanguageIcon />}
                  label={language === 'ar' ? 'العربية' : 'English'}
                  variant="outlined"
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', alignItems: 'center', flexWrap: 'wrap' }}>
                <SearchBar placeholder="Search compliance data..." />
                <LanguageSwitch />
                <NotificationCenter />
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* Connection Status Alert */}
        {!isConnected && (
          <Alert 
            severity="warning" 
            sx={{ mb: 3 }}
            action={
              <LanguageSwitch />
            }
          >
            Real-time connection lost. Some features may be limited.
          </Alert>
        )}

        {/* Dashboard Tabs */}
        <DashboardTabs activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Main Content */}
        <Suspense fallback={<LoadingSkeleton />}>
          <AnimatePresence mode="wait">
            {renderTabContent()}
          </AnimatePresence>
        </Suspense>

        {/* Floating Action Button */}
        <Zoom in={!refreshing}>
          <Fab
            color="primary"
            aria-label="Refresh Dashboard"
            sx={{ position: 'fixed', bottom: 24, right: 24 }}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <motion.div
              animate={{ rotate: refreshing ? 360 : 0 }}
              transition={{ duration: 1, repeat: refreshing ? Infinity : 0 }}
            >
              <RefreshIcon />
            </motion.div>
          </Fab>
        </Zoom>

        {/* Loading Indicator */}
        {refreshing && (
          <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
            <LinearProgress />
          </Box>
        )}
      </Container>
    </MainLayout>
  );
}
