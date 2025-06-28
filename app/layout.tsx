import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Valuefy - AI Data Query System',
  description: 'Intelligent data query system for wealth management insights',
  generator: 'Next.js',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
