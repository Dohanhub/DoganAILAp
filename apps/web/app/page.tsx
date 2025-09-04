import { t } from '../lib/i18n'

export default async function Home() {
  return (
    <main className="p-md">
      <h1 className="text-2xl font-semibold">{await t('home.title')}</h1>
      <p className="text-fg-muted mt-sm">{await t('home.subtitle')}</p>
    </main>
  )
}
