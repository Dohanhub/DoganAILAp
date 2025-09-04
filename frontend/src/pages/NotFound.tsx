/**
 * NotFound Page - 404 error page
 */

import React from 'react'
import { Link } from 'react-router-dom'
import { HomeIcon, ArrowLeftIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full text-center">
        <div className="mb-8">
          <div className="mx-auto w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center mb-6">
            <MagnifyingGlassIcon className="w-12 h-12 text-gray-400" />
          </div>
          <h1 className="text-6xl font-bold text-gray-900 mb-2">404</h1>
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
          <p className="text-gray-600 mb-8">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="space-y-4">
          <Link to="/dashboard">
            <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              <HomeIcon className="w-4 h-4" />
              Go to Dashboard
            </button>
          </Link>
          
          <button 
            className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            onClick={() => window.history.back()}
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Go Back
          </button>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Need help? Contact our{' '}
            <Link to="/support" className="text-blue-600 hover:text-blue-800 underline">
              support team
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default NotFound
