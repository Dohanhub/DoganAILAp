import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// API service functions
export const authService = {
  login: (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  register: (data: any) =>
    api.post('/api/auth/register', data),
  me: () => api.get('/api/auth/me'),
}

export const organizationService = {
  list: (params?: any) => api.get('/api/organizations', { params }),
  get: (id: number) => api.get(`/api/organizations/${id}`),
  create: (data: any) => api.post('/api/organizations', data),
  update: (id: number, data: any) => api.put(`/api/organizations/${id}`, data),
  delete: (id: number) => api.delete(`/api/organizations/${id}`),
}

export const frameworkService = {
  list: (saudiOnly = false) => api.get('/api/frameworks', { params: { saudi_only: saudiOnly } }),
  getControls: (code: string, category?: string) =>
    api.get(`/api/frameworks/${code}/controls`, { params: { category } }),
}

export const assessmentService = {
  list: (params?: any) => api.get('/api/assessments', { params }),
  create: (data: any) => api.post('/api/assessments', data),
  complete: (id: number, data: any) => api.put(`/api/assessments/${id}/complete`, null, { params: data }),
}

export const riskService = {
  list: (params?: any) => api.get('/api/risks', { params }),
  create: (data: any) => api.post('/api/risks', data),
  update: (id: number, data: any) => api.put(`/api/risks/${id}`, data),
}

export const analyticsService = {
  dashboard: (organizationId?: number) =>
    api.get('/api/analytics/dashboard', { params: { organization_id: organizationId } }),
  trends: (organizationId: number, frameworkCode?: string, days = 30) =>
    api.get('/api/analytics/trends', {
      params: { organization_id: organizationId, framework_code: frameworkCode, days },
    }),
}

export const reportService = {
  generate: (data: any) => api.post('/api/reports/generate', data),
  download: (id: number) => api.get(`/api/reports/${id}/download`, { responseType: 'blob' }),
}

export const notificationService = {
  list: (unreadOnly = false) => api.get('/api/notifications', { params: { unread_only: unreadOnly } }),
  markRead: (id: number) => api.put(`/api/notifications/${id}/read`),
}