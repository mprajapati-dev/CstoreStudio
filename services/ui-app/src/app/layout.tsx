import './globals.css'
import type { Metadata } from 'next'
import AuthWrapper from '@/components/AuthWrapper'

export const metadata: Metadata = {
  title: 'CstoreStudio',
  description: 'AI-agentic maintenance platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <AuthWrapper>
          {children}
        </AuthWrapper>
      </body>
    </html>
  )
}
