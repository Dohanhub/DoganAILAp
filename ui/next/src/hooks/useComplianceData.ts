import { useQuery, useMutation, useQueryClient } from 'react-query';
import { apiClient } from '@/lib/api';

interface ComplianceMetrics {
  totalCompliance: number;
  compliantItems: number;
  totalItems: number;
  criticalIssues: number;
  warningItems: number;
  passedControls: number;
  complianceTrend: number;
  criticalTrend: number;
  warningTrend: number;
  passedTrend: number;
}

interface ComplianceActivity {
  id: string;
  title: string;
  description: string;
  type: 'success' | 'warning' | 'error';
  timestamp: string;
}

interface ComplianceData {
  metrics: ComplianceMetrics;
  trends: Array<{
    name: string;
    compliance: number;
    date: string;
  }>;
  distribution: Array<{
    score: number;
    label: string;
    color: string;
  }>;
  recentActivities: ComplianceActivity[];
  lastUpdated: string;
}

export const useComplianceData = () => {
  const queryClient = useQueryClient();

  const query = useQuery<ComplianceData>(
    'compliance-data',
    async () => {
      try {
        const response = await apiClient.compliance.metrics();
        return response.data;
      } catch (error) {
        console.error('Failed to fetch compliance data:', error);
        
        // Return fallback mock data
        return {
          metrics: {
            totalCompliance: 85.2,
            compliantItems: 342,
            totalItems: 401,
            criticalIssues: 12,
            warningItems: 47,
            passedControls: 342,
            complianceTrend: 2.3,
            criticalTrend: -1.8,
            warningTrend: -0.5,
            passedTrend: 3.1,
          },
          trends: [
            { name: 'Mon', compliance: 82, date: '2024-01-01' },
            { name: 'Tue', compliance: 84, date: '2024-01-02' },
            { name: 'Wed', compliance: 81, date: '2024-01-03' },
            { name: 'Thu', compliance: 86, date: '2024-01-04' },
            { name: 'Fri', compliance: 85, date: '2024-01-05' },
            { name: 'Sat', compliance: 87, date: '2024-01-06' },
            { name: 'Sun', compliance: 85, date: '2024-01-07' },
          ],
          distribution: [
            { score: 342, label: 'Compliant', color: '#4caf50' },
            { score: 47, label: 'Warnings', color: '#ff9800' },
            { score: 12, label: 'Critical', color: '#f44336' },
          ],
          recentActivities: [
            {
              id: '1',
              title: 'NCA Policy Updated',
              description: 'Commercial authorization requirements updated',
              type: 'success',
              timestamp: '2 minutes ago',
            },
            {
              id: '2',
              title: 'SAMA Alert',
              description: 'Banking compliance threshold exceeded',
              type: 'warning',
              timestamp: '15 minutes ago',
            },
            {
              id: '3',
              title: 'Critical Violation',
              description: 'Data protection policy violation detected',
              type: 'error',
              timestamp: '1 hour ago',
            },
          ],
          lastUpdated: new Date().toISOString(),
        };
      }
    },
    {
      refetchInterval: 60000, // 1 minute
      staleTime: 30000, // 30 seconds
      cacheTime: 300000, // 5 minutes
      retry: 2,
    }
  );

  const evaluateCompliance = useMutation(
    (evaluationData: any) => apiClient.compliance.evaluate(evaluationData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('compliance-data');
        queryClient.invalidateQueries('audit-logs');
      },
      onError: (error) => {
        console.error('Compliance evaluation failed:', error);
      },
    }
  );

  const getComplianceHistory = useQuery(
    'compliance-history',
    () => apiClient.compliance.history(),
    {
      enabled: false, // Only fetch when explicitly called
      staleTime: 60000,
    }
  );

  return {
    ...query,
    data: query.data,
    isLoading: query.isLoading,
    isRefetching: query.isRefetching,
    error: query.error,
    refetch: query.refetch,
    evaluateCompliance,
    getComplianceHistory,
  };
};
