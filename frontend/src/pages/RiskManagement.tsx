/**
 * RiskManagement Page - Risk assessment and management
 */

import React from 'react'
import { useRisks } from '../hooks/useAuth'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { 
  PlusIcon, 
  ExclamationTriangleIcon, 
  ArrowTrendingUpIcon, 
  ShieldCheckIcon, 
  EyeIcon 
} from '@heroicons/react/24/outline'

const RiskManagement: React.FC = () => {
  const { data: risks, isLoading, error } = useRisks()

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
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Risks</h3>
        <p className="text-gray-500">Unable to load risk data. Please try again.</p>
      </div>
    )
  }

  const getRiskSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Management</h1>
          <p className="text-gray-600 mt-1">
            Monitor and manage organizational risks
          </p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <PlusIcon className="h-4 w-4" />
          Add Risk
        </button>
      </div>

      {/* Risk Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Risks</p>
              <p className="text-2xl font-bold">{risks?.length || 0}</p>
            </div>
            <ShieldCheckIcon className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Critical</p>
              <p className="text-2xl font-bold text-red-600">
                {risks?.filter((r: any) => r.severity === 'critical').length || 0}
              </p>
            </div>
            <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High</p>
              <p className="text-2xl font-bold text-orange-600">
                {risks?.filter((r: any) => r.severity === 'high').length || 0}
              </p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-orange-500" />
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Mitigated</p>
              <p className="text-2xl font-bold text-green-600">
                {risks?.filter((r: any) => r.status === 'mitigated').length || 0}
              </p>
            </div>
            <ShieldCheckIcon className="h-8 w-8 text-green-500" />
          </div>
        </div>
      </div>

      {/* Risks List */}
      <div className="space-y-4">
        {risks?.map((risk: any) => (
          <div key={risk.id} className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{risk.title}</h3>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 text-xs rounded-full ${getRiskSeverityColor(risk.severity)}`}>
                  {risk.severity}
                </span>
                <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800 border">
                  {risk.status}
                </span>
              </div>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              {risk.description}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Probability</span>
                <p className="font-medium">{risk.probability || 'N/A'}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Impact</span>
                <p className="font-medium">{risk.impact || 'N/A'}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500 uppercase tracking-wide">Owner</span>
                <p className="font-medium">{risk.owner || 'Unassigned'}</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-500">
                Last updated: {risk.updated_at ? new Date(risk.updated_at).toLocaleDateString() : 'N/A'}
              </div>
              <button className="inline-flex items-center gap-1 px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
                <EyeIcon className="h-3 w-3" />
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {(!risks || risks.length === 0) && (
        <div className="text-center py-12">
          <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Risks Found</h3>
          <p className="text-gray-500 mb-4">
            Start by identifying and documenting organizational risks.
          </p>
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="h-4 w-4" />
            Add Risk
          </button>
        </div>
      )}
    </div>
  )
}

export default RiskManagement
