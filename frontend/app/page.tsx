'use client'

import { useAuth } from '@/components/AuthProvider'
import { Hero } from '@/components/Hero'
import { Features } from '@/components/Features'

export default function Home() {
  const { isLoggedIn } = useAuth()

  if (isLoggedIn) {
    window.location.href = '/dashboard'
    return null
  }

  return (
    <main>
      <Hero />
      <Features />
    </main>
  )
}
