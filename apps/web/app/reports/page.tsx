"use client"
import { useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

export default function Reports() {
  const [standard, setStandard] = useState('')
  const [data, setData] = useState<any>(null)
  const run = async (e:React.FormEvent) => {
    e.preventDefault()
    const res = await apiFetch(`/api/reports/standard/${encodeURIComponent(standard)}`)
    if (res.ok) setData(await res.json())
  }
  const exportFile = async (fmt:'csv'|'json') => {
    const res = await apiFetch(`/api/reports/standard/${encodeURIComponent(standard)}/export?fmt=${fmt}`)
    const blob = await res.blob(); const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `report_${standard}.${fmt}`; a.click(); URL.revokeObjectURL(url)
  }
  return (
    <main className="p-md space-y-md max-w-2xl">
      <h1 className="text-xl font-semibold">{t('reports.title')}</h1>
      <form onSubmit={run} className="space-y-sm">
        <input className="border rounded-md p-sm" placeholder={t('reports.standard.placeholder')} value={standard} onChange={e=>setStandard(e.target.value)} />
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">{t('btn.run')}</button>
      </form>
      {data && (
        <div className="space-y-sm">
          <pre className="bg-gray-900 text-white p-md rounded-md overflow-auto">{JSON.stringify(data, null, 2)}</pre>
          <div className="space-x-sm">
            <button className="border rounded-md px-sm py-xs" onClick={()=>exportFile('csv')}>{t('btn.export.csv')}</button>
            <button className="border rounded-md px-sm py-xs" onClick={()=>exportFile('json')}>{t('btn.export.json')}</button>
            <button className="border rounded-md px-sm py-xs" onClick={()=>window.print()}>{t('btn.export.pdf')}</button>
          </div>
        </div>
      )}
    </main>
  )
}
