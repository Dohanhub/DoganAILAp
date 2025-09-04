/**
 * Custom React Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuth as useAuthContext } from '../providers/AuthProvider'
import { 
  complianceApi, 
  riskApi, 
  dashboardApi, 
  auditApi, 
  reportsApi,
  organizationApi 
} from '../lib/api'

// Auth hook
export const useAuth = () => {
  return useAuthContext()
}

// Dashboard hooks
export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: dashboardApi.getStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useComplianceOverview = () => {
  return useQuery({
    queryKey: ['dashboard', 'compliance-overview'],
    queryFn: dashboardApi.getComplianceOverview,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useRiskSummary = () => {
  return useQuery({
    queryKey: ['dashboard', 'risk-summary'],
    queryFn: dashboardApi.getRiskSummary,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Compliance hooks
export const useFrameworks = () => {
  return useQuery({
    queryKey: ['compliance', 'frameworks'],
    queryFn: complianceApi.getFrameworks,
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

export const useFramework = (id: string) => {
  return useQuery({
    queryKey: ['compliance', 'frameworks', id],
    queryFn: () => complianceApi.getFramework(id),
    enabled: !!id,
    staleTime: 30 * 60 * 1000,
  })
}

export const useControls = (frameworkId?: string) => {
  return useQuery({
    queryKey: ['compliance', 'controls', frameworkId || 'all'],
    queryFn: () => complianceApi.getControls(frameworkId),
    staleTime: 20 * 60 * 1000, // 20 minutes
  })
}

export const useAssessments = () => {
  return useQuery({
    queryKey: ['assessments'],
    queryFn: complianceApi.getAssessments,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useCreateAssessment = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: complianceApi.createAssessment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

// Risk management hooks
export const useRisks = () => {
  return useQuery({
    queryKey: ['risks'],
    queryFn: riskApi.getRisks,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useCreateRisk = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: riskApi.createRisk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'risk-summary'] })
    },
  })
}

export const useUpdateRisk = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, ...data }: { id: string; [key: string]: any }) =>
      riskApi.updateRisk(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'risk-summary'] })
    },
  })
}

export const useDeleteRisk = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: riskApi.deleteRisk,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'risk-summary'] })
    },
  })
}

// Audit hooks
export const useAuditLogs = (params?: {
  start_date?: string
  end_date?: string
  user_id?: string
  action?: string
  limit?: number
  offset?: number
}) => {
  return useQuery({
    queryKey: ['audit', 'logs', params],
    queryFn: () => auditApi.getAuditLogs(params),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Reports hooks
export const useReports = () => {
  return useQuery({
    queryKey: ['reports'],
    queryFn: reportsApi.getReports,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useGenerateReport = () => {
  return useMutation({
    mutationFn: reportsApi.generateReport,
  })
}

export const useScheduleReport = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: reportsApi.scheduleReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })
}

// Organization hooks
export const useOrganizations = () => {
  return useQuery({
    queryKey: ['organizations'],
    queryFn: organizationApi.getOrganizations,
    staleTime: 15 * 60 * 1000, // 15 minutes
  })
}

export const useCreateOrganization = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: organizationApi.createOrganization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}