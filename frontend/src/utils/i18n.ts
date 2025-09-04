/**
 * i18n configuration for DoganAI Compliance Kit
 * Supports English and Arabic languages
 */

// Simple i18n implementation
class I18n {
  private currentLanguage: string = 'en'
  private translations: Record<string, Record<string, string>> = {
    en: {
      'dashboard.title': 'Dashboard',
      'settings.title': 'Settings',
      'reports.title': 'Reports',
      // Add more translations as needed
    },
    ar: {
      'dashboard.title': 'لوحة التحكم',
      'settings.title': 'الإعدادات',
      'reports.title': 'التقارير',
      // Add more translations as needed
    }
  }

  changeLanguage(language: string) {
    this.currentLanguage = language
  }

  t(key: string, options?: any): string {
    const translation = this.translations[this.currentLanguage]?.[key]
    if (!translation) {
      console.warn(`Translation missing for key: ${key}`)
      return key
    }
    
    // Simple interpolation if options provided
    if (options) {
      return translation.replace(/\{\{(\w+)\}\}/g, (match, prop) => {
        return options[prop] || match
      })
    }
    
    return translation
  }
}

const i18n = new I18n()
export default i18n
