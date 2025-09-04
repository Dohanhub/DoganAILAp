/**
 * ComplianceFrameworks Page - Compliance frameworks management
 */

import React from 'react'
import { useFrameworks } from '../hooks/useAuth'
import { LoadingSpinner } from '../components/ui/LoadingSpinner'
import { 
  PlusIcon, 
  ShieldCheckIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'

const ComplianceFrameworks: React.FC = () => {
  const { data: frameworks, isLoading, error } = useFrameworks()

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
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Frameworks</h3>
        <p className="text-gray-500">Unable to load compliance frameworks. Please try again.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Compliance Frameworks</h1>
          <p className="text-gray-600 mt-1">
            Manage and monitor your compliance frameworks
          </p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <PlusIcon className="h-4 w-4" />
          Add Framework
        </button>
      </div>

      {/* Frameworks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {frameworks?.map((framework: any) => (
          <div key={framework.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <ShieldCheckIcon className="h-8 w-8 text-blue-600" />
              <span className={`px-2 py-1 text-xs rounded-full ${
                framework.status === 'active' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {framework.status}
              </span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{framework.name}</h3>
            <p className="text-gray-600 text-sm mb-4">
              {framework.description}
            </p>
            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Controls:</span>
                <span className="font-medium">{framework.controls_count || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Compliance:</span>
                <div className="flex items-center gap-1">
                  <CheckCircleIcon className="h-3 w-3 text-green-500" />
                  <span className="font-medium">{framework.compliance_rate || 0}%</span>
                </div>
              </div>
            </div>
            <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50">
              View Details
            </button>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {(!frameworks || frameworks.length === 0) && (
        <div className="text-center py-12">
          <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Frameworks Found</h3>
          <p className="text-gray-500 mb-4">
            Get started by adding your first compliance framework.
          </p>
          <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            <PlusIcon className="h-4 w-4" />
            Add Framework
          </button>
        </div>
      )}
    </div>
  )
}

export default ComplianceFrameworks
