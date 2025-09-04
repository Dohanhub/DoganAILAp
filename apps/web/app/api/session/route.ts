import { cookies } from 'next/headers'

export async function POST(req: Request) {
  const form = await req.formData()
  const username = String(form.get('username') || '')
  const password = String(form.get('password') || '')
  if (!username || !password) {
    return new Response(JSON.stringify({ error: 'Missing credentials' }), { status: 400 })
  }
  const base = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8010'
  const body = new URLSearchParams({ username, password })
  const res = await fetch(`${base}/token`, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body })
  if (!res.ok) {
    const txt = await res.text()
    return new Response(txt || 'Login failed', { status: res.status })
  }
  const data = await res.json()
  const token = data?.access_token
  if (!token) return new Response('Bad token response', { status: 500 })
  const c = await cookies()
  const secure = process.env.NODE_ENV === 'production'
  c.set('auth', token, { httpOnly: true, sameSite: 'lax', secure, maxAge: 60 * 30, path: '/' })
  return new Response(JSON.stringify({ ok: true }), { status: 200 })
}

export async function DELETE() {
  const c = await cookies()
  c.set('auth', '', { httpOnly: true, sameSite: 'lax', secure: process.env.NODE_ENV === 'production', maxAge: 0, path: '/' })
  return new Response(JSON.stringify({ ok: true }), { status: 200 })
}
