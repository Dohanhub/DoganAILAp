import './globals.css'
import '@doganai/tokens/dist/css/variables.css'
import '../src/styles/theme.css'
import { ReactNode } from 'react'
import { Nav } from '../components/Nav'
import { LanguageToggle } from '../components/LanguageToggle'

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-bg-base text-fg-base">
        <div className="flex items-center justify-between">
          <Nav />
          <div className="p-md"><LanguageToggle /></div>
        </div>
        {children}
      </body>
    </html>
  )
}
