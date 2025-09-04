"use client"
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { apiFetch } from '../../../lib/api'
import { t } from '../../../lib/i18n'

type Control = { id:number; control_id:string; title:string }

export default function Controls() {
  const params = useParams() as { standardId?: string }
  const [items, setItems] = useState<Control[]>([])
  useEffect(() => {
    (async () => {
      const res = await apiFetch(`/api/controls/${params.standardId}`)
      if (res.ok) setItems(await res.json())
    })()
  }, [params?.standardId])
  return (
    <main className="p-md">
      <h1 className="text-xl font-semibold mb-md">{t('controls.title')}</h1>
      <ul className="space-y-sm">
        {items.map(c => (
          <li key={c.id} className="border rounded-md p-sm">
            <div className="font-medium">{c.control_id} - {c.title}</div>
          </li>
        ))}
      </ul>
    </main>
  )
}
