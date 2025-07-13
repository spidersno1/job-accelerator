/**
 * 主仪表板组件 - 程序员求职加速器的核心界面
 * 
 * 这个组件是整个应用程序的主要界面，提供以下功能：
 * 
 * 核心功能模块：
 * 1. 技能分析 - 多种方式分析用户技能水平
 * 2. 岗位匹配 - 智能匹配适合的工作机会
 * 3. 学习路径 - 个性化学习建议和进度跟踪
 * 4. 学习进度 - 可视化学习进度和成就
 * 5. AI助手 - 智能对话和建议
 * 
 * 数据可视化：
 * - 技能雷达图显示技能分布
 * - 柱状图显示学习进度
 * - 实时数据更新和状态管理
 * 
 * 技术特性：
 * - 使用React Hooks进行状态管理
 * - Chart.js集成用于数据可视化
 * - 响应式设计适配不同设备
 * - 异步数据获取和错误处理
 * 
 * @author 程序员求职加速器团队
 * @created 2024年
 * @updated 2025年1月
 */

/**
 * 主仪表板组件 - 程序员求职加速器的核心界面
 * 
 * 这个组件是整个应用程序的主要界面，提供以下功能：
 * 
 * 核心功能模块：
 * 1. 技能分析 - 多种方式分析用户技能水平
 * 2. 岗位匹配 - 智能匹配适合的工作机会
 * 3. 学习路径 - 个性化学习建议和进度跟踪
 * 4. 学习进度 - 可视化学习进度和成就
 * 5. AI助手 - 智能对话和建议
 * 
 * 数据可视化：
 * - 技能雷达图显示技能分布
 * - 柱状图显示学习进度
 * - 实时数据更新和状态管理
 * 
 * 技术特性：
 * - 使用React Hooks进行状态管理
 * - Chart.js集成用于数据可视化
 * - 响应式设计适配不同设备
 * - 异步数据获取和错误处理
 * 
 * @author 程序员求职加速器团队
 * @created 2024年
 * @updated 2025年1月
 */

'use client'

import React, { useEffect, useState } from 'react'
import api from '@/lib/api'
import axios from 'axios'
import { BarChart3, BookOpen, Briefcase, Target, TrendingUp, Users, MessageSquare } from 'lucide-react'
import { Radar, Bar } from 'react-chartjs-2'
import { 
  Chart as ChartJS, 
  RadialLinearScale, 
  PointElement, 
  LineElement, 
  Filler, 
  Tooltip, 
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
} from 'chart.js'

// 注册Chart.js所需的组件
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement
)

// 导入子组件
import SkillsMatch from './SkillsMatch'
import { SkillsRadar } from './SkillsRadar'
import { Skill, SkillReport } from '../types/index'
import type { ChartEvent, ActiveElement, TooltipItem } from 'chart.js'
import LeetCodeAnalysis from './LeetCodeAnalysis'
import JobMatching from './JobMatching'
import JobMatchingEnhanced from './JobMatchingEnhanced'
import SkillAnalysis from './SkillAnalysis'
import SkillAnalysisEnhanced from './SkillAnalysisEnhanced'
import LearningPathEnhanced from './LearningPathEnhanced'

interface ProgressTask {
  name: string
  progress: number
  status: string
}

interface ProgressData {
  tasks: ProgressTask[]
  overallProgress: number
}

