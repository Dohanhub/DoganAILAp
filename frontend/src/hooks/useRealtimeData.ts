/**
 * Real-time data hook for dashboard updates
 */

import { useState, useEffect } from 'react'

interface RealtimeData {
  metrics?: any
  notifications: any[]
  events: any[]
  lastUpdated: Date
}

export const useRealtimeData = () => {
  const [data, setData] = useState<RealtimeData>({
    notifications: [],
    events: [],
    lastUpdated: new Date()
  })

  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Simulate real-time connection
    setIsConnected(true)
    
    // Mock data update interval
    const interval = setInterval(() => {
      setData(prev => ({
        ...prev,
        lastUpdated: new Date()
      }))
    }, 30000) // Update every 30 seconds

    return () => {
      clearInterval(interval)
      setIsConnected(false)
    }
  }, [])

  return {
    data,
    isConnected,
    refetch: () => {
      setData(prev => ({
        ...prev,
        lastUpdated: new Date()
      }))
    }
  }
}

export default useRealtimeData
