/**
 * I18n Provider - Internationalization support for Arabic and English
 */

import React, { createContext, useContext, useEffect, useState } from 'react'
import i18n from '../utils/i18n'

type Language = 'en' | 'ar'

type I18nProviderProps = {
  children: React.ReactNode
  defaultLanguage?: Language
}

type I18nProviderState = {
  language: Language
  setLanguage: (language: Language) => void
  t: (key: string, options?: any) => string
  dir: 'ltr' | 'rtl'
}

const I18nProviderContext = createContext<I18nProviderState | undefined>(undefined)

export function I18nProvider({
  children,
  defaultLanguage = 'en',
}: I18nProviderProps) {
  const [language, setLanguage] = useState<Language>(
    () => (localStorage.getItem('doganai-language') as Language) || defaultLanguage
  )

  useEffect(() => {
    // Change i18n language
    i18n.changeLanguage(language)
    
    // Set document direction and language
    document.documentElement.lang = language
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr'
    
    // Store preference
    localStorage.setItem('doganai-language', language)
  }, [language])

  const t = (key: string, options?: any) => {
    return i18n.t(key, options)
  }

  const value: I18nProviderState = {
    language,
    setLanguage,
    t,
    dir: language === 'ar' ? 'rtl' : 'ltr',
  }

  return (
    <I18nProviderContext.Provider value={value}>
      {children}
    </I18nProviderContext.Provider>
  )
}

export const useI18n = () => {
  const context = useContext(I18nProviderContext)
  if (context === undefined) {
    throw new Error('useI18n must be used within an I18nProvider')
  }
  return context
}