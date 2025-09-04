import React, { useState, useEffect } from 'react'
import { assessmentService, organizationService, frameworkService } from '../services/api'
import { ClipboardDocumentCheckIcon, PlusIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Assessments() {
  const [assessments, setAssessments] = useState<any[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])
  const [frameworks, setFrameworks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    organization_id: '',
    framework_code: '',
    assessment_type: 'initial'
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [assessmentsRes, orgsRes, frameworksRes] = await Promise.all([
        assessmentService.list(),
        organizationService.list(),
        frameworkService.list()
      ])
      setAssessments(assessmentsRes.data)
      setOrganizations(orgsRes.data)
      setFrameworks(frameworksRes.data)
    } catch (error) {
      toast.error('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await assessmentService.create({
        organization_id: parseInt(formData.organization_id),
        framework_code: formData.framework_code,
        assessment_type: formData.assessment_type
      })
      toast.success('Assessment created successfully')
      setShowCreateModal(false)
      loadData()
      setFormData({ organization_id: '', framework_code: '', assessment_type: 'initial' })
    } catch (error) {
      toast.error('Failed to create assessment')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800'
      case 'planned':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-bold text-gray-900">Assessments</h1>
          <p className="mt-2 text-sm text-gray-700">
            Compliance assessments and maturity evaluations
          </p>
        </div>
        <div className="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
          >
            <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
            New Assessment
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center mt-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      ) : (
        <div className="mt-8 grid gap-4">
          {assessments.length > 0 ? (
            assessments.map((assessment) => (
              <div key={assessment.id} className="bg-white shadow rounded-lg p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <ClipboardDocumentCheckIcon className="h-6 w-6 text-gray-400 mt-1" />
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {assessment.framework} Assessment
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {assessment.organization} • {assessment.type}
                      </p>
                      <div className="mt-2 flex items-center space-x-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(assessment.status)}`}>
                          {assessment.status}
                        </span>
                        {assessment.score !== null && (
                          <span className={`text-sm font-semibold ${getScoreColor(assessment.score)}`}>
                            Score: {assessment.score}%
                          </span>
                        )}
                        {assessment.maturity_level && (
                          <span className="text-sm text-gray-500">
                            Maturity: Level {assessment.maturity_level}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">
                      {assessment.assessor}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Started: {new Date(assessment.started_at).toLocaleDateString()}
                    </p>
                    {assessment.completed_at && (
                      <p className="text-xs text-gray-400">
                        Completed: {new Date(assessment.completed_at).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white shadow rounded-lg p-12 text-center">
              <ClipboardDocumentCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-semibold text-gray-900">No assessments</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating a new compliance assessment.
              </p>
              <div className="mt-6">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="inline-flex items-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500"
                >
                  <PlusIcon className="-ml-0.5 mr-1.5 h-5 w-5" />
                  New Assessment
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
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Assessment</h3>
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
                    <label className="block text-sm font-medium text-gray-700">Framework</label>
                    <select
                      required
                      value={formData.framework_code}
                      onChange={(e) => setFormData({ ...formData, framework_code: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    >
                      <option value="">Select framework</option>
                      {frameworks.map((fw) => (
                        <option key={fw.id} value={fw.code}>
                          {fw.name} {fw.is_saudi && '🇸🇦'}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Assessment Type</label>
                    <select
                      value={formData.assessment_type}
                      onChange={(e) => setFormData({ ...formData, assessment_type: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    >
                      <option value="initial">Initial Assessment</option>
                      <option value="periodic">Periodic Review</option>
                      <option value="continuous">Continuous Monitoring</option>
                      <option value="gap_analysis">Gap Analysis</option>
                    </select>
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