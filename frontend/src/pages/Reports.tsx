import React, { useState } from 'react'
import { organizationService, frameworkService, reportService } from '../services/api'
import { DocumentArrowDownIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Reports() {
  const [generating, setGenerating] = useState(false)
  const [formData, setFormData] = useState({
    organization_id: '',
    report_type: 'executive',
    framework_codes: [] as string[],
    format: 'pdf'
  })

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.organization_id) {
      toast.error('Please select an organization')
      return
    }
    
    setGenerating(true)
    try {
      const response = await reportService.generate({
        organization_id: parseInt(formData.organization_id),
        report_type: formData.report_type,
        framework_codes: formData.framework_codes,
        format: formData.format
      })
      toast.success('Report generated successfully!')
      
      // Auto-download
      const downloadResponse = await reportService.download(response.data.id)
      const blob = new Blob([downloadResponse.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${response.data.id}.${formData.format}`
      a.click()
    } catch (error) {
      toast.error('Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  const reportTypes = [
    {
      id: 'executive',
      name: 'Executive Summary',
      description: 'High-level overview for leadership and board members',
      icon: '📊'
    },
    {
      id: 'detailed',
      name: 'Detailed Compliance Report',
      description: 'Comprehensive analysis with all control assessments',
      icon: '📋'
    },
    {
      id: 'gap_analysis',
      name: 'Gap Analysis',
      description: 'Identify compliance gaps and remediation priorities',
      icon: '🔍'
    },
    {
      id: 'benchmark',
      name: 'Industry Benchmark',
      description: 'Compare performance against industry standards',
      icon: '📈'
    }
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="mt-2 text-sm text-gray-700">
          Generate compliance reports and analytics
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Report Generator */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Report</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Organization</label>
              <select
                required
                value={formData.organization_id}
                onChange={(e) => setFormData({ ...formData, organization_id: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
              >
                <option value="">Select organization</option>
                <option value="1">Sample Organization</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
              <div className="space-y-2">
                {reportTypes.map((type) => (
                  <label key={type.id} className="flex items-start cursor-pointer">
                    <input
                      type="radio"
                      name="report_type"
                      value={type.id}
                      checked={formData.report_type === type.id}
                      onChange={(e) => setFormData({ ...formData, report_type: e.target.value })}
                      className="mt-1 mr-3"
                    />
                    <div>
                      <div className="flex items-center">
                        <span className="mr-2">{type.icon}</span>
                        <span className="text-sm font-medium text-gray-900">{type.name}</span>
                      </div>
                      <p className="text-xs text-gray-500">{type.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Format</label>
              <select
                value={formData.format}
                onChange={(e) => setFormData({ ...formData, format: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
              >
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="json">JSON</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={generating}
              className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                <>
                  <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
                  Generate Report
                </>
              )}
            </button>
          </form>
        </div>

        {/* Recent Reports */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Reports</h2>
          <div className="space-y-3">
            <div className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">
                    Executive Report - Q4 2024
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Generated on Dec 15, 2024 • PDF
                  </p>
                </div>
                <button className="text-green-600 hover:text-green-700">
                  <DocumentArrowDownIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">
                    NCA Compliance Assessment
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Generated on Dec 10, 2024 • Excel
                  </p>
                </div>
                <button className="text-green-600 hover:text-green-700">
                  <DocumentArrowDownIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
            <div className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">
                    SAMA Framework Gap Analysis
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Generated on Dec 5, 2024 • PDF
                  </p>
                </div>
                <button className="text-green-600 hover:text-green-700">
                  <DocumentArrowDownIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Templates */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Report Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
            <ChartBarIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-gray-900">Regulatory Submission</h3>
            <p className="text-xs text-gray-500 mt-1">Format for NCA/SAMA submissions</p>
          </div>
          <div className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
            <ChartBarIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-gray-900">Board Presentation</h3>
            <p className="text-xs text-gray-500 mt-1">Executive dashboard format</p>
          </div>
          <div className="border rounded-lg p-4 text-center hover:shadow-md transition-shadow">
            <ChartBarIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <h3 className="text-sm font-medium text-gray-900">Audit Report</h3>
            <p className="text-xs text-gray-500 mt-1">Detailed audit findings format</p>
          </div>
        </div>
      </div>
    </div>
  )
}