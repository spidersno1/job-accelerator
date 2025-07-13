/**
 * 认证中间件 - 处理路由级别的认证逻辑
 * 1. 检查访问权限(受保护路由/认证路由)
 * 2. 验证JWT token有效性
 * 3. 处理强制登出逻辑
 */
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { cookies } from 'next/headers'
import jwtDecode from 'jwt-decode'

// 需要登录才能访问的路由
const protectedRoutes = ['/dashboard', '/settings']
// 已登录用户不应访问的路由(如登录/注册页)
const authRoutes = ['/login', '/register']

/**
 * 认证中间件主逻辑
 * @param request 请求对象
 * @returns 重定向响应或继续请求
 */
export async function middleware(request: NextRequest) {
  // 检查是否有强制退出参数
  const url = new URL(request.url)
  if (url.searchParams.has('logout')) {
    console.log('检测到logout参数，强制清除认证状态')
    const response = NextResponse.redirect(new URL('/login', request.url))
    // 强制清除所有cookie变体
    const domains = [
      request.nextUrl.hostname,
      `.${request.nextUrl.hostname}`,
      request.nextUrl.hostname.split('.').slice(-2).join('.'),
      `.${request.nextUrl.hostname.split('.').slice(-2).join('.')}`
    ]
    
    const paths = ['/', '/dashboard', '/login']
    const cookieNames = ['access_token', 'refresh_token', 'session', 'auth']
    
    domains.forEach(domain => {
      paths.forEach(path => {
        cookieNames.forEach(name => {
          response.cookies.set(name, '', {
            path,
            domain,
            expires: new Date(0),
            httpOnly: true,
            secure: request.nextUrl.protocol === 'https:'
          })
        })
      })
    })
    
    // 添加严格的缓存控制头
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    response.headers.set('Pragma', 'no-cache')
    response.headers.set('Expires', '0')
    response.headers.set('Clear-Site-Data', '"cookies", "storage", "cache"')
    
    // 添加额外的清除参数
    const redirectUrl = new URL('/login', request.nextUrl)
    redirectUrl.searchParams.set('logout', Date.now().toString())
    redirectUrl.searchParams.set('no-cache', '1')
    redirectUrl.searchParams.set('force', '1')
    // 确保完全清除所有可能的认证状态
    const finalResponse = NextResponse.redirect(redirectUrl)
    // 强制清除access_token（确保覆盖所有情况）
    const clearAccessToken = (response: NextResponse) => {
      const domains = [
        request.nextUrl.hostname,
        `.${request.nextUrl.hostname}`,
        request.nextUrl.hostname.split('.').slice(-2).join('.'),
        `.${request.nextUrl.hostname.split('.').slice(-2).join('.')}`
      ]
      const paths = ['/', '/dashboard', '/login']
      
      domains.forEach(domain => {
        paths.forEach(path => {
          response.cookies.set('access_token', '', {
            path,
            domain,
            expires: new Date(0),
            httpOnly: true,
            secure: request.nextUrl.protocol === 'https:'
          })
        })
      })
      return response
    }

    // 先清除所有cookie
    cookieNames.forEach(name => {
      domains.forEach(domain => {
        paths.forEach(path => {
          finalResponse.cookies.set(name, '', {
            path,
            domain,
            expires: new Date(0),
            httpOnly: true,
            secure: request.nextUrl.protocol === 'https:'
          })
        })
      })
    })
    
    // 再专门清除access_token并返回
    return clearAccessToken(finalResponse)
  }


  const token = request.cookies.get('access_token')?.value
  console.log('Middleware token check:', token ? 'exists' : 'missing')
  
  if (token) {
    try {
      const decoded = jwtDecode<{exp?: number}>(token)
      if (!decoded.exp || Date.now() >= decoded.exp * 1000) {
        console.log('Token expired, redirecting to login')
        return NextResponse.redirect(new URL('/login', request.url))
      }
    } catch {
      console.log('Invalid token, redirecting to login')
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }
  const { pathname } = request.nextUrl

  // 如果访问的是受保护路由且未登录
  if (protectedRoutes.some(route => pathname.startsWith(route)) && !token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // 如果访问的是认证路由且已登录
  if (authRoutes.includes(pathname) && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

// 中间件配置 - 匹配所有路由除了指定的排除项
export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
