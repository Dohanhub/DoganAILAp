import type { Metadata } from 'next';
import { Inter, Noto_Sans_Arabic } from 'next/font/google';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { HelmetProvider } from 'react-helmet-async';
import { I18nextProvider } from 'react-i18next';

import { theme } from '@/config/theme';
import { i18n } from '@/config/i18n';
import { GlobalProvider } from '@/stores/GlobalStore';
import { SocketProvider } from '@/providers/SocketProvider';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { LoadingProvider } from '@/providers/LoadingProvider';
import { NotificationProvider } from '@/providers/NotificationProvider';
import { EnhancedThemeProvider } from '@/components/enhanced/EnhancedTheme';
import { InteractiveFeatures } from '@/components/enhanced/InteractiveFeatures';

import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const notoArabic = Noto_Sans_Arabic({
  subsets: ['arabic'],
  variable: '--font-arabic',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    template: '%s | DoganAI Compliance Platform',
    default: 'DoganAI Compliance Platform - World-Class Enterprise Solution',
  },
  description: 'Advanced compliance evaluation and monitoring platform for Saudi Arabian regulations',
  keywords: [
    'compliance',
    'KSA',
    'Saudi Arabia',
    'regulatory',
    'enterprise',
    'DoganAI',
    'audit',
    'governance',
  ],
  authors: [{ name: 'DoganAI Labs', url: 'https://doganai.com' }],
  creator: 'DoganAI Labs',
  publisher: 'DoganAI Labs',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://compliance.doganai.com'),
  alternates: {
    canonical: '/',
    languages: {
      'ar-SA': '/ar',
      'en-US': '/en',
    },
  },
  openGraph: {
    type: 'website',
    locale: 'ar_SA',
    url: 'https://compliance.doganai.com',
    title: 'DoganAI Compliance Platform',
    description: 'World-class compliance evaluation platform',
    siteName: 'DoganAI Compliance',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DoganAI Compliance Platform',
    description: 'World-class compliance evaluation platform',
    creator: '@DoganAI',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-token',
  },
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 2,
    },
  },
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html 
      lang="ar" 
      dir="rtl" 
      className={`${inter.variable} ${notoArabic.variable}`}
      suppressHydrationWarning
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        <meta name="theme-color" content="#1976d2" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body className="antialiased">
        <HelmetProvider>
          <QueryClientProvider client={queryClient}>
            <AppRouterCacheProvider>
              <EnhancedThemeProvider mode="light">
                <CssBaseline />
                <GlobalProvider>
                  <LoadingProvider>
                    <NotificationProvider>
                      <SocketProvider>
                        <InteractiveFeatures>
                          <div id="root" className="min-h-screen bg-gray-50">
                            {children}
                          </div>
                        </InteractiveFeatures>
                      </SocketProvider>
                    </NotificationProvider>
                  </LoadingProvider>
                </GlobalProvider>
              </EnhancedThemeProvider>
            </AppRouterCacheProvider>
            <ReactQueryDevtools initialIsOpen={false} />
          </QueryClientProvider>
        </HelmetProvider>
      </body>
    </html>
  );
}
