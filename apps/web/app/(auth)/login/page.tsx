"use client"
import { useState } from 'react'
import { t } from '../../../lib/i18n'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const body = new URLSearchParams()
    body.append('username', email)
    body.append('password', password)
    const res = await fetch('/api/session', { method: 'POST', body })
    if (res.ok) {
      setMessage('Logged in')
      try { window.location.href = '/diagnostics' } catch {}
    } else {
      setMessage('Login failed')
    }
  }

  return (
    <main className="p-md max-w-md">
      <h1 className="text-xl font-semibold mb-md">{t('login.title')}</h1>
      <form onSubmit={onSubmit} className="space-y-sm">
        <input className="border rounded-md p-sm w-full" placeholder={t('login.email')} value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="border rounded-md p-sm w-full" placeholder={t('login.password')} type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="bg-brand-primary text-white rounded-md px-md py-sm">{t('login.submit')}</button>
      </form>
      {message && <p className="mt-sm text-fg-muted">{message}</p>}
    </main>
  )
}
