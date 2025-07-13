'use client'

export function Features() {
  return (
    <div className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            为什么选择我们？
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            基于AI技术，为程序员提供全方位的求职支持，让求职过程更加高效和精准
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="bg-gray-50 p-8 rounded-lg transition-all duration-300 hover:shadow-xl hover:transform hover:-translate-y-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              🎯 精准技能分析
            </h3>
            <p className="text-gray-600">
              通过分析GitHub代码仓库和LeetCode解题记录，准确评估你的技能水平和编程能力
            </p>
          </div>

          <div className="bg-gray-50 p-8 rounded-lg transition-all duration-300 hover:shadow-xl hover:transform hover:-translate-y-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              📚 个性化学习路径
            </h3>
            <p className="text-gray-600">
              AI根据你的技能差距和目标岗位，生成专属的学习计划和资源推荐
            </p>
          </div>

          <div className="bg-gray-50 p-8 rounded-lg transition-all duration-300 hover:shadow-xl hover:transform hover:-translate-y-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              🤖 AI智能督学
            </h3>
            <p className="text-gray-600">
              每日推送个性化学习任务，跟踪学习进度，保持学习动力
            </p>
          </div>

          <div className="bg-gray-50 p-8 rounded-lg transition-all duration-300 hover:shadow-xl hover:transform hover:-translate-y-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              💼 智能岗位匹配
            </h3>
            <p className="text-gray-600">
              基于技能匹配算法，推荐最适合的岗位，提高求职成功率
            </p>
          </div>

          <div className="bg-gray-50 p-8 rounded-lg transition-all duration-300 hover:shadow-xl hover:transform hover:-translate-y-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              📊 数据驱动决策
            </h3>
            <p className="text-gray-600">
              提供详细的技能报告和求职建议，帮助你做出明智的职业决策
            </p>
          </div>

          <div className="bg-gray-50 p-8 rounded-lg transition-all duration-300 hover:shadow-xl hover:transform hover:-translate-y-1">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              🚀 持续优化
            </h3>
            <p className="text-gray-600">
              系统不断学习和优化，为你提供越来越精准的求职建议
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
