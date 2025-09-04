import { useQuery, useQueryClient } from 'react-query';
import { apiClient } from '@/lib/api';
import { useGlobalStore } from '@/stores/GlobalStore';

interface ServiceHealth {
  status: 'online' | 'offline' | 'degraded';
  responseTime?: number;
  lastCheck: string;
}

interface HealthData {
  status: 'healthy' | 'warning' | 'critical';
  uptime: number;
  responseTime: number;
  services: {
    [key: string]: ServiceHealth;
  };
  timestamp: string;
}

export const useHealthCheck = () => {
  const queryClient = useQueryClient();
  const { setSystemHealth, setConnected, autoRefresh } = useGlobalStore();

  const query = useQuery<HealthData>(
    'health-check',
    async () => {
      try {
        const response = await apiClient.health.check();
        const healthData = response.data;
        
        // Update global state
        setSystemHealth(healthData);
        setConnected(true);
        
        return healthData;
      } catch (error) {
        console.error('Health check failed:', error);
        setConnected(false);
        
        // Return fallback data
        return {
          status: 'critical' as const,
          uptime: 0,
          responseTime: 0,
          services: {},
          timestamp: new Date().toISOString(),
        };
      }
    },
    {
      refetchInterval: autoRefresh ? 30000 : false, // 30 seconds
      refetchIntervalInBackground: true,
      staleTime: 10000, // 10 seconds
      cacheTime: 60000, // 1 minute
      retry: 2,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      onError: (error) => {
        console.error('Health check query failed:', error);
        setConnected(false);
      },
      onSuccess: (data) => {
        setSystemHealth(data);
        setConnected(true);
      },
    }
  );

  const checkAllServices = async () => {
    try {
      const servicesResponse = await apiClient.health.services();
      queryClient.setQueryData('health-services', servicesResponse.data);
      return servicesResponse.data;
    } catch (error) {
      console.error('Services health check failed:', error);
      throw error;
    }
  };

  return {
    ...query,
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    checkAllServices,
    refetch: query.refetch,
  };
};
