'use client'

import { Code, Target, TrendingUp, Users } from 'lucide-react'

export function Hero() {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 animate-fade-in-up">
            AI驱动的程序员求职助手
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-blue-100">
            分析技能、生成学习路径、匹配岗位，让求职更高效
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
              开始使用
            </button>
            <button className="bg-gradient-to-r from-blue-400 to-blue-500 text-white px-8 py-3 rounded-lg font-semibold hover:from-blue-500 hover:to-blue-600 transition-all duration-300 transform hover:scale-105">
              了解更多
            </button>
          </div>
        </div>

          <div className="mt-16 grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center transition-all duration-300 hover:transform hover:scale-105">
              <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 hover:bg-white/20 transition-colors">
                <Code size={32} />
              </div>
            <h3 className="text-lg font-semibold mb-2">技能分析</h3>
            <p className="text-blue-100">基于GitHub和LeetCode数据智能分析技能水平</p>
          </div>
          
          <div className="text-center">
            <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Target size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">学习路径</h3>
            <p className="text-blue-100">AI生成个性化学习路径，针对性提升技能</p>
          </div>
          
          <div className="text-center">
            <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <TrendingUp size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">每日督学</h3>
            <p className="text-blue-100">AI智能督学，保持学习动力和进度</p>
          </div>
          
          <div className="text-center">
            <div className="bg-white/10 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Users size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">岗位匹配</h3>
            <p className="text-blue-100">智能匹配高契合度岗位，提高求职成功率</p>
          </div>
        </div>
      </div>
    </div>
  )
}
