import { create } from 'zustand'
import api from '../services/api'
import toast from 'react-hot-toast'

interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
}

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  checkAuth: () => void
}

export const useAuthStore = create<AuthStore>((set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (username: string, password: string) => {
        set({ isLoading: true })
        try {
          const formData = new FormData()
          formData.append('username', username)
          formData.append('password', password)
          
          const response = await api.post('/api/auth/login', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          })
          const { access_token, user } = response.data
          
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false
          })
          
          toast.success(`Welcome back, ${user.full_name || user.username}!`)
        } catch (error: any) {
          set({ isLoading: false })
          toast.error(error.response?.data?.detail || 'Login failed')
          throw error
        }
      },

      register: async (data: any) => {
        set({ isLoading: true })
        try {
          const response = await api.post('/api/auth/register', data)
          const { access_token, user } = response.data
          
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false
          })
          
          toast.success('Registration successful!')
        } catch (error: any) {
          set({ isLoading: false })
          toast.error(error.response?.data?.detail || 'Registration failed')
          throw error
        }
      },

      logout: () => {
        delete api.defaults.headers.common['Authorization']
        set({
          user: null,
          token: null,
          isAuthenticated: false
        })
        toast.success('Logged out successfully')
      },

      checkAuth: () => {
        const state = get()
        if (state.token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
          set({ isAuthenticated: true })
        }
      }
}))