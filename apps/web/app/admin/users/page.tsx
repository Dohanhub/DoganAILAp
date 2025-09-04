"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../../lib/api'
import { fetchMe } from '../../../lib/session'
import { t } from '../../../lib/i18n'

export default function UsersAdmin() {
  const [ok, setOk] = useState(false)
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<'admin'|'auditor'|'user'>('user')
  const [msg, setMsg] = useState('')
  useEffect(() => { (async () => { const me = await fetchMe(); setOk(me?.role === 'admin') })() }, [])
  if (!ok) return <main className="p-md">Forbidden</main>
  const save = async (e:React.FormEvent) => {
    e.preventDefault()
    const res = await apiFetch('/api/users/assign-role', { method: 'POST', body: { email, role } })
    setMsg(res.ok ? 'Updated' : 'Failed')
  }
  return (
    <main className="p-md space-y-sm max-w-xl">
      <h1 className="text-xl font-semibold">{t('admin.users')}</h1>
      <form onSubmit={save} className="space-y-sm">
        <input className="border rounded-md p-sm w-full" placeholder={t('users.email')} value={email} onChange={e=>setEmail(e.target.value)} />
        <select className="border rounded-md p-sm" value={role} onChange={e=>setRole(e.target.value as any)}>
          <option value="user">user</option>
          <option value="auditor">auditor</option>
          <option value="admin">admin</option>
        </select>
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">{t('btn.assign')}</button>
      </form>
      {msg && <p className="text-fg-muted">{msg}</p>}
    </main>
  )
}
