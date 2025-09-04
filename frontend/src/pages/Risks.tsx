import React, { useState, useEffect } from 'react'
import { riskService, organizationService } from '../services/api'
import { ExclamationTriangleIcon, PlusIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Risks() {
  const [risks, setRisks] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    organization_id: '',
    title: '',
    severity: 'medium',
    likelihood: 'medium',
    description: '',
    category: 'operational'
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [risksRes, orgsRes] = await Promise.all([
        riskService.list(),
        organizationService.list()
      ])
      setRisks(risksRes.data)
      setOrganizations(orgsRes.data)
    } catch (error) {
      toast.error('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await riskService.create({
        organization_id: parseInt(formData.organization_id),
        title: formData.title,
        severity: formData.severity,
        likelihood: formData.likelihood,
        description: formData.description,
        category: formData.category
      })
      toast.success('Risk created successfully')
      setShowCreateModal(false)
      loadData()
      setFormData({
        organization_id: '',
        title: '',
        severity: 'medium',
        likelihood: 'medium',
        description: '',
        category: 'operational'
      })
    } catch (error) {
      toast.error('Failed to create risk')
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (severity: string) => {
    const sizeClass = severity === 'critical' ? 'h-8 w-8' : 'h-6 w-6'
    const colorClass = severity === 'critical' || severity === 'high' ? 'text-red-500' : 'text-yellow-500'
    return <ExclamationTriangleIcon className={`${sizeClass} ${colorClass}`} />
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Risk Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Identify, assess, and manage compliance risks
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
          >
            <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
            Add Risk
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center mt-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      ) : (
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {risks.length > 0 ? (
            risks.map((risk) => (
              <div key={risk.id} className={`bg-white shadow rounded-lg p-6 border-l-4 ${getSeverityColor(risk.severity)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(risk.severity)}
                      <h3 className="text-lg font-medium text-gray-900">{risk.title}</h3>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">{risk.organization}</p>
                    <div className="mt-3 flex items-center space-x-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(risk.severity)}`}>
                        {risk.severity}
                      </span>
                      <span className="text-xs text-gray-500">
                        Likelihood: {risk.likelihood}
                      </span>
                    </div>
                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700">
                        Risk Score: <span className="font-bold">{risk.risk_score}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Category: {risk.category}
                      </p>
                    </div>
                    <div className="mt-4 flex items-center justify-between">
                      <span className={`text-xs ${risk.status === 'open' ? 'text-red-600' : 'text-green-600'}`}>
                        Status: {risk.status}
                      </span>
                      {risk.mitigation_deadline && (
                        <span className="text-xs text-gray-500">
                          Due: {new Date(risk.mitigation_deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full bg-white shadow rounded-lg p-12 text-center">
              <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold text-gray-900">No risks identified</h3>
              <p className="mt-1 text-sm text-gray-500">
                Start by identifying potential compliance risks.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
                >
                  <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
                  Add First Risk
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={() => setShowCreateModal(false)} />
            <div className="relative bg-white rounded-lg max-w-md w-full p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Risk</h3>
              <form onSubmit={handleCreate}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Organization</label>
                    <select
                      required
                      value={formData.organization_id}
                      onChange={(e) => setFormData({ ...formData, organization_id: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    >
                      <option value="">Select organization</option>
                      {organizations.map((org) => (
                        <option key={org.id} value={org.id}>
                          {org.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Risk Title</label>
                    <input
                      type="text"
                      required
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Severity</label>
                      <select
                        value={formData.severity}
                        onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                      >
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                        <option value="minimal">Minimal</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Likelihood</label>
                      <select
                        value={formData.likelihood}
                        onChange={(e) => setFormData({ ...formData, likelihood: e.target.value })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                      >
                        <option value="very_high">Very High</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                        <option value="very_low">Very Low</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Category</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    >
                      <option value="strategic">Strategic</option>
                      <option value="operational">Operational</option>
                      <option value="financial">Financial</option>
                      <option value="compliance">Compliance</option>
                      <option value="reputational">Reputational</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Description</label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={3}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    />
                  </div>
                </div>
                <div className="mt-6 flex gap-3">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700"
                  >
                    Create
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="flex-1 bg-gray-200 text-gray-700 rounded-md px-4 py-2 hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}