import React, { useState } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import {
  HomeIcon,
  BuildingOfficeIcon,
  ClipboardDocumentCheckIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline'
import { useAuthStore } from '../store/authStore'
import clsx from 'clsx'
import { useEffect } from 'react'
import { features } from '../features/registry'

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [theme, setTheme] = useState('light') // light/dark theme
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  // Accessibility: close sidebar on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') setSidebarOpen(false)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Theming: toggle dark/light
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-500">
      {/* Theme toggle button */}
      <button
        aria-label="Toggle dark mode"
        className="fixed top-4 right-4 z-50 rounded-full p-2 bg-white dark:bg-gray-800 shadow hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      >
        {theme === 'light' ? (
          <svg className="h-6 w-6 text-gray-700" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m8.66-8.66l-.71.71M4.05 19.07l-.71.71M21 12h-1M4 12H3m16.95 7.07l-.71-.71M6.34 6.34l-.71-.71" /></svg>
        ) : (
          <svg className="h-6 w-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" /></svg>
        )}
      </button>
      {/* Mobile sidebar with animation and ARIA */}
      <div
        className={clsx(
          'fixed inset-0 z-50 lg:hidden transition-opacity duration-300',
          sidebarOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        )}
        aria-hidden={!sidebarOpen}
      >
        <div className="fixed inset-0 bg-gray-900/80" onClick={() => setSidebarOpen(false)} />
        <div className={clsx(
          'fixed inset-y-0 left-0 flex w-64 flex-col bg-white dark:bg-gray-800 transform transition-transform duration-300',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )} role="navigation" aria-label="Sidebar">
          <div className="flex h-16 items-center justify-between px-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Dogan AI</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white"
              aria-label="Close sidebar"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 space-y-2 px-2 py-4">
            {features.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={clsx(
                    'group flex items-center rounded-md px-3 py-2 text-base font-medium transition-colors duration-150',
                    isActive
                      ? 'bg-green-100 text-green-700 shadow dark:bg-green-900 dark:text-green-200'
                      : 'text-gray-700 hover:bg-green-50 hover:text-green-900 dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-white'
                  )}
                  onClick={() => setSidebarOpen(false)}
                  tabIndex={sidebarOpen ? 0 : -1}
                >
                  <item.icon
                    className={clsx(
                      'mr-4 h-6 w-6 flex-shrink-0',
                      isActive ? 'text-green-700 dark:text-green-200' : 'text-gray-400 group-hover:text-green-600 dark:text-gray-400 dark:group-hover:text-green-300'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
      {/* Desktop sidebar with ARIA and theming */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
        <div className="flex flex-grow flex-col overflow-y-auto">
          <div className="flex h-16 items-center px-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Dogan AI Lab</h2>
          </div>
          <nav className="flex-1 space-y-2 px-2 py-4" role="navigation" aria-label="Sidebar">
            {features.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  className={clsx(
                    'group flex items-center rounded-md px-3 py-2 text-base font-medium transition-colors duration-150',
                    isActive
                      ? 'bg-green-100 text-green-700 shadow dark:bg-green-900 dark:text-green-200'
                      : 'text-gray-700 hover:bg-green-50 hover:text-green-900 dark:text-gray-200 dark:hover:bg-gray-700 dark:hover:text-white'
                  )}
                  tabIndex={0}
                >
                  <item.icon
                    className={clsx(
                      'mr-4 h-6 w-6 flex-shrink-0',
                      isActive ? 'text-green-700 dark:text-green-200' : 'text-gray-400 group-hover:text-green-600 dark:text-gray-400 dark:group-hover:text-green-300'
                    )}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>
          {/* Modular plug-and-play feature section placeholder */}
          {/* Future: Dynamically load feature modules here */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <button
              onClick={handleLogout}
              className="group flex w-full items-center rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-red-50 hover:text-red-700 dark:text-gray-200 dark:hover:bg-red-900 dark:hover:text-red-300 transition-colors duration-150"
            >
              <ArrowRightOnRectangleIcon className="mr-4 h-6 w-6 text-gray-400 group-hover:text-red-600 dark:text-gray-400 dark:group-hover:text-red-300" />
              Logout
            </button>
          </div>
        </div>
      </div>
      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-40 flex h-16 items-center gap-x-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8 transition-colors duration-500">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-gray-700 dark:text-gray-200 lg:hidden"
            aria-label="Open sidebar"
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1 items-center">
              <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Saudi Compliance Platform
              </h1>
            </div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              <button className="text-gray-400 hover:text-gray-500 dark:text-gray-300 dark:hover:text-white" aria-label="Notifications">
                <BellIcon className="h-6 w-6" />
              </button>
              <div className="hidden lg:block lg:h-6 lg:w-px lg:bg-gray-200 dark:bg-gray-700" />
              <div className="flex items-center gap-x-2">
                <UserCircleIcon className="h-8 w-8 text-gray-400 dark:text-gray-200" />
                <div className="hidden sm:block">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-100">{user?.full_name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-300">{user?.role}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Page content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
// Comments: Theming, animation, and accessibility hooks are now in place for future modular extension.