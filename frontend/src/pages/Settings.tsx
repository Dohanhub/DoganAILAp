import React, { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { UserCircleIcon, BellIcon, ShieldCheckIcon, GlobeAltIcon, KeyIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Settings() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    department: '',
    phone: '',
    language: 'en',
    notifications: {
      email: true,
      sms: false,
      app: true
    },
    security: {
      two_factor: false,
      session_timeout: '60'
    }
  })

  const handleSave = (section: string) => {
    toast.success(`${section} settings saved successfully`)
  }

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserCircleIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'language', name: 'Language & Region', icon: GlobeAltIcon },
    { id: 'api', name: 'API Keys', icon: KeyIcon }
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-sm text-gray-700">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Tabs */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  activeTab === tab.id
                    ? 'bg-green-50 text-green-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <tab.icon className="mr-3 h-5 w-5" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="bg-white shadow rounded-lg p-6">
            {activeTab === 'profile' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Full Name</label>
                    <input
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Department</label>
                    <input
                      type="text"
                      value={formData.department}
                      onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                      placeholder="IT, Finance, Legal, etc."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone</label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                      placeholder="+966 5XX XXX XXXX"
                    />
                  </div>
                  <button
                    onClick={() => handleSave('Profile')}
                    className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700"
                  >
                    Save Profile
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Email Notifications</h3>
                      <p className="text-sm text-gray-500">Receive compliance alerts via email</p>
                    </div>
                    <button
                      onClick={() => setFormData({
                        ...formData,
                        notifications: { ...formData.notifications, email: !formData.notifications.email }
                      })}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                        formData.notifications.email ? 'bg-green-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          formData.notifications.email ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">SMS Notifications</h3>
                      <p className="text-sm text-gray-500">Critical alerts via SMS</p>
                    </div>
                    <button
                      onClick={() => setFormData({
                        ...formData,
                        notifications: { ...formData.notifications, sms: !formData.notifications.sms }
                      })}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                        formData.notifications.sms ? 'bg-green-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          formData.notifications.sms ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">In-App Notifications</h3>
                      <p className="text-sm text-gray-500">Show notifications in the application</p>
                    </div>
                    <button
                      onClick={() => setFormData({
                        ...formData,
                        notifications: { ...formData.notifications, app: !formData.notifications.app }
                      })}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                        formData.notifications.app ? 'bg-green-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          formData.notifications.app ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  <button
                    onClick={() => handleSave('Notification')}
                    className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700"
                  >
                    Save Preferences
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h3>
                      <p className="text-sm text-gray-500">Add an extra layer of security</p>
                    </div>
                    <button
                      onClick={() => setFormData({
                        ...formData,
                        security: { ...formData.security, two_factor: !formData.security.two_factor }
                      })}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                        formData.security.two_factor ? 'bg-green-600' : 'bg-gray-200'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                          formData.security.two_factor ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Session Timeout (minutes)</label>
                    <select
                      value={formData.security.session_timeout}
                      onChange={(e) => setFormData({
                        ...formData,
                        security: { ...formData.security, session_timeout: e.target.value }
                      })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    >
                      <option value="15">15 minutes</option>
                      <option value="30">30 minutes</option>
                      <option value="60">1 hour</option>
                      <option value="120">2 hours</option>
                    </select>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Change Password</h3>
                    <button className="bg-gray-600 text-white rounded-md px-4 py-2 hover:bg-gray-700">
                      Change Password
                    </button>
                  </div>
                  <button
                    onClick={() => handleSave('Security')}
                    className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700"
                  >
                    Save Security Settings
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'language' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Language & Region</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Language</label>
                    <select
                      value={formData.language}
                      onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                    >
                      <option value="en">English</option>
                      <option value="ar">العربية (Arabic)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Time Zone</label>
                    <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm">
                      <option>Asia/Riyadh (GMT+3)</option>
                      <option>Asia/Dubai (GMT+4)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Date Format</label>
                    <select className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm">
                      <option>DD/MM/YYYY</option>
                      <option>MM/DD/YYYY</option>
                      <option>YYYY-MM-DD</option>
                    </select>
                  </div>
                  <button
                    onClick={() => handleSave('Language')}
                    className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700"
                  >
                    Save Language Settings
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'api' && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">API Keys</h2>
                <p className="text-sm text-gray-500 mb-4">
                  Manage API keys for integrations and automated compliance checks
                </p>
                <div className="space-y-4">
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-gray-900">Production API Key</h3>
                        <p className="text-xs text-gray-500 mt-1">Created on Dec 1, 2024</p>
                      </div>
                      <button className="text-red-600 hover:text-red-700 text-sm">
                        Revoke
                      </button>
                    </div>
                    <div className="mt-2">
                      <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                        sk_live_xxxx...xxxx
                      </code>
                    </div>
                  </div>
                  <button className="bg-green-600 text-white rounded-md px-4 py-2 hover:bg-green-700">
                    Generate New API Key
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}