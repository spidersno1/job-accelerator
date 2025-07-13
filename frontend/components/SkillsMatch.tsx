'use client'

import React, { useState } from 'react'
import { SkillsMatchProps } from '../types/index'

const SkillsMatch: React.FC<SkillsMatchProps> = ({ skills, learningPath }) => {
  const [activeTab, setActiveTab] = useState<'skills' | 'path'>('skills')
  const [expandedTask, setExpandedTask] = useState<number | null>(null)

  const toggleTaskExpand = (index: number) => {
    setExpandedTask(expandedTask === index ? null : index)
  }

  return (
    <div className="h-full p-4 bg-white rounded-lg shadow">
      <div className="flex border-b mb-4">
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'skills' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('skills')}
        >
          技能匹配
        </button>
        <button
          className={`px-4 py-2 font-medium ${activeTab === 'path' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'}`}
          onClick={() => setActiveTab('path')}
        >
          学习路径
        </button>
      </div>

      {activeTab === 'skills' ? (
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            已掌握 {skills.length} 项技能
          </h3>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {skills.slice(0, 6).map(skill => (
              <div 
                key={skill.id}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
              >
                {skill.skill_name}
              </div>
            ))}
          </div>
          {skills.length > 6 && (
            <p className="text-gray-500 mt-4">+{skills.length - 6} 更多技能...</p>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {learningPath && (
            <>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-900">{learningPath.path_name}</h3>
                <p className="text-sm text-gray-600">{learningPath.description}</p>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full" 
                      style={{ width: `${learningPath.overall_progress || 0}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    已完成 {learningPath.overall_progress || 0}%
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">学习任务</h4>
                {learningPath.tasks.map((task, index) => (
                  <div 
                    key={index} 
                    className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleTaskExpand(index)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h5 className="font-medium">{task.task_name}</h5>
                        <p className="text-sm text-gray-600">{task.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          task.status === 'completed' ? 'bg-green-100 text-green-800' :
                          task.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {task.status === 'completed' ? '已完成' : 
                           task.status === 'in_progress' ? '进行中' : '未开始'}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          task.difficulty === '简单' ? 'bg-blue-100 text-blue-800' :
                          task.difficulty === '中等' ? 'bg-purple-100 text-purple-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {task.difficulty}
                        </span>
                      </div>
                    </div>

                    {expandedTask === index && (
                      <div className="mt-3 pt-3 border-t">
                        <div className="flex justify-between text-sm mb-2">
                          <span>预计耗时: {task.estimated_hours}小时</span>
                          {task.status === 'in_progress' && (
                            <span>进度: {task.progress}%</span>
                          )}
                        </div>
                        {task.resources && (
                          <div className="text-sm">
                            <p className="font-medium mb-1">推荐资源:</p>
                            <div className="space-y-1">
                              {JSON.parse(task.resources).map((resource: string, i: number) => (
                                <a 
                                  key={i} 
                                  href={resource} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:underline block truncate"
                                >
                                  {resource}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {learningPath.ai_suggestions && learningPath.ai_suggestions.length > 0 && (
                <div className="mt-4 bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">AI学习建议</h4>
                  <ul className="list-disc list-inside text-sm text-blue-800 space-y-1">
                    {learningPath.ai_suggestions.map((suggestion, i) => (
                      <li key={i}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default SkillsMatch
