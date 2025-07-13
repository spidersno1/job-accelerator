'use client';

import React, { useState, useEffect } from 'react';
import { analyzeSkills, getSkills, testAnalyzeSkills } from '../lib/api';
import { Radar, Bar, Doughnut } from 'react-chartjs-2';
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
  BarElement,
  ArcElement
} from 'chart.js';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement
);

interface SkillAnalysisData {
  status: string;
  message: string;
  statistics: {
    total_skills: number;
    average_proficiency: number;
    by_category: Record<string, {
      count: number;
      average_proficiency: number;
      skills: Array<{
        name: string;
        level: number;
        source: string;
      }>;
    }>;
    top_skills: Array<{
      name: string;
      level: number;
      category: string;
    }>;
    improvement_areas: Array<{
      name: string;
      level: number;
      category: string;
    }>;
  };
  learning_recommendations: Array<{
    skill: string;
    current_level: number;
    target_level: number;
    recommendation: string;
    resources: string[];
  }>;
  analysis_date: string;
}

const SkillAnalysis: React.FC = () => {
  const [analysisData, setAnalysisData] = useState<SkillAnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'details' | 'recommendations'>('overview');

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyzeSkills();
      setAnalysisData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '分析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTestAnalyze = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await testAnalyzeSkills();
      setAnalysisData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '测试分析失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 组件加载时自动进行分析
    handleAnalyze();
  }, []);

  const renderRadarChart = () => {
    if (!analysisData) return null;

    const categories = Object.keys(analysisData.statistics.by_category);
    const data = {
      labels: categories.map(cat => cat.replace('_', ' ').toUpperCase()),
      datasets: [
        {
          label: '技能熟练度',
          data: categories.map(cat => analysisData.statistics.by_category[cat].average_proficiency),
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
        },
      ],
    };

    const options = {
      responsive: true,
      scales: {
        r: {
          angleLines: {
            display: true,
          },
          suggestedMin: 0,
          suggestedMax: 100,
          ticks: {
            stepSize: 20,
          },
        },
      },
    };

    return <Radar data={data} options={options} />;
  };

  const renderBarChart = () => {
    if (!analysisData) return null;

    const topSkills = analysisData.statistics.top_skills.slice(0, 10);
    const data = {
      labels: topSkills.map(skill => skill.name),
      datasets: [
        {
          label: '熟练度',
          data: topSkills.map(skill => skill.level),
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: '技能熟练度排名',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
        },
      },
    };

    return <Bar data={data} options={options} />;
  };

  const renderDoughnutChart = () => {
    if (!analysisData) return null;

    const categories = Object.keys(analysisData.statistics.by_category);
    const data = {
      labels: categories.map(cat => cat.replace('_', ' ').toUpperCase()),
      datasets: [
        {
          data: categories.map(cat => analysisData.statistics.by_category[cat].count),
          backgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
            '#FF9F40',
          ],
          hoverBackgroundColor: [
            '#FF6384',
            '#36A2EB',
            '#FFCE56',
            '#4BC0C0',
            '#9966FF',
            '#FF9F40',
          ],
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'right' as const,
        },
        title: {
          display: true,
          text: '技能分布',
        },
      },
    };

    return <Doughnut data={data} options={options} />;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">正在分析技能...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">技能分析失败</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <div className="mt-4">
              <button
                onClick={handleAnalyze}
                className="bg-red-100 text-red-800 px-3 py-2 rounded-md text-sm font-medium hover:bg-red-200"
              >
                重新分析
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">暂无分析数据</p>
        <button
          onClick={handleAnalyze}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          开始分析
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 分析概览 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">技能分析报告</h2>
          <div className="flex space-x-2">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
            >
              {loading ? '分析中...' : '重新分析'}
            </button>
            <button
              onClick={handleTestAnalyze}
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:bg-green-300"
            >
              {loading ? '测试中...' : '测试分析'}
            </button>
          </div>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-blue-800">总技能数</h3>
            <p className="text-2xl font-bold text-blue-900">{analysisData.statistics.total_skills}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-green-800">平均熟练度</h3>
            <p className="text-2xl font-bold text-green-900">{analysisData.statistics.average_proficiency}%</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-800">技能类别</h3>
            <p className="text-2xl font-bold text-purple-900">{Object.keys(analysisData.statistics.by_category).length}</p>
          </div>
        </div>

        {/* 标签页导航 */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: '概览', icon: '📊' },
              { id: 'details', name: '详情', icon: '📋' },
              { id: 'recommendations', name: '建议', icon: '💡' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* 标签页内容 */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">技能雷达图</h3>
            <div className="h-64">
              {renderRadarChart()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">技能分布</h3>
            <div className="h-64">
              {renderDoughnutChart()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 lg:col-span-2">
            <h3 className="text-lg font-medium text-gray-900 mb-4">技能排名</h3>
            <div className="h-64">
              {renderBarChart()}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'details' && (
        <div className="space-y-6">
          {/* 最强技能 */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">🏆 最强技能</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analysisData.statistics.top_skills.map((skill, index) => (
                <div key={index} className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-800">{skill.name}</h4>
                  <p className="text-sm text-green-600">{skill.category}</p>
                  <div className="mt-2 flex items-center">
                    <div className="flex-1 bg-green-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${skill.level}%` }}
                      ></div>
                    </div>
                    <span className="ml-2 text-sm font-medium text-green-800">{skill.level}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 需要改进的技能 */}
          {analysisData.statistics.improvement_areas.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">🎯 需要改进的技能</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysisData.statistics.improvement_areas.map((skill, index) => (
                  <div key={index} className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-medium text-yellow-800">{skill.name}</h4>
                    <p className="text-sm text-yellow-600">{skill.category}</p>
                    <div className="mt-2 flex items-center">
                      <div className="flex-1 bg-yellow-200 rounded-full h-2">
                        <div
                          className="bg-yellow-600 h-2 rounded-full"
                          style={{ width: `${skill.level}%` }}
                        ></div>
                      </div>
                      <span className="ml-2 text-sm font-medium text-yellow-800">{skill.level}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 按类别详情 */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">📈 按类别详情</h3>
            <div className="space-y-4">
              {Object.entries(analysisData.statistics.by_category).map(([category, data]) => (
                <div key={category} className="border-l-4 border-blue-500 pl-4">
                  <h4 className="font-medium text-gray-900 capitalize">
                    {category.replace('_', ' ')} ({data.count} 项技能)
                  </h4>
                  <p className="text-sm text-gray-600">平均熟练度: {data.average_proficiency}%</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {data.skills.slice(0, 5).map((skill, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {skill.name} ({skill.level}%)
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'recommendations' && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">💡 学习建议</h3>
          {analysisData.learning_recommendations.length > 0 ? (
            <div className="space-y-6">
              {analysisData.learning_recommendations.map((rec, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <h4 className="font-medium text-gray-900">{rec.skill}</h4>
                    <span className="text-sm text-gray-500">
                      {rec.current_level}% → {rec.target_level}%
                    </span>
                  </div>
                  <p className="text-gray-700 mb-3">{rec.recommendation}</p>
                  <div>
                    <h5 className="text-sm font-medium text-gray-900 mb-2">推荐资源:</h5>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {rec.resources.map((resource, idx) => (
                        <li key={idx} className="flex items-center">
                          <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                          {resource}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">🎉 您的技能水平很不错！继续保持并持续学习新技术。</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SkillAnalysis;