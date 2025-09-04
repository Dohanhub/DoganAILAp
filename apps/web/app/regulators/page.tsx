"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

type Reg = { id:number; name:string; country?:string; sector?:string; website?:string }

export default function Regulators() {
  const [items, setItems] = useState<Reg[]>([])
  useEffect(() => { (async () => {
    const res = await apiFetch('/api/regulators')
    if (res.ok) setItems(await res.json())
  })() }, [])
  return (
    <main className="p-md">
      <h1 className="text-xl font-semibold mb-md">{t('regulators.title')}</h1>
      <ul className="space-y-sm">
        {items.map(r => (
          <li key={r.id} className="border rounded-md p-sm">
            <div className="font-medium">{r.name}</div>
            <div className="text-fg-muted text-sm">{r.country} {r.sector ? `• ${r.sector}` : ''}</div>
            {r.website && <a className="text-blue-600 text-sm" href={r.website} target="_blank">{r.website}</a>}
          </li>
        ))}
      </ul>
    </main>
  )
}
