import { cookies } from 'next/headers'

export async function GET(req: Request) {
  const url = new URL(req.url)
  const path = url.searchParams.get('path') || '/health'
  const base = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8010'
  const target = path.startsWith('http') ? path : `${base}${path}`
  const token = (await cookies()).get('auth')?.value
  const fwdHeaders: Record<string, string> = {}
  if (token) fwdHeaders['Authorization'] = `Bearer ${token}`
  // Forward API/tenant keys if provided by client
  const apiKey = req.headers.get('x-api-key')
  const tenantKey = req.headers.get('x-tenant-key')
  if (apiKey) fwdHeaders['X-API-Key'] = apiKey
  if (tenantKey) fwdHeaders['X-Tenant-Key'] = tenantKey
  const res = await fetch(target, { headers: fwdHeaders, cache: 'no-store' })
  const body = await res.text()
  return new Response(body, { status: res.status, headers: { 'Content-Type': res.headers.get('content-type') || 'application/json' } })
}
