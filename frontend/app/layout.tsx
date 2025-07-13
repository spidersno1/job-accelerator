/**
 * 根布局组件 - 应用程序的顶层布局
 * 
 * 这个组件定义了整个应用程序的基础布局结构，包括：
 * 1. HTML文档结构和元数据
 * 2. 全局样式导入
 * 3. 认证上下文提供者
 * 4. 公共头部组件
 * 5. 主要内容区域
 * 
 * 技术特性：
 * - 使用Next.js 14的App Router
 * - 支持服务端渲染(SSR)
 * - 响应式设计
 * - 全局状态管理
 * 
 * 组件层次结构：
 * RootLayout
 * ├── AuthProvider (认证上下文)
 * │   ├── Header (全局头部)
 * │   └── main content (页面内容)
 * 
 * @author 程序员求职加速器团队
 * @created 2024年
 * @updated 2025年1月
 */

import type { Metadata } from 'next'
import './globals.css'

import Header from '@/components/Header'
import AuthProvider from '@/components/AuthProvider'

/**
 * 页面元数据配置
 * 
 * 定义应用程序的SEO信息和浏览器显示标题
 */
export const metadata: Metadata = {
  title: '程序员求职加速器Agent',
  description: 'AI驱动的程序员求职助手 - 技能分析、岗位匹配、学习路径生成',
  keywords: ['程序员', '求职', 'AI', '技能分析', '岗位匹配', '学习路径'],
  authors: [{ name: '程序员求职加速器团队' }],
}

/**
 * 视口配置
 * 
 * 定义响应式视口设置，确保在移动设备上正确显示
 */
export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

/**
 * 主题颜色配置
 * 
 * 定义浏览器主题色彩，用于状态栏和地址栏显示
 */
export const themeColor = '#3b82f6'

/**
 * 根布局组件
 * 
 * 为所有页面提供统一的布局结构和全局功能
 * 
 * @param children - 子页面组件
 * @returns JSX.Element - 完整的HTML文档结构
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <head />
      <body className="font-sans">
        {/* 认证上下文提供者 - 管理全局用户状态 */}
        <AuthProvider>
          {/* 全局头部导航 */}
          <Header />
          
          {/* 主要内容区域 */}
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}