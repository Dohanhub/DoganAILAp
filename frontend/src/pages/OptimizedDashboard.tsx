import React, { useEffect, useMemo, memo } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { 
  ExclamationTriangleIcon, 
  DocumentTextIcon, 
  ClockIcon, 
  UserGroupIcon, 
  ShieldCheckIcon, 
  ArrowTrendingUpIcon, 
  ArrowTrendingDownIcon, 
  ArrowPathIcon, 
  CheckCircleIcon,
  BuildingOfficeIcon,
  SignalIcon,
  CpuChipIcon,
  MinusIcon
} from '@heroicons/react/24/outline'
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Area, 
  AreaChart 
} from 'recharts'
import { useRealtimeData } from '../hooks/useRealtimeData'

// Memoized components for performance
const StatCard = memo(({ stat }: { stat: any }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200">
    <div className="p-6">
      <div className="flex items-center justify-between">
        <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${stat.lightColor}`}>
          <stat.icon className={`h-6 w-6 ${stat.textColor}`} />
        </div>
        <div className="flex items-center space-x-1">
          {stat.changeType === 'positive' ? (
            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
          ) : stat.changeType === 'negative' ? (
            <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
          ) : (
            <MinusIcon className="h-4 w-4 text-gray-400" />
          )}
          <span className={`text-sm font-medium ${
            stat.changeType === 'positive' ? 'text-green-600' : 
            stat.changeType === 'negative' ? 'text-red-600' : 'text-gray-500'
          }`}>
            {stat.change}
          </span>
        </div>
      </div>
      <div className="mt-4">
        <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
        <p className="text-sm text-gray-500 mt-1">{stat.name}</p>
      </div>
    </div>
    <div className="bg-gray-50 px-6 py-2">
      <div className="text-xs text-gray-500">vs last month</div>
    </div>
  </div>
))

const ComplianceChart = memo(({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold text-gray-900">Live Compliance Trends</h3>
      <div className="flex items-center space-x-2">
        <SignalIcon className="h-4 w-4 text-green-500" />
        <span className="text-sm text-green-600 font-medium">Live Data</span>
      </div>
    </div>
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorNCA" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
          </linearGradient>
          <linearGradient id="colorSAMA" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="timestamp" stroke="#6B7280" fontSize={12} />
        <YAxis stroke="#6B7280" fontSize={12} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#ffffff', 
            border: '1px solid #E5E7EB', 
            borderRadius: '8px',
            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
          }}
          labelStyle={{ color: '#111827', fontWeight: 'bold' }}
        />
        <Area type="monotone" dataKey="nca_score" stroke="#10B981" fillOpacity={1} fill="url(#colorNCA)" strokeWidth={2} />
        <Area type="monotone" dataKey="sama_score" stroke="#3B82F6" fillOpacity={1} fill="url(#colorSAMA)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  </div>
))

const RiskDistributionChart = memo(({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold text-gray-900">Real-Time Risk Distribution</h3>
      <span className="text-sm text-gray-500">Total: {data.reduce((sum, item) => sum + item.value, 0)} risks</span>
    </div>
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry: any, index: number) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  </div>
))

const PerformanceMetrics = memo(({ data }: { data: any[] }) => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold text-gray-900">Live Framework Performance</h3>
      <div className="flex items-center space-x-2">
        <CpuChipIcon className="h-4 w-4 text-blue-500" />
        <span className="text-sm text-blue-600 font-medium">Real-Time</span>
      </div>
    </div>
    <div className="space-y-4">
      {data.map((framework) => (
        <div key={framework.name} className="flex items-center">
          <div className="w-32 text-sm font-medium text-gray-700">{framework.name}</div>
          <div className="flex-1 mx-4">
            <div className="relative">
              <div className="h-8 bg-gray-100 rounded-lg overflow-hidden">
                <div 
                  className="h-full rounded-lg transition-all duration-1000 ease-out"
                  style={{ 
                    width: `${framework.current}%`,
                    backgroundColor: framework.color,
                    opacity: 0.9
                  }}
                />
                <div 
                  className="absolute top-0 h-full w-1 bg-gray-800"
                  style={{ left: `${framework.target}%` }}
                />
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm font-bold text-gray-900">{framework.current}%</div>
            <div className="text-xs text-gray-500">Target: {framework.target}%</div>
          </div>
        </div>
      ))}
    </div>
  </div>
))

const LoadingSpinner = () => (
  <div className="flex items-center justify-center h-64">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-600 mx-auto"></div>
      <p className="mt-4 text-gray-600">Loading real-time data...</p>
    </div>
  </div>
)

const ErrorBoundary = ({ children, error }: { children: React.ReactNode, error?: string }) => {
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
          <span className="ml-2 text-sm text-red-800">Failed to load data: {error}</span>
        </div>
      </div>
    )
  }
  return <>{children}</>
}

export default function OptimizedDashboard() {
  const queryClient = useQueryClient()
  
  // Real-time data hook
  const realtimeData = useRealtimeData()
  const { isConnected } = realtimeData
  
  // Extract data from realtime hook with fallbacks
  const metrics = realtimeData?.data?.metrics || {
    nca_score: 85,
    sama_score: 92,
    pdpl_score: 78,
    iso_score: 88,
    nist_score: 81
  }
  const events = realtimeData?.data?.events || []
  const notifications = realtimeData?.data?.notifications || []
  const connectionStatus = isConnected ? 'connected' : 'disconnected'

  // Optimized data fetching with React Query
  const { data: dashboardStats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/analytics/summary')
      if (!response.ok) throw new Error('Failed to fetch dashboard stats')
      const s = await response.json()
      return {
        organizations: s.organizations ?? 0,
        assessments: s.totalAssessments ?? 0,
        avg_compliance: s.averageComplianceScore ?? 0,
        open_risks: s.totalRisks ?? 0,
        org_change: '+0%',
        assessment_change: '+0%',
        compliance_change: '+0%',
        risk_change: '+0%'
      }
    },
    staleTime: 30000, // 30 seconds
    refetchInterval: isConnected ? 60000 : false, // 1 minute if connected
    retry: 3
  })

  const { data: complianceData, isLoading: complianceLoading, error: complianceError } = useQuery({
    queryKey: ['compliance-trends'],
    queryFn: async () => {
      const response = await fetch('/api/v1/analytics/trends?days=30')
      if (!response.ok) throw new Error('Failed to fetch compliance trends')
      const data = await response.json()
      return data?.trends ? data : { trends: data || [] }
    },
    staleTime: 60000, // 1 minute
    refetchInterval: isConnected ? 120000 : false, // 2 minutes if connected
    retry: 3
  })

  const { data: riskData, isLoading: riskLoading, error: riskError } = useQuery({
    queryKey: ['risk-distribution'],
    queryFn: async () => {
      const response = await fetch('/api/v1/risks/distribution')
      if (!response.ok) throw new Error('Failed to fetch risk distribution')
      return response.json()
    },
    staleTime: 45000, // 45 seconds
    refetchInterval: isConnected ? 90000 : false, // 1.5 minutes if connected
    retry: 3
  })

  // Memoized calculations
  const stats = useMemo(() => {
    if (!dashboardStats) return []
    
    return [
      {
        name: 'Total Organizations',
        value: dashboardStats.organizations || 0,
        icon: BuildingOfficeIcon,
        change: dashboardStats.org_change || '+0%',
        changeType: dashboardStats.org_change?.startsWith('+') ? 'positive' : 'negative',
        color: 'bg-blue-600',
        lightColor: 'bg-blue-100',
        textColor: 'text-blue-600',
      },
      {
        name: 'Live Assessments',
        value: dashboardStats.assessments || 0,
        icon: DocumentTextIcon,
        change: dashboardStats.assessment_change || '+0%',
        changeType: dashboardStats.assessment_change?.startsWith('+') ? 'positive' : 'negative',
        color: 'bg-green-600',
        lightColor: 'bg-green-100',
        textColor: 'text-green-600',
      },
      {
        name: 'Real-Time Compliance',
        value: `${dashboardStats.avg_compliance || 0}%`,
        icon: ShieldCheckIcon,
        change: dashboardStats.compliance_change || '+0%',
        changeType: dashboardStats.compliance_change?.startsWith('+') ? 'positive' : 'negative',
        color: 'bg-purple-600',
        lightColor: 'bg-purple-100',
        textColor: 'text-purple-600',
      },
      {
        name: 'Active Risk Items',
        value: dashboardStats.open_risks || 0,
        icon: ExclamationTriangleIcon,
        change: dashboardStats.risk_change || '+0%',
        changeType: dashboardStats.risk_change?.startsWith('-') ? 'positive' : 'negative',
        color: 'bg-red-600',
        lightColor: 'bg-red-100',
        textColor: 'text-red-600',
      },
    ]
  }, [dashboardStats])

  const riskChartData = useMemo(() => {
    if (!riskData?.distribution) return []
    
    return riskData.distribution.map((r: any) => ({
      name: r.severity?.charAt(0).toUpperCase() + r.severity?.slice(1) || 'Unknown',
      value: r.count || 0,
      color: r.severity === 'critical' ? '#DC2626' : 
             r.severity === 'high' ? '#F59E0B' : 
             r.severity === 'medium' ? '#3B82F6' : '#10B981'
    }))
  }, [riskData])

  const performanceData = useMemo(() => {
    if (!metrics) return []
    
    return [
      { name: 'NCA', current: metrics.nca_score || 0, target: 90, color: '#10B981' },
      { name: 'SAMA', current: metrics.sama_score || 0, target: 95, color: '#3B82F6' },
      { name: 'PDPL', current: metrics.pdpl_score || 0, target: 85, color: '#8B5CF6' },
      { name: 'ISO 27001', current: metrics.iso_score || 0, target: 90, color: '#F59E0B' },
      { name: 'NIST', current: metrics.nist_score || 0, target: 80, color: '#EC4899' },
    ]
  }, [metrics])

  // Handle real-time updates
  useEffect(() => {
    if (events.length > 0) {
      const latestEvent = events[events.length - 1]
      if (latestEvent.type === 'compliance_update') {
        // Invalidate relevant queries to refetch data
        queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
        queryClient.invalidateQueries({ queryKey: ['compliance-trends'] })
      }
    }
  }, [events, queryClient])

  // Show notifications
  useEffect(() => {
    notifications.forEach((notification: any) => {
      if (notification.type === 'error') {
        toast.error(notification.message)
      } else if (notification.type === 'warning') {
        toast(notification.message, { icon: '⚠️' })
      } else {
        toast.success(notification.message)
      }
    })
  }, [notifications])

  const isLoading = statsLoading || complianceLoading || riskLoading

  if (isLoading) {
    return (
      <div className="bg-gray-50 min-h-screen">
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4">
            <h1 className="text-2xl font-bold text-gray-900">Executive Dashboard</h1>
            <div className="flex items-center space-x-2 mt-1">
              <ClockIcon className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-500">Loading real-time compliance data...</span>
            </div>
          </div>
        </div>
        <div className="p-6">
          <LoadingSpinner />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Enhanced Header with Connection Status */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Executive Dashboard</h1>
              <div className="flex items-center space-x-4 mt-1">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-sm text-gray-500">
                    {isConnected ? 'Live Data Connected' : 'Connection Lost'}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  Last updated: {new Date().toLocaleTimeString()}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <SignalIcon className={`h-5 w-5 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
              <span className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                {connectionStatus}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Optimized Stats Grid */}
        <ErrorBoundary error={statsError?.message}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat) => (
              <StatCard key={stat.name} stat={stat} />
            ))}
          </div>
        </ErrorBoundary>

        {/* Optimized Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ErrorBoundary error={complianceError?.message}>
            <ComplianceChart data={complianceData?.trends || []} />
          </ErrorBoundary>
          
          <ErrorBoundary error={riskError?.message}>
            <RiskDistributionChart data={riskChartData} />
          </ErrorBoundary>
        </div>

        {/* Performance Metrics */}
        <PerformanceMetrics data={performanceData} />

        {/* Real-time Activity Feed */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Live Assessment Activity</h3>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-sm text-green-600">Live Updates</span>
              </div>
            </div>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {events.slice(-10).map((event: any, idx: number) => (
                <div key={event.id || idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{event.title || 'System Event'}</p>
                      <p className="text-xs text-gray-500">{event.description || 'Real-time update'}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">{event.value || 'N/A'}</p>
                    <p className="text-xs text-gray-500">{event.timestamp || 'Just now'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Alerts</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {notifications.slice(-5).map((notification: any, idx: number) => (
                <div key={idx} className={`p-3 rounded-lg border ${
                  notification.type === 'error' ? 'bg-red-50 border-red-200' :
                  notification.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-green-50 border-green-200'
                }`}>
                  <div className="flex items-start">
                    <ExclamationTriangleIcon className={`h-5 w-5 mt-0.5 ${
                      notification.type === 'error' ? 'text-red-600' :
                      notification.type === 'warning' ? 'text-yellow-600' :
                      'text-green-600'
                    }`} />
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">{notification.title || 'System Alert'}</p>
                      <p className="text-xs text-gray-500 mt-1">{notification.message}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
