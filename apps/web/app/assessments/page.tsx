"use client"
import { useEffect, useState } from 'react'
import { apiFetch } from '../../lib/api'
import { t } from '../../lib/i18n'

export default function Assessments() {
  const [standard, setStandard] = useState('')
  const [controlId, setControlId] = useState('')
  const [result, setResult] = useState<any>(null)
  const [labels, setLabels] = useState({
    title: 'Assessments',
    std: 'Standard',
    ctrl: 'Control ID',
    run: 'Run',
  })
  useEffect(() => {
    let mounted = true
    ;(async () => {
      try {
        const [title, std, ctrl, run] = await Promise.all([
          t('assessments.title'),
          t('assessments.standard.placeholder'),
          t('assessments.control.placeholder'),
          t('btn.run'),
        ])
        if (mounted) setLabels({ title, std, ctrl, run })
      } catch {}
    })()
    return () => {
      mounted = false
    }
  }, [])
  const submit = async (e:React.FormEvent) => {
    e.preventDefault()
    const res = await apiFetch('/api/compliance/check', { method: 'POST', body: { standard, control_id: controlId } })
    setResult(await res.json())
  }
  return (
    <main className="p-md space-y-md">
      <h1 className="text-xl font-semibold">{labels.title}</h1>
      <form onSubmit={submit} className="space-y-sm">
        <input className="border rounded-md p-sm" placeholder={labels.std} value={standard} onChange={e=>setStandard(e.target.value)} />
        <input className="border rounded-md p-sm" placeholder={labels.ctrl} value={controlId} onChange={e=>setControlId(e.target.value)} />
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">{labels.run}</button>
      </form>
      {result && (
        <pre className="bg-bg-inverted text-white p-md rounded-md overflow-auto">{JSON.stringify(result, null, 2)}</pre>
      )}
    </main>
  )
}
