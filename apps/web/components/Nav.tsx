"use client"
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { fetchMe } from '../lib/session'
import { t } from '../lib/i18n'

export function Nav() {
  const [role, setRole] = useState<string>('')
  useEffect(() => { (async () => { const me = await fetchMe(); if (me) setRole(me.role) })() }, [])
  return (
    <nav className="flex gap-md p-md border-b">
      <Link href="/">{t('nav.home')}</Link>
      <Link href="/standards">{t('nav.standards')}</Link>
      <Link href="/regulators">{t('nav.regulators')}</Link>
      <Link href="/vendors">{t('nav.vendors')}</Link>
      <Link href="/connectors">{t('nav.connectors')}</Link>
      <Link href="/assessments">{t('nav.assessments')}</Link>
      <Link href="/evidence">{t('nav.evidence')}</Link>
      <Link href="/reports">{t('nav.reports')}</Link>
      {role === 'admin' && <Link href="/admin">{t('nav.admin')}</Link>}
      <Link className="ml-auto" href="/(auth)/login">{t('nav.login')}</Link>
      <Link href="/settings">{t('nav.settings')}</Link>
    </nav>
  )
}
