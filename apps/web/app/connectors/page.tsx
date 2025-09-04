"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

type Connector = { id:number; name:string; category?:string; vendor_id?:number; regulator_id?:number; description?:string }

export default function Connectors() {
  const [items, setItems] = useState<Connector[]>([])
  useEffect(() => { (async () => {
    const res = await apiFetch('/api/connectors')
    if (res.ok) setItems(await res.json())
  })() }, [])
  return (
    <main className="p-md">
      <h1 className="text-xl font-semibold mb-md">{t('connectors.title')}</h1>
      <ul className="space-y-sm">
        {items.map(c => (
          <li key={c.id} className="border rounded-md p-sm">
            <div className="font-medium">{c.name}</div>
            <div className="text-fg-muted text-sm">{c.category}</div>
            {c.description && <div className="text-sm">{c.description}</div>}
          </li>
        ))}
      </ul>
    </main>
  )
}
