"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

type Vendor = { id:number; name:string; category?:string; website?:string; contact_email?:string }

export default function Vendors() {
  const [items, setItems] = useState<Vendor[]>([])
  useEffect(() => { (async () => {
    const res = await apiFetch('/api/vendors')
    if (res.ok) setItems(await res.json())
  })() }, [])
  return (
    <main className="p-md">
      <h1 className="text-xl font-semibold mb-md">{t('vendors.title')}</h1>
      <ul className="space-y-sm">
        {items.map(v => (
          <li key={v.id} className="border rounded-md p-sm">
            <div className="font-medium">{v.name}</div>
            <div className="text-fg-muted text-sm">{v.category}</div>
            <div className="text-sm">
              {v.website && <a className="text-blue-600" href={v.website} target="_blank">{v.website}</a>}
              {v.contact_email && <span className="ml-sm">{v.contact_email}</span>}
            </div>
          </li>
        ))}
      </ul>
    </main>
  )
}
