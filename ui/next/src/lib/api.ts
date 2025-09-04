import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add API key for local development
    config.headers['X-API-Key'] = 'local_dev_key_12345';
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    
    // Handle common errors
    if (error.response?.status === 401) {
      // Redirect to login or refresh token
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// API Methods
export const apiClient = {
  // Health endpoints
  health: {
    check: () => api.get('/health'),
    services: () => api.get('/health/services'),
  },
  
  // Compliance endpoints
  compliance: {
    metrics: () => api.get('/api/compliance/metrics'),
    evaluate: (data: any) => api.post('/api/compliance/evaluate', data),
    history: (params?: any) => api.get('/api/compliance/history', { params }),
    reports: () => api.get('/api/compliance/reports'),
  },
  
  // Dashboard endpoints
  dashboard: {
    overview: () => api.get('/api/dashboard/overview'),
    activity: () => api.get('/api/dashboard/activity'),
    notifications: () => api.get('/api/dashboard/notifications'),
  },
  
  // Audit endpoints
  audit: {
    logs: (params?: any) => api.get('/api/audit/logs', { params }),
    create: (data: any) => api.post('/api/audit/logs', data),
  },
  
  // Vendor endpoints
  vendors: {
    list: () => api.get('/api/vendors'),
    get: (id: string) => api.get(`/api/vendors/${id}`),
    evaluate: (id: string, data: any) => api.post(`/api/vendors/${id}/evaluate`, data),
  },
  
  // Benchmarks endpoints
  benchmarks: {
    list: () => api.get('/api/benchmarks'),
    kpis: () => api.get('/api/benchmarks/kpis'),
  },
  
  // Real-time data
  realtime: {
    status: () => api.get('/api/realtime/status'),
    metrics: () => api.get('/api/realtime/metrics'),
  },
};

// Generic API helpers
export const makeRequest = async <T = any>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await api.request<T>(config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Export the configured axios instance
export default api;
