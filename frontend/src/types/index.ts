// Common types for DoganAI Compliance Kit

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  organization_id?: number
}

export interface Organization {
  id: number
  name: string
  description?: string
  industry?: string
  size?: string
  country: string
  created_at: string
}

export interface Framework {
  code: string
  name: string
  name_arabic?: string
  description: string
  controls: number
  mandatory: boolean
  country: string
  sector: string
}

export interface Assessment {
  id: number
  name: string
  framework_code: string
  organization_id: number
  status: 'draft' | 'in_progress' | 'completed'
  score?: number
  created_at: string
  completed_at?: string
}

export interface Risk {
  id: number
  title: string
  description: string
  category: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  likelihood: number
  impact: number
  risk_score: number
  status: 'open' | 'mitigated' | 'closed'
  organization_id: number
}

export interface DashboardMetrics {
  total_organizations: number
  total_assessments: number
  completed_assessments: number
  average_compliance_score: number
  high_risk_count: number
  recent_assessments: Assessment[]
  compliance_trends: Array<{
    date: string
    score: number
    framework: string
  }>
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}
