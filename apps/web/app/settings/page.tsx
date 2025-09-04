"use client"
import { useEffect, useState } from 'react'
import { t } from '../../lib/i18n'

export default function Settings() {
  const [apiBase, setApiBase] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [tenantKey, setTenantKey] = useState('')
  const [token, setToken] = useState('')
  const [lang, setLang] = useState<'en'|'ar'>('en')
  const [msg, setMsg] = useState('')
  useEffect(() => {
    if (typeof window !== 'undefined') {
      setApiBase(localStorage.getItem('apiBase') || '')
      setApiKey(localStorage.getItem('apiKey') || '')
      setTenantKey(localStorage.getItem('tenantKey') || '')
      setToken(localStorage.getItem('token') || '')
      const l = (localStorage.getItem('lang') as 'en'|'ar') || (document.documentElement.getAttribute('lang') as any) || 'en'
      setLang(l === 'ar' ? 'ar' : 'en')
    }
  }, [])
  const save = (e: React.FormEvent) => {
    e.preventDefault()
    localStorage.setItem('apiBase', apiBase)
    localStorage.setItem('apiKey', apiKey)
    localStorage.setItem('tenantKey', tenantKey)
    localStorage.setItem('token', token)
    localStorage.setItem('lang', lang)
    document.documentElement.setAttribute('lang', lang)
    document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr')
    setMsg('Saved')
  }
  return (
    <main className="p-md space-y-sm max-w-xl">
      <h1 className="text-xl font-semibold">{t('settings.title')}</h1>
      <form onSubmit={save} className="space-y-sm">
        <input className="border rounded-md p-sm w-full" placeholder={`${t('settings.apiBase')} (e.g. http://localhost:8010)`} value={apiBase} onChange={e=>setApiBase(e.target.value)} />
        <input className="border rounded-md p-sm w-full" placeholder={t('settings.apiKey')} value={apiKey} onChange={e=>setApiKey(e.target.value)} />
        <input className="border rounded-md p-sm w-full" placeholder={t('settings.tenantKey')} value={tenantKey} onChange={e=>setTenantKey(e.target.value)} />
        <input className="border rounded-md p-sm w-full" placeholder={t('settings.token')} value={token} onChange={e=>setToken(e.target.value)} />
        <label className="block text-sm text-fg-muted">{t('settings.language')}</label>
        <select className="border rounded-md p-sm" value={lang} onChange={e=>setLang(e.target.value as any)}>
          <option value="en">{t('lang.en')}</option>
          <option value="ar">{t('lang.ar')}</option>
        </select>
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">{t('btn.save')}</button>
      </form>
      {msg && <p className="text-fg-muted">{msg}</p>}
    </main>
  )
}
