/**
 * Optimized API Service for Market-Ready Dashboard Performance
 * Implements caching, batching, and real-time data management
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios'

// Performance monitoring
interface PerformanceMetrics {
  requestCount: number
  averageResponseTime: number
  errorRate: number
  cacheHitRate: number
  lastUpdated: Date
}

// Cache interface
interface CacheEntry<T> {
  data: T
  timestamp: Date
  ttl: number
  key: string
}

// Request batching
interface BatchRequest {
  endpoint: string
  params?: any
  resolve: (data: any) => void
  reject: (error: any) => void
}

class OptimizedApiService {
  private api: AxiosInstance
  private cache: Map<string, CacheEntry<any>> = new Map()
  private batchQueue: BatchRequest[] = []
  private batchTimer: NodeJS.Timeout | null = null
  private metrics: PerformanceMetrics = {
    requestCount: 0,
    averageResponseTime: 0,
    errorRate: 0,
    cacheHitRate: 0,
    lastUpdated: new Date()
  }

  constructor(baseURL: string = 'http://localhost:8000') {
    this.api = axios.create({
      baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'X-Client': 'DoganAI-Dashboard'
      }
    })

    this.setupInterceptors()
    this.startCacheCleanup()
  }

  private setupInterceptors() {
    // Request interceptor for performance tracking
    this.api.interceptors.request.use(
      (config) => {
        config.metadata = { startTime: Date.now() }
        this.metrics.requestCount++
        return config
      },
      (error) => {
        this.metrics.errorRate++
        return Promise.reject(error)
      }
    )

    // Response interceptor for performance tracking
    this.api.interceptors.response.use(
      (response: AxiosResponse & { config: any }) => {
        const endTime = Date.now()
        const duration = endTime - response.config.metadata.startTime
        
        // Update average response time
        this.metrics.averageResponseTime = 
          (this.metrics.averageResponseTime + duration) / 2
        
        this.metrics.lastUpdated = new Date()
        return response
      },
      (error) => {
        this.metrics.errorRate++
        this.metrics.lastUpdated = new Date()
        return Promise.reject(error)
      }
    )
  }

  private startCacheCleanup() {
    // Clean expired cache entries every 5 minutes
    setInterval(() => {
      const now = Date.now()
      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp.getTime() > entry.ttl) {
          this.cache.delete(key)
        }
      }
    }, 5 * 60 * 1000)
  }

  private getCacheKey(endpoint: string, params?: any): string {
    return `${endpoint}_${JSON.stringify(params || {})}`
  }

  private getFromCache<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    const now = Date.now()
    if (now - entry.timestamp.getTime() > entry.ttl) {
      this.cache.delete(key)
      return null
    }

    this.metrics.cacheHitRate = 
      (this.metrics.cacheHitRate * 0.9) + (1 * 0.1) // Moving average
    
    return entry.data
  }

  private setCache<T>(key: string, data: T, ttl: number = 60000) {
    this.cache.set(key, {
      data,
      timestamp: new Date(),
      ttl,
      key
    })
  }

  private processBatch() {
    if (this.batchQueue.length === 0) return

    const batch = [...this.batchQueue]
    this.batchQueue = []

    // Group requests by endpoint
    const grouped = batch.reduce((acc, req) => {
      if (!acc[req.endpoint]) acc[req.endpoint] = []
      acc[req.endpoint].push(req)
      return acc
    }, {} as Record<string, BatchRequest[]>)

    // Execute batched requests
    Object.entries(grouped).forEach(([endpoint, requests]) => {
      this.executeBatchedRequest(endpoint, requests)
    })
  }

  private async executeBatchedRequest(endpoint: string, requests: BatchRequest[]) {
    try {
      // For dashboard endpoints, we can batch multiple requests
      if (endpoint.includes('/dashboard/')) {
        const batchEndpoint = endpoint.replace('/dashboard/', '/dashboard/batch/')
        const params = requests.map(req => req.params).filter(Boolean)
        
        const response = await this.api.post(batchEndpoint, { requests: params })
        
        // Distribute responses back to individual requests
        requests.forEach((req, index) => {
          const data = response.data.results?.[index] || response.data
          req.resolve(data)
        })
      } else {
        // Execute individual requests for non-batchable endpoints
        requests.forEach(async (req) => {
          try {
            const response = await this.api.get(req.endpoint, { params: req.params })
            req.resolve(response.data)
          } catch (error) {
            req.reject(error)
          }
        })
      }
    } catch (error) {
      requests.forEach(req => req.reject(error))
    }
  }

  // Optimized dashboard data fetching
  async getDashboardStats(useCache: boolean = true): Promise<any> {
    const cacheKey = this.getCacheKey('/api/v1/analytics/summary')
    
    if (useCache) {
      const cached = this.getFromCache(cacheKey)
      if (cached) return cached
    }

    try {
      const response = await this.api.get('/api/v1/analytics/summary')
      const s = response.data
      // Map to legacy stats shape expected by the dashboard
      const data = {
        organizations: s.organizations ?? 0,
        assessments: s.totalAssessments ?? 0,
        avg_compliance: s.averageComplianceScore ?? 0,
        open_risks: s.openRisks ?? 0,
        org_change: '+0%',
        assessment_change: '+0%',
        compliance_change: '+0%',
        risk_change: '+0%'
      }
      
      // Cache for 30 seconds
      this.setCache(cacheKey, data, 30000)
      return data
    } catch (error) {
      // Return fallback data on error
      return this.getFallbackDashboardStats()
    }
  }

  async getComplianceTrends(timeframe: string = '7d', useCache: boolean = true): Promise<any> {
    const cacheKey = this.getCacheKey('/api/v1/analytics/trends', { timeframe })
    
    if (useCache) {
      const cached = this.getFromCache(cacheKey)
      if (cached) return cached
    }

    try {
      const days = parseInt(timeframe.replace(/[^0-9]/g, ''), 10) || 7
      const response = await this.api.get('/api/v1/analytics/trends', { params: { days } })
      const data = response.data?.trends ? response.data : { trends: response.data || [] }
      
      // Cache for 1 minute
      this.setCache(cacheKey, data, 60000)
      return data
    } catch (error) {
      return this.getFallbackComplianceTrends()
    }
  }

  async getRiskDistribution(useCache: boolean = true): Promise<any> {
    const cacheKey = this.getCacheKey('/api/v1/risks/distribution')
    
    if (useCache) {
      const cached = this.getFromCache(cacheKey)
      if (cached) return cached
    }

    try {
      const response = await this.api.get('/api/v1/risks/distribution')
      const data = response.data
      
      // Cache for 45 seconds
      this.setCache(cacheKey, data, 45000)
      return data
    } catch (error) {
      return this.getFallbackRiskDistribution()
    }
  }

  // Batched request method
  async batchRequest<T>(endpoint: string, params?: any): Promise<T> {
    return new Promise((resolve, reject) => {
      this.batchQueue.push({ endpoint, params, resolve, reject })
      
      // Set batch timer if not already set
      if (!this.batchTimer) {
        this.batchTimer = setTimeout(() => {
          this.processBatch()
          this.batchTimer = null
        }, 50) // 50ms batch window
      }
    })
  }

  // Real-time data subscription
  subscribeToRealTimeUpdates(callback: (data: any) => void): () => void {
    const eventSource = new EventSource('/api/v1/compliance/stream')
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        // Invalidate relevant cache entries
        if (data.type === 'compliance_update') {
          this.invalidateCache('/api/v1/compliance/dashboard/stats')
          this.invalidateCache('/api/v1/compliance/trends')
        } else if (data.type === 'risk_update') {
          this.invalidateCache('/api/v1/compliance/risks/distribution')
        }
        
        callback(data)
      } catch (error) {
        console.error('Error parsing real-time data:', error)
      }
    }

    eventSource.onerror = (error) => {
      console.error('Real-time connection error:', error)
    }

    // Return cleanup function
    return () => {
      eventSource.close()
    }
  }

  private invalidateCache(pattern: string) {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key)
      }
    }
  }

  // Fallback data methods
  private getFallbackDashboardStats() {
    return {
      organizations: 0,
      assessments: 0,
      avg_compliance: 0,
      open_risks: 0,
      org_change: '+0%',
      assessment_change: '+0%',
      compliance_change: '+0%',
      risk_change: '+0%',
      data_source: 'FALLBACK',
      timestamp: new Date().toISOString()
    }
  }

  private getFallbackComplianceTrends() {
    return {
      trends: [],
      data_source: 'FALLBACK',
      timestamp: new Date().toISOString()
    }
  }

  private getFallbackRiskDistribution() {
    return {
      distribution: [],
      total_risks: 0,
      data_source: 'FALLBACK',
      timestamp: new Date().toISOString()
    }
  }

  // Performance monitoring
  getPerformanceMetrics(): PerformanceMetrics {
    return { ...this.metrics }
  }

  getCacheStats() {
    return {
      size: this.cache.size,
      hitRate: this.metrics.cacheHitRate,
      entries: Array.from(this.cache.keys())
    }
  }

  // Cache management
  clearCache() {
    this.cache.clear()
  }

  preloadData() {
    // Preload critical dashboard data
    Promise.all([
      this.getDashboardStats(false),
      this.getComplianceTrends('7d', false),
      this.getRiskDistribution(false)
    ]).catch(error => {
      console.warn('Failed to preload dashboard data:', error)
    })
  }
}

// Create singleton instance
export const optimizedApi = new OptimizedApiService()

// Export for React Query integration
export const dashboardQueries = {
  stats: () => ({
    queryKey: ['dashboard-stats'],
    queryFn: () => optimizedApi.getDashboardStats(),
    staleTime: 30000,
    refetchInterval: 60000
  }),
  
  trends: (timeframe: string = '7d') => ({
    queryKey: ['compliance-trends', timeframe],
    queryFn: () => optimizedApi.getComplianceTrends(timeframe),
    staleTime: 60000,
    refetchInterval: 120000
  }),
  
  risks: () => ({
    queryKey: ['risk-distribution'],
    queryFn: () => optimizedApi.getRiskDistribution(),
    staleTime: 45000,
    refetchInterval: 90000
  })
}

export default optimizedApi
