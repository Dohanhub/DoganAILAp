"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../../lib/api'
import { fetchMe } from '../../../lib/session'
import { t } from '../../../lib/i18n'

type Tenant = { id:number; name:string; api_key?:string }

export default function TenantsAdmin() {
  const [ok, setOk] = useState(false)
  const [items, setItems] = useState<Tenant[]>([])
  const [name, setName] = useState('')
  const refresh = async () => {
    const res = await apiFetch('/api/tenants')
    if (res.ok) setItems(await res.json())
  }
  useEffect(() => { (async () => { const me = await fetchMe(); setOk(me?.role === 'admin'); await refresh() })() }, [])
  const create = async (e:React.FormEvent) => {
    e.preventDefault()
    await apiFetch('/api/tenants', { method: 'POST', body: { name } })
    setName(''); await refresh()
  }
  const rotate = async (id:number) => { await apiFetch(`/api/tenants/${id}/rotate-key`, { method: 'POST' }); await refresh() }
  if (!ok) return <main className="p-md">Forbidden</main>
  return (
    <main className="p-md space-y-md">
      <h1 className="text-xl font-semibold">{t('admin.tenants')}</h1>
      <form onSubmit={create} className="space-x-sm">
        <input className="border rounded-md p-sm" placeholder={t('tenants.name.placeholder')} value={name} onChange={e=>setName(e.target.value)} />
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">{t('btn.create')}</button>
      </form>
      <ul className="space-y-sm">
        {items.map(tenant => (
          <li key={tenant.id} className="border rounded-md p-sm">
            <div className="font-medium">{tenant.name}</div>
            <div className="text-sm text-fg-muted">{t('tenants.apiKey')}: {tenant.api_key || '(none)'}</div>
            <button className="mt-sm border rounded-md px-sm py-xs" onClick={() => rotate(tenant.id)}>{t('btn.rotate')}</button>
          </li>
        ))}
      </ul>
    </main>
  )
}
