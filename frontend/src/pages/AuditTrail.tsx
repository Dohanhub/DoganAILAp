/**
 * AuditTrail Page - System audit trail and activity logs
 */

import React, { useState } from 'react'
import { 
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  UserIcon,
  CalendarIcon,
  EyeIcon
} from '@heroicons/react/24/outline'
import { useAuditLogs } from '../hooks/useAuth'
import LoadingSpinner from '../components/ui/LoadingSpinner'

interface AuditLog {
  id: string
  action: string
  user_name?: string
  user_id: string
  timestamp: string
  entity_type: string
  entity_id: string
  details?: string
  ip_address?: string
}

interface AuditLogsResponse {
  logs: AuditLog[]
  total: number
}

const AuditTrail: React.FC = () => {
  const [filters, setFilters] = useState({
    user_id: '',
    action: '',
    start_date: '',
    end_date: '',
  })

  const { data: auditLogs, isLoading, error } = useAuditLogs(filters)

  const getActionColor = (action: string) => {
    switch (action?.toLowerCase()) {
      case 'create': return 'bg-green-100 text-green-800'
      case 'update': return 'bg-yellow-100 text-yellow-800'
      case 'delete': return 'bg-red-100 text-red-800'
      case 'login': return 'bg-blue-100 text-blue-800'
      case 'logout': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Audit Trail</h3>
        <p className="text-gray-500">Unable to load audit logs. Please try again.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
          <p className="text-gray-600 mt-1">
            Track all system activities and user actions
          </p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <ArrowDownTrayIcon className="h-4 w-4" />
          Export Logs
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <FunnelIcon className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              Search User
            </label>
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by user..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={filters.user_id}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFilters({ ...filters, user_id: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              Action Type
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.action}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFilters({ ...filters, action: e.target.value })}
            >
              <option value="">All actions</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
              <option value="login">Login</option>
              <option value="logout">Logout</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              Start Date
            </label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.start_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFilters({ ...filters, start_date: e.target.value })}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              End Date
            </label>
            <input
              type="date"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.end_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFilters({ ...filters, end_date: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* Audit Logs */}
      <div className="space-y-3">
        {(auditLogs as AuditLogsResponse)?.logs?.map((log: AuditLog) => (
          <div key={log.id} className="bg-white rounded-lg shadow hover:shadow-sm transition-shadow p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${getActionColor(log.action)}`}>
                    {log.action}
                  </span>
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <UserIcon className="h-3 w-3" />
                    {log.user_name || log.user_id}
                  </div>
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <CalendarIcon className="h-3 w-3" />
                    {formatTimestamp(log.timestamp)}
                  </div>
                </div>
                <p className="text-gray-900 font-medium mb-1">
                  {log.entity_type}: {log.entity_id}
                </p>
                {log.details && (
                  <p className="text-sm text-gray-600">
                    {log.details}
                  </p>
                )}
                {log.ip_address && (
                  <div className="mt-2 text-xs text-gray-500">
                    IP: {log.ip_address}
                  </div>
                )}
              </div>
              <button className="p-1 text-gray-400 hover:text-gray-600">
                <EyeIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {(!(auditLogs as AuditLogsResponse)?.logs || (auditLogs as AuditLogsResponse).logs.length === 0) && (
        <div className="text-center py-12">
          <ClipboardDocumentListIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Audit Logs Found</h3>
          <p className="text-gray-500">
            No audit trail entries match your current filters.
          </p>
        </div>
      )}

      {/* Pagination */}
      {(auditLogs as AuditLogsResponse)?.total && (auditLogs as AuditLogsResponse).total > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {(auditLogs as AuditLogsResponse).logs?.length || 0} of {(auditLogs as AuditLogsResponse).total} entries
          </p>
          <div className="flex items-center gap-2">
            <button 
              className="px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-400 cursor-not-allowed"
              disabled
            >
              Previous
            </button>
            <button 
              className="px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-400 cursor-not-allowed"
              disabled
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AuditTrail
