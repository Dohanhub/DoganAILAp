'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { useGlobalStore } from '@/stores/GlobalStore';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  emit: (event: string, data?: any) => void;
  on: (event: string, callback: Function) => void;
  off: (event: string, callback?: Function) => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

interface SocketProviderProps {
  children: React.ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const { setConnected, setSystemHealth, setNotifications } = useGlobalStore();

  useEffect(() => {
    const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'http://localhost:8000';
    
    console.log('🔌 Initializing Socket.IO connection to:', WS_URL);
    
    const newSocket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      timeout: 5000,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      forceNew: true,
    });

    // Connection events
    newSocket.on('connect', () => {
      console.log('✅ Socket.IO connected');
      setIsConnected(true);
      setConnected(true);
      setSocket(newSocket);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('❌ Socket.IO disconnected:', reason);
      setIsConnected(false);
      setConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('🚫 Socket.IO connection error:', error);
      setIsConnected(false);
      setConnected(false);
    });

    newSocket.on('reconnect', (attemptNumber) => {
      console.log('🔄 Socket.IO reconnected after', attemptNumber, 'attempts');
      setIsConnected(true);
      setConnected(true);
    });

    newSocket.on('reconnect_error', (error) => {
      console.error('🔄❌ Socket.IO reconnection failed:', error);
    });

    // Data events
    newSocket.on('health_update', (data) => {
      console.log('📊 Received health update:', data);
      setSystemHealth(data);
    });

    newSocket.on('notification', (data) => {
      console.log('🔔 Received notification:', data);
      setNotifications(data);
    });

    newSocket.on('compliance_update', (data) => {
      console.log('⚖️ Received compliance update:', data);
      // Handle compliance updates
    });

    newSocket.on('alert', (data) => {
      console.log('🚨 Received alert:', data);
      // Handle alerts
    });

    // Subscribe to default channels
    newSocket.emit('subscribe', {
      channels: ['health', 'notifications', 'compliance', 'alerts'],
      userId: 'user-' + Math.random().toString(36).substr(2, 9),
    });

    setSocket(newSocket);

    return () => {
      console.log('🔌 Cleaning up Socket.IO connection');
      newSocket.disconnect();
      setSocket(null);
      setIsConnected(false);
    };
  }, [setConnected, setSystemHealth, setNotifications]);

  const emit = (event: string, data?: any) => {
    if (socket && isConnected) {
      socket.emit(event, data);
    } else {
      console.warn('Cannot emit event: Socket not connected');
    }
  };

  const on = (event: string, callback: Function) => {
    if (socket) {
      socket.on(event, callback);
    }
  };

  const off = (event: string, callback?: Function) => {
    if (socket) {
      socket.off(event, callback);
    }
  };

  const value: SocketContextType = {
    socket,
    isConnected,
    emit,
    on,
    off,
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = (): SocketContextType => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
