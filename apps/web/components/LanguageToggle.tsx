"use client"
import { useEffect, useState } from 'react'

export function LanguageToggle() {
  const [rtl, setRtl] = useState(false)
  useEffect(() => {
    const saved = localStorage.getItem('rtl') === '1'
    setRtl(saved)
    if (saved) document.documentElement.setAttribute('dir','rtl')
  }, [])
  const toggle = () => {
    const next = !rtl
    setRtl(next)
    localStorage.setItem('rtl', next ? '1' : '0')
    document.documentElement.setAttribute('dir', next ? 'rtl' : 'ltr')
  }
  return (
    <button className="border rounded-md px-sm py-xs" onClick={toggle} title="Toggle RTL">
      {rtl ? 'AR' : 'EN'}
    </button>
  )
}

