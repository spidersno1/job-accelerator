import { cookies } from 'next/headers'
import DashboardPage from './page'

export default function ServerDashboardPage() {
  const cookieStore = cookies()
  const token = cookieStore.get('access_token')?.value
  
  if (!token) {
    console.log('未找到access_token cookie，检查以下可能原因:')
    console.log('1. 是否已成功登录并设置cookie')
    console.log('2. cookie domain/path设置是否正确')
    console.log('3. 是否启用了httpOnly/secure标志')
  } else {
    console.log('从cookie获取到access_token:', token ? '存在' : '不存在')
  }

  return <DashboardPage />
}