export function Dashboard() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [report, setReport] = useState<SkillReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzeStatus, setAnalyzeStatus] = useState('')
  const [activeTab, setActiveTab] = useState('overview')
  const [progressData, setProgressData] = useState<ProgressData | null>(null)
  const [loadingProgress, setLoadingProgress] = useState(false)
  const [progressError, setProgressError] = useState<string | null>(null)
  const [selectedTask, setSelectedTask] = useState<ProgressTask | null>(null)

  const fetchProgressData = async () => {
    setLoadingProgress(true)
    setProgressError(null)
    try {
      const response = await api.get('/api/learning-path/progress')
      setProgressData(response.data)
    } catch (error: any) {
      setProgressError(error.message)
    } finally {
      setLoadingProgress(false)
    }
  }

  const chartOptions = {
    responsive: true,
    animation: {
      duration: 1000,
      easing: 'easeOutQuart'
    },
    onClick: (event: ChartEvent, elements: ActiveElement[]) => {
      if (elements.length > 0 && progressData) {
        setSelectedTask(progressData.tasks[elements[0].index])
      }
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (context: TooltipItem<'bar'>) => {
            return `${progressData?.tasks[context.dataIndex].name}: ${context.raw}%`
          }
        }
      }
    }
  }

  useEffect(() => {
    const interval = setInterval(() => {
      if (activeTab === 'progress') {
        fetchProgressData()
      }
    }, 30000) // 每30秒刷新一次
    return () => clearInterval(interval)
  }, [activeTab])

  const tabs = [
    { id: 'overview', name: '概览', icon: BarChart3 },
    { id: 'skills', name: '技能分析', icon: Target },
    { id: 'learning', name: '学习路径', icon: BookOpen },
    { id: 'jobs', name: '岗位匹配', icon: Briefcase },
    { id: 'progress', name: '学习进度', icon: TrendingUp },
    { id: 'agent', name: 'AI助手', icon: Users },
  ]

  useEffect(() => {
    fetchSkills()
    fetchLatestReport()
  }, [])

  const fetchSkills = async () => {
    try {
      const response = await api.get('/api/skills')
      setSkills(response.data)
    } catch (error) {
      console.error('获取技能数据失败:', error)
    }
  }

  const fetchLatestReport = async () => {
    try {
      const response = await api.get('/api/skills/reports/latest')
      setReport(response.data)
    } catch (error) {
      console.error('获取报告失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    try {
      setAnalyzeStatus('processing')
      await axios.post('/api/skills/analyze')
      
      const interval = setInterval(async () => {
        const { data } = await axios.get('/api/skills/reports/latest')
        if (data) {
          setReport(data)
          setAnalyzeStatus('completed')
          clearInterval(interval)
        }
      }, 3000)
    } catch (error) {
      console.error('分析失败:', error)
      setAnalyzeStatus('failed')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">技能分析面板</h1>
          <p className="text-gray-600 mt-2">当前技能数: {skills.length}</p>
        <LeetCodeAnalysis />
        </div>

        <div className="bg-white rounded-lg shadow-sm">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.name}</span>
                  </button>
                )
              })}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'skills' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">技能分析</h3>
                </div>
                <SkillAnalysisEnhanced />
              </div>
            )}

            {activeTab === 'jobs' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">职位匹配</h3>
                </div>
                <JobMatchingEnhanced />
              </div>
            )}

            {activeTab === 'progress' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">学习进度</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-4">进度概览</h4>
                    <div className="h-64">
                      {/* 进度图表将在这里渲染 */}
                      <div className="flex items-center justify-center h-full text-gray-500">
                        进度图表加载中...
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-4">任务状态</h4>
                    <div className="space-y-3">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center justify-between">
                          <span className="text-sm">任务 {i}</span>
                          <div className="w-32 bg-gray-200 rounded-full h-2.5">
                            <div 
                              className="bg-blue-600 h-2.5 rounded-full" 
                              style={{ width: `${i * 30}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'agent' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">AI学习助手</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-4">个性化建议</h4>
                  <div className="space-y-3">
                    {['建议1', '建议2', '建议3'].map((suggestion, i) => (
                      <div key={i} className="p-3 bg-white rounded-md shadow-xs">
                        <p className="text-sm">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'learning' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium text-gray-900">学习路径</h3>
                </div>
                <LearningPathEnhanced />
              </div>
            )}

            {activeTab !== 'skills' && activeTab !== 'jobs' && activeTab !== 'learning' && activeTab !== 'progress' && activeTab !== 'agent' && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {tabs.find(t => t.id === activeTab)?.name}功能
                </h3>
                <p className="text-gray-600">功能正在开发中...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
