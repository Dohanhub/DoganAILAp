import React, { useEffect, useState } from 'react'
import { analyticsService } from '../services/api'
import {
  ChartBarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  BuildingOfficeIcon,
  ShieldCheckIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  MinusIcon,
} from '@heroicons/react/24/outline'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [statsData, setStatsData] = useState<any>(null)

  useEffect(() => {
    loadDashboard()
  }, [])

  const loadDashboard = async () => {
    try {
      // Load dashboard stats
      const statsResponse = await fetch('http://localhost:8000/api/dashboard/stats')
      const stats = await statsResponse.json()
      setStatsData(stats)
      
      // Load analytics data
      const analyticsResponse = await analyticsService.dashboard()
      setDashboardData(analyticsResponse.data)
    } catch (error) {
      console.error('Dashboard error:', error)
      // Use fallback data if API fails
      setStatsData({
        organizations: 5,
        assessments: 12,
        open_risks: 8,
        frameworks: 5,
        avg_compliance: 75,
        risk_distribution: [
          { severity: 'critical', count: 2 },
          { severity: 'high', count: 3 },
          { severity: 'medium', count: 3 }
        ]
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const stats = [
    {
      name: 'Total Organizations',
      value: statsData?.organizations || 0,
      icon: BuildingOfficeIcon,
      change: '+12%',
      changeType: 'positive',
      color: 'bg-blue-600',
      lightColor: 'bg-blue-100',
      textColor: 'text-blue-600',
    },
    {
      name: 'Compliance Assessments',
      value: statsData?.assessments || 0,
      icon: DocumentTextIcon,
      change: '+23%',
      changeType: 'positive',
      color: 'bg-green-600',
      lightColor: 'bg-green-100',
      textColor: 'text-green-600',
    },
    {
      name: 'Average Compliance',
      value: `${statsData?.avg_compliance || 0}%`,
      icon: ShieldCheckIcon,
      change: '+5%',
      changeType: 'positive',
      color: 'bg-purple-600',
      lightColor: 'bg-purple-100',
      textColor: 'text-purple-600',
    },
    {
      name: 'Open Risk Items',
      value: statsData?.open_risks || 0,
      icon: ExclamationTriangleIcon,
      change: '-8%',
      changeType: 'negative',
      color: 'bg-red-600',
      lightColor: 'bg-red-100',
      textColor: 'text-red-600',
    },
  ]

  const riskData = statsData?.risk_distribution?.map((r: any) => ({
    name: r.severity?.charAt(0).toUpperCase() + r.severity?.slice(1) || 'Unknown',
    value: r.count || 0,
    color: r.severity === 'critical' ? '#DC2626' : r.severity === 'high' ? '#F59E0B' : r.severity === 'medium' ? '#3B82F6' : '#10B981'
  })) || []

  // Sample compliance trend data
  const complianceTrend = [
    { month: 'Jan', NCA: 65, SAMA: 70, PDPL: 60, ISO27001: 75 },
    { month: 'Feb', NCA: 68, SAMA: 72, PDPL: 65, ISO27001: 77 },
    { month: 'Mar', NCA: 70, SAMA: 75, PDPL: 68, ISO27001: 80 },
    { month: 'Apr', NCA: 75, SAMA: 78, PDPL: 72, ISO27001: 82 },
    { month: 'May', NCA: 78, SAMA: 80, PDPL: 75, ISO27001: 85 },
    { month: 'Jun', NCA: 82, SAMA: 85, PDPL: 78, ISO27001: 88 },
  ]

  const performanceData = [
    { name: 'NCA', current: 82, target: 90, color: '#10B981' },
    { name: 'SAMA', current: 85, target: 95, color: '#3B82F6' },
    { name: 'PDPL', current: 78, target: 85, color: '#8B5CF6' },
    { name: 'ISO 27001', current: 88, target: 90, color: '#F59E0B' },
    { name: 'NIST', current: 75, target: 80, color: '#EC4899' },
  ]

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Executive Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Real-time compliance and risk analytics</p>
        </div>
      </div>

      <div className="p-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat) => (
            <div key={stat.name} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${stat.lightColor}`}>
                    <stat.icon className={`h-6 w-6 ${stat.textColor}`} />
                  </div>
                  <div className="flex items-center space-x-1">
                    {stat.changeType === 'positive' ? (
                      <ArrowUpIcon className="h-4 w-4 text-green-500" />
                    ) : stat.changeType === 'negative' ? (
                      <ArrowDownIcon className="h-4 w-4 text-red-500" />
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
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Compliance Trend Chart */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Compliance Trends</h3>
              <select className="text-sm border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500">
                <option>Last 6 months</option>
                <option>Last year</option>
                <option>All time</option>
              </select>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={complianceTrend}>
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
                <XAxis dataKey="month" stroke="#6B7280" fontSize={12} />
                <YAxis stroke="#6B7280" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #E5E7EB', borderRadius: '8px' }}
                  labelStyle={{ color: '#111827', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="NCA" stroke="#10B981" fillOpacity={1} fill="url(#colorNCA)" strokeWidth={2} />
                <Area type="monotone" dataKey="SAMA" stroke="#3B82F6" fillOpacity={1} fill="url(#colorSAMA)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Risk Distribution */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Risk Distribution</h3>
              <span className="text-sm text-gray-500">Total: {statsData?.open_risks || 0} risks</span>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Framework Performance */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Framework Performance</h3>
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">View Details →</button>
          </div>
          <div className="space-y-4">
            {performanceData.map((framework) => (
              <div key={framework.name} className="flex items-center">
                <div className="w-32 text-sm font-medium text-gray-700">{framework.name}</div>
                <div className="flex-1 mx-4">
                  <div className="relative">
                    <div className="h-8 bg-gray-100 rounded-lg overflow-hidden">
                      <div 
                        className="h-full rounded-lg transition-all duration-500"
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

        {/* Recent Activity */}
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Assessments</h3>
            <div className="space-y-4">
              {[
                { org: 'Saudi National Bank', framework: 'SAMA', score: 92, date: '2 hours ago', status: 'completed' },
                { org: 'Al Rajhi Corporation', framework: 'NCA', score: 88, date: '5 hours ago', status: 'completed' },
                { org: 'SABIC', framework: 'ISO 27001', score: 85, date: '1 day ago', status: 'completed' },
                { org: 'Saudi Telecom', framework: 'PDPL', score: 78, date: '2 days ago', status: 'in-progress' },
              ].map((assessment, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <DocumentTextIcon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{assessment.org}</p>
                      <p className="text-xs text-gray-500">{assessment.framework} Assessment</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">{assessment.score}%</p>
                    <p className="text-xs text-gray-500">{assessment.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Critical Alerts</h3>
            <div className="space-y-3">
              {[
                { title: 'SAMA Compliance Update', type: 'warning', time: '1 hour ago' },
                { title: 'New NCA Guidelines', type: 'info', time: '3 hours ago' },
                { title: 'Risk Assessment Due', type: 'error', time: '1 day ago' },
              ].map((alert, idx) => (
                <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start">
                    <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mt-0.5" />
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                      <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
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