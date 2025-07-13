'use client'

import { Dashboard } from '@/components/Dashboard'
import { redirect } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useAuth, AuthStatus } from '@/components/AuthProvider'
import { isTokenValid } from '@/lib/auth'

export default function DashboardPage() {
  const [token, setToken] = useState<string>('')
  const { isLoggedIn, status } = useAuth()

  useEffect(() => {
    const storedToken = localStorage.getItem('access_token') || ''
    setToken(storedToken)
  }, [])

  useEffect(() => {
    if (status !== AuthStatus.LOADING) {
      if (!isLoggedIn && !isTokenValid(token)) {
        console.log('用户未登录且token无效，重定向到登录页')
        redirect('/login')
      } else if (!isLoggedIn && isTokenValid(token)) {
        console.log('token有效但登录状态未更新，刷新页面')
        window.location.reload()
      }
    }
  }, [isLoggedIn, status, token])

  if (status === AuthStatus.LOADING || !isLoggedIn) {
    return null
  }

  console.log('渲染Dashboard组件')
  return <Dashboard />
}
