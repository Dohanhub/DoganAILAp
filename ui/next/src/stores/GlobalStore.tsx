'use client';

import React, { createContext, useContext, useEffect } from 'react';
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools } from 'zustand/middleware';

// Types
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  permissions: string[];
}

interface Notifications {
  alerts: number;
  compliance: number;
  system: number;
  total: number;
}

interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  uptime: number;
  responseTime: number;
  services: {
    [key: string]: {
      status: 'online' | 'offline' | 'degraded';
      responseTime?: number;
      lastCheck: string;
    };
  };
}

interface GlobalState {
  // User state
  user: User | null;
  isAuthenticated: boolean;
  
  // UI state
  language: 'ar' | 'en';
  darkMode: boolean;
  sidebarOpen: boolean;
  
  // Application state
  notifications: Notifications;
  systemHealth: SystemHealth | null;
  isLoading: boolean;
  error: string | null;
  
  // Real-time data
  isConnected: boolean;
  lastUpdate: Date | null;
  
  // Settings
  autoRefresh: boolean;
  refreshInterval: number;
  
  // Actions
  setUser: (user: User | null) => void;
  setLanguage: (language: 'ar' | 'en') => void;
  toggleDarkMode: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setNotifications: (notifications: Partial<Notifications>) => void;
  setSystemHealth: (health: SystemHealth) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setConnected: (connected: boolean) => void;
  updateLastUpdate: () => void;
  setAutoRefresh: (autoRefresh: boolean) => void;
  setRefreshInterval: (interval: number) => void;
  clearError: () => void;
  logout: () => void;
  reset: () => void;
}

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  language: 'ar' as const,
  darkMode: false,
  sidebarOpen: true,
  notifications: {
    alerts: 0,
    compliance: 0,
    system: 0,
    total: 0,
  },
  systemHealth: null,
  isLoading: false,
  error: null,
  isConnected: false,
  lastUpdate: null,
  autoRefresh: true,
  refreshInterval: 30000, // 30 seconds
};

// Create the store
export const useGlobalStore = create<GlobalState>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,
        
        // User actions
        setUser: (user) => set(
          { user, isAuthenticated: !!user },
          false,
          'setUser'
        ),
        
        // UI actions
        setLanguage: (language) => set(
          { language },
          false,
          'setLanguage'
        ),
        
        toggleDarkMode: () => set(
          (state) => ({ darkMode: !state.darkMode }),
          false,
          'toggleDarkMode'
        ),
        
        toggleSidebar: () => set(
          (state) => ({ sidebarOpen: !state.sidebarOpen }),
          false,
          'toggleSidebar'
        ),
        
        setSidebarOpen: (open) => set(
          { sidebarOpen: open },
          false,
          'setSidebarOpen'
        ),
        
        // Notification actions
        setNotifications: (notifications) => set(
          (state) => {
            const updated = { ...state.notifications, ...notifications };
            updated.total = updated.alerts + updated.compliance + updated.system;
            return { notifications: updated };
          },
          false,
          'setNotifications'
        ),
        
        // System health actions
        setSystemHealth: (health) => set(
          { systemHealth: health },
          false,
          'setSystemHealth'
        ),
        
        // Loading and error actions
        setLoading: (loading) => set(
          { isLoading: loading },
          false,
          'setLoading'
        ),
        
        setError: (error) => set(
          { error },
          false,
          'setError'
        ),
        
        clearError: () => set(
          { error: null },
          false,
          'clearError'
        ),
        
        // Connection actions
        setConnected: (connected) => set(
          { isConnected: connected },
          false,
          'setConnected'
        ),
        
        updateLastUpdate: () => set(
          { lastUpdate: new Date() },
          false,
          'updateLastUpdate'
        ),
        
        // Settings actions
        setAutoRefresh: (autoRefresh) => set(
          { autoRefresh },
          false,
          'setAutoRefresh'
        ),
        
        setRefreshInterval: (interval) => set(
          { refreshInterval: interval },
          false,
          'setRefreshInterval'
        ),
        
        // Auth actions
        logout: () => set(
          {
            user: null,
            isAuthenticated: false,
            notifications: initialState.notifications,
          },
          false,
          'logout'
        ),
        
        // Reset action
        reset: () => set(
          initialState,
          false,
          'reset'
        ),
      }),
      {
        name: 'doganai-compliance-store',
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          language: state.language,
          darkMode: state.darkMode,
          sidebarOpen: state.sidebarOpen,
          autoRefresh: state.autoRefresh,
          refreshInterval: state.refreshInterval,
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
        onRehydrateStorage: () => (state) => {
          if (state) {
            console.log('Hydration completed');
          }
        },
      }
    ),
    {
      name: 'GlobalStore',
    }
  )
);

