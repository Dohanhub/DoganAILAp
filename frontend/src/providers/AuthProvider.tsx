/**
 * Auth Provider - Authentication state management
 */

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../lib/api'

export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'auditor' | 'user'
  permissions: string[]
  tenant_id?: string
  avatar?: string
}

type AuthProviderProps = {
  children: React.ReactNode
}

type AuthProviderState = {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthProviderContext = createContext<AuthProviderState | undefined>(undefined)

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  // Check for existing session on mount
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('doganai-token')
      if (!token) {
        setIsLoading(false)
        return
      }

      // Verify token with backend
      const userData = await authApi.me()
      setUser(userData)
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('doganai-token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true)
      const response = await authApi.login(email, password)
      
      // Store token
      localStorage.setItem('doganai-token', response.access_token)
      
      // Set user data
      setUser(response.user)
      
      // Navigate to dashboard
      navigate('/dashboard')
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local state regardless of API call result
      localStorage.removeItem('doganai-token')
      setUser(null)
      navigate('/login')
    }
  }

  const refreshUser = async () => {
    try {
      const userData = await authApi.me()
      setUser(userData)
    } catch (error) {
      console.error('Failed to refresh user:', error)
      logout()
    }
  }

  const value: AuthProviderState = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshUser,
  }

  return (
    <AuthProviderContext.Provider value={value}>
      {children}
    </AuthProviderContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthProviderContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}