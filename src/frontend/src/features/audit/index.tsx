import { useEffect, useState } from 'react'
import { useAuthStore } from '../../store/authStore'
import { auditService } from '../../services/api'

interface AuditRow {
  id: number
  userId?: string
  action: string
  resourceType?: string
  resourceId?: number
  success: boolean
  timestamp: string
}

export default function Audit() {
  const { user } = useAuthStore()
  const [rows, setRows] = useState<AuditRow[] | null>(null)

  const allowed = user?.role === 'admin' || user?.role === 'auditor'

  useEffect(() => {
    if (!allowed) return
    auditService
      .list(100)
      .then((res) => setRows(res.data || []))
      .catch(() => setRows([]))
  }, [allowed])

  if (!allowed) return <p className="text-red-600">Unauthorized</p>
  if (!rows) return <p>Loading…</p>

  return (
    <div>
      <h4 className="text-lg font-semibold mb-3">Audit Trail</h4>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2">Time</th>
              <th className="py-2">User</th>
              <th className="py-2">Action</th>
              <th className="py-2">Resource</th>
              <th className="py-2">Success</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id} className="border-b">
                <td className="py-2">{new Date(a.timestamp).toLocaleString()}</td>
                <td className="py-2">{a.userId || '-'}</td>
                <td className="py-2">{a.action}</td>
                <td className="py-2">{a.resourceType} {a.resourceId}</td>
                <td className="py-2">{a.success ? '✅' : '❌'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

