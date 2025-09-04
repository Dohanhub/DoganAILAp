"use client"
import { useState } from 'react'
import { getApiBase, authHeaders, apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'
import { fmtNumber, fmtDate } from '../../lib/format'

export default function Evidence() {
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState('')
  const [items, setItems] = useState<any[]>([])
  const refresh = async () => {
    const res = await apiFetch('/api/evidence')
    if (res.ok) setItems(await res.json())
  }
  const submit = async (e:React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${getApiBase()}/api/evidence/upload`, {
      method: 'POST',
      headers: authHeaders(),
      body: form
    })
    setMessage(res.ok ? 'Uploaded' : 'Upload failed')
    await refresh()
  }
  return (
    <main className="p-md space-y-md">
      <h1 className="text-xl font-semibold">{t('evidence.title')}</h1>
      <form onSubmit={submit} className="space-y-sm">
        <input type="file" onChange={e=>setFile(e.target.files?.[0] || null)} />
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">Upload</button>
      </form>
      {message && <p className="text-fg-muted">{message}</p>}
      <div className="space-x-sm">
        <button className="border rounded-md px-sm py-xs" onClick={async ()=>{
          const res = await apiFetch('/api/evidence/export?fmt=csv')
          const blob = await res.blob(); const url = URL.createObjectURL(blob);
          const a = document.createElement('a'); a.href = url; a.download = 'evidence.csv'; a.click(); URL.revokeObjectURL(url)
        }}>{t('btn.export.csv')}</button>
        <button className="border rounded-md px-sm py-xs" onClick={async ()=>{
          const res = await apiFetch('/api/evidence/export?fmt=json')
          const blob = await res.blob(); const url = URL.createObjectURL(blob);
          const a = document.createElement('a'); a.href = url; a.download = 'evidence.json'; a.click(); URL.revokeObjectURL(url)
        }}>{t('btn.export.json')}</button>
        <button className="border rounded-md px-sm py-xs" onClick={()=>{
          window.print() // user can Save as PDF
        }}>{t('btn.export.pdf')}</button>
      </div>
      <section className="mt-md">
        <h2 className="text-lg font-semibold mb-sm">{t('evidence.recent')}</h2>
        <ul className="space-y-sm">
          {items.map(e => (
            <li key={e.id} className="border rounded-md p-sm">
              <div className="font-medium">{e.filename}</div>
              <div className="text-fg-muted text-sm">{fmtNumber(Math.round(e.size/1024))} KB • {fmtDate(e.uploaded_at)}</div>
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
