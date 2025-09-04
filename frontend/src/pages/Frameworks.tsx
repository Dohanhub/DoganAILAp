import React, { useState, useEffect } from 'react'
import { frameworkService } from '../services/api'
import { DocumentTextIcon, ShieldCheckIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Frameworks() {
  const [frameworks, setFrameworks] = useState<any[]>([])
  const [selectedFramework, setSelectedFramework] = useState<any>(null)
  const [controls, setControls] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [controlsLoading, setControlsLoading] = useState(false)

  useEffect(() => {
    loadFrameworks()
  }, [])

  const loadFrameworks = async () => {
    try {
      const response = await frameworkService.list()
      setFrameworks(response.data)
    } catch (error) {
      toast.error('Failed to load frameworks')
    } finally {
      setLoading(false)
    }
  }

  const loadControls = async (frameworkCode: string) => {
    setControlsLoading(true)
    try {
      const response = await frameworkService.getControls(frameworkCode)
      setControls(response.data.controls)
    } catch (error) {
      toast.error('Failed to load controls')
    } finally {
      setControlsLoading(false)
    }
  }

  const handleFrameworkSelect = (framework: any) => {
    setSelectedFramework(framework)
    loadControls(framework.code)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Compliance Frameworks</h1>
        <p className="mt-2 text-sm text-gray-700">
          Saudi and international compliance frameworks with detailed controls
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center mt-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Frameworks List */}
          <div className="lg:col-span-1">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Frameworks</h2>
            <div className="space-y-3">
              {frameworks.map((framework) => (
                <div
                  key={framework.id}
                  onClick={() => handleFrameworkSelect(framework)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedFramework?.id === framework.id
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-start">
                    <ShieldCheckIcon className="h-5 w-5 text-gray-400 mt-1 mr-3" />
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-gray-900">
                        {framework.code} {framework.is_saudi && '🇸🇦'}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">{framework.name}</p>
                      {framework.name_arabic && (
                        <p className="text-sm text-gray-500 mt-1" dir="rtl">{framework.name_arabic}</p>
                      )}
                      <div className="mt-2 flex items-center space-x-3">
                        <span className="text-xs text-gray-500">
                          {framework.controls_count} controls
                        </span>
                        {framework.is_mandatory && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            Mandatory
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-400 mt-2">
                        Authority: {framework.authority}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Controls Detail */}
          <div className="lg:col-span-2">
            {selectedFramework ? (
              <>
                <div className="mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {selectedFramework.name} Controls
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Detailed control requirements and implementation guidance
                  </p>
                </div>
                {controlsLoading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {controls.length > 0 ? (
                      controls.map((control) => (
                        <div key={control.id} className="bg-white shadow rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center">
                                <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                                <h4 className="text-sm font-semibold text-gray-900">
                                  {control.control_id}: {control.title}
                                </h4>
                              </div>
                              {control.title_arabic && (
                                <p className="text-sm text-gray-600 mt-1" dir="rtl">
                                  {control.title_arabic}
                                </p>
                              )}
                              <p className="text-sm text-gray-600 mt-2">
                                {control.description}
                              </p>
                              <div className="mt-3 flex items-center space-x-4">
                                {control.category && (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                    {control.category}
                                  </span>
                                )}
                                {control.priority && (
                                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                                    control.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                                    control.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                                    control.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {control.priority} Priority
                                  </span>
                                )}
                                {control.control_type && (
                                  <span className="text-xs text-gray-500">
                                    Type: {control.control_type}
                                  </span>
                                )}
                                {control.automation_possible && (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                    Automatable
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        No controls available for this framework
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white shadow rounded-lg p-12 text-center">
                <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-semibold text-gray-900">Select a Framework</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Choose a framework from the list to view its controls
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}