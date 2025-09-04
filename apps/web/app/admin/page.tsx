"use client"
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { fetchMe } from '../../lib/session'
import { t } from '../../lib/i18n'

export default function AdminHome() {
  const [ok, setOk] = useState(false)
  useEffect(() => { (async () => { const me = await fetchMe(); setOk(me?.role === 'admin') })() }, [])
  if (!ok) return <main className="p-md">Forbidden</main>
  return (
    <main className="p-md space-y-sm">
      <h1 className="text-xl font-semibold">{t('admin.title')}</h1>
      <ul className="list-disc pl-md">
        <li><Link className="text-blue-600" href="/admin/tenants">{t('admin.tenants')}</Link></li>
        <li><Link className="text-blue-600" href="/admin/users">{t('admin.users')}</Link></li>
        <li><Link className="text-blue-600" href="/diagnostics">Diagnostics</Link></li>
      </ul>
    </main>
  )
}