// Provider component for additional initialization
interface GlobalProviderProps {
  children: React.ReactNode;
}

export const GlobalProvider: React.FC<GlobalProviderProps> = ({ children }) => {
  const { 
    language, 
    darkMode, 
    autoRefresh, 
    refreshInterval,
    setConnected,
    updateLastUpdate,
    setSystemHealth,
    setNotifications 
  } = useGlobalStore();

  // Initialize language and theme
  useEffect(() => {
    // Set document direction based on language
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = language;
  }, [language]);

  useEffect(() => {
    // Set theme class on body
    document.body.className = darkMode ? 'dark-theme' : 'light-theme';
  }, [darkMode]);

  // Auto-refresh logic
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      updateLastUpdate();
      
      // Simulate health check and notifications update
      // In real app, this would be replaced with actual API calls
      setConnected(Math.random() > 0.1); // 90% uptime simulation
      
      const mockHealth = {
        status: Math.random() > 0.8 ? 'warning' : 'healthy' as const,
        uptime: Date.now() - 86400000, // 24 hours ago
        responseTime: Math.floor(Math.random() * 500) + 100,
        services: {
          api: {
            status: Math.random() > 0.9 ? 'offline' : 'online' as const,
            responseTime: Math.floor(Math.random() * 200) + 50,
            lastCheck: new Date().toISOString(),
          },
          database: {
            status: Math.random() > 0.95 ? 'degraded' : 'online' as const,
            responseTime: Math.floor(Math.random() * 100) + 20,
            lastCheck: new Date().toISOString(),
          },
          auth: {
            status: 'online' as const,
            responseTime: Math.floor(Math.random() * 150) + 30,
            lastCheck: new Date().toISOString(),
          },
        },
      };
      
      setSystemHealth(mockHealth);
      
      // Update notifications with random values for demo
      setNotifications({
        alerts: Math.floor(Math.random() * 5),
        compliance: Math.floor(Math.random() * 3),
        system: Math.floor(Math.random() * 2),
      });
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, setConnected, updateLastUpdate, setSystemHealth, setNotifications]);

  // Error boundary simulation
  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error('Global error caught:', error);
      useGlobalStore.getState().setError(error.message);
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);
      useGlobalStore.getState().setError('An unexpected error occurred');
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return <>{children}</>;
};

// Selectors for optimized performance
export const useAuth = () => useGlobalStore((state) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  setUser: state.setUser,
  logout: state.logout,
}));

export const useUI = () => useGlobalStore((state) => ({
  language: state.language,
  darkMode: state.darkMode,
  sidebarOpen: state.sidebarOpen,
  setLanguage: state.setLanguage,
  toggleDarkMode: state.toggleDarkMode,
  toggleSidebar: state.toggleSidebar,
  setSidebarOpen: state.setSidebarOpen,
}));

export const useNotifications = () => useGlobalStore((state) => ({
  notifications: state.notifications,
  setNotifications: state.setNotifications,
}));

export const useSystemStatus = () => useGlobalStore((state) => ({
  systemHealth: state.systemHealth,
  isConnected: state.isConnected,
  lastUpdate: state.lastUpdate,
  setSystemHealth: state.setSystemHealth,
  setConnected: state.setConnected,
  updateLastUpdate: state.updateLastUpdate,
}));

export const useAppSettings = () => useGlobalStore((state) => ({
  autoRefresh: state.autoRefresh,
  refreshInterval: state.refreshInterval,
  setAutoRefresh: state.setAutoRefresh,
  setRefreshInterval: state.setRefreshInterval,
}));

export const useErrorHandling = () => useGlobalStore((state) => ({
  error: state.error,
  isLoading: state.isLoading,
  setError: state.setError,
  setLoading: state.setLoading,
  clearError: state.clearError,
}));
