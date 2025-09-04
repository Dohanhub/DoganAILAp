"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

type Std = { id:number; name:string; version:string }

export default function StandardsPage() {
  const [items, setItems] = useState<Std[]>([])
  useEffect(() => {
    (async () => {
      const res = await apiFetch('/api/standards')
      if (res.ok) setItems(await res.json())
    })()
  }, [])
  return (
    <main className="p-md">
      <h1 className="text-xl font-semibold mb-md">{t('standards.title')}</h1>
      <ul className="space-y-sm">
        {items.map(s => (
          <li key={s.id} className="border rounded-md p-sm">
            <div className="font-medium">{s.name}</div>
            <div className="text-fg-muted text-sm">v{s.version}</div>
          </li>
        ))}
      </ul>
    </main>
  )
}
