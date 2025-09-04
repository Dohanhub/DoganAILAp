"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

export default function Diagnostics() {
  const [conn, setConn] = useState<any>(null)
  const [diag, setDiag] = useState<any>(null)
  useEffect(() => { (async () => {
    const a = await apiFetch('/api/auto/connectivity')
    if (a.ok) setConn(await a.json())
    const d = await apiFetch('/api/diagnostics')
    if (d.ok) setDiag(await d.json())
  })() }, [])
  return (
    <main className="p-md space-y-md">
      <h1 className="text-xl font-semibold">{t('diagnostics.title')}</h1>
      <section>
        <h2 className="font-medium mb-sm">{t('diagnostics.connectivity')}</h2>
        <pre className="bg-gray-900 text-white p-md rounded-md overflow-auto">{JSON.stringify(conn, null, 2)}</pre>
      </section>
      <section>
        <h2 className="font-medium mb-sm">{t('diagnostics.db')}</h2>
        <pre className="bg-gray-900 text-white p-md rounded-md overflow-auto">{JSON.stringify(diag, null, 2)}</pre>
      </section>
    </main>
  )
}
