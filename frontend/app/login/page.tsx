'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { login } from '@/lib/auth'
import { getDeviceFingerprint } from '@/lib/deviceFingerprint'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    console.log('表单提交触发') 
    e.preventDefault()
    console.log('表单已阻止默认行为')
    try {
      console.log('准备调用login函数', {username})
      const deviceInfo = getDeviceFingerprint()
      const success = await login(username, password, deviceInfo)
      console.log('login函数返回:', success)
      if (success) {
        console.log('登录成功，准备跳转')
        console.log('localStorage token:', localStorage.getItem('access_token'))
        
        // 强制刷新确保状态同步
        window.location.href = '/dashboard?refresh=' + Date.now()
      } else {
        console.log('登录失败，保持当前页面')
        setError('登录失败，请检查用户名和密码')
      }
    } catch (err) {
      console.error('登录捕获错误:', err)
      setError('登录失败，请检查用户名和密码')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-gray-50">
      <form 
        id="login-form"
        onSubmit={handleSubmit} 
        className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg"
        autoComplete="off"
      >
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-800">欢迎回来</h1>
          <p className="text-gray-600">请输入您的账号信息</p>
        </div>
        
        {error && (
          <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
              用户名
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              密码
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <button
          type="submit"
          className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition duration-200"
        >
          登录
        </button>
      </form>
    </div>
  )
}
