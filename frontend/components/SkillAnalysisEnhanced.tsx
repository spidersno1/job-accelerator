import { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  ArcElement
} from 'chart.js';
import { Bar, Radar, Doughnut } from 'react-chartjs-2';
import CodeUploader from './CodeUploader';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  ArcElement
);

/**
 * 上传数据类型定义
 */
type UploadData = {
  type: 'file' | 'text' | 'image';
  content: string | File;
  filename?: string;
};

/**
 * 技能数据类型定义
 */
type SkillData = {
  name: string;
  category: string;
  proficiency_level: number;
  source: string;
  evidence: any;
  created_at?: string;
};

/**
 * 分析报告类型定义
 */
type AnalysisReport = {
  overview: {
    total_skills: number;
    average_proficiency: number;
    categories: string[];
    top_skills: Array<{name: string; level: number}>;
    improvement_areas: Array<{name: string; level: number}>;
  };
  details: {
    skills_by_category: Record<string, SkillData[]>;
    skill_distribution: {
      beginner: number;
      intermediate: number;
      advanced: number;
    };
  };
  recommendations: {
    learning_suggestions: Array<{
      skill: string;
      current_level: number;
      suggestion: string;
      resources?: string[];
    }>;
    skill_gaps: string[];
    next_steps: string[];
  };
};

/**
 * 技能分析增强组件
 * 
 * 提供多种方式的技能分析功能：
 * - 文件上传分析
 * - 文本内容分析
 * - 图片OCR分析
 * 
 * 功能特点：
 * - 可视化技能分布
 * - 详细的技能报告
 * - 学习建议推荐
 * - 实时分析结果
 */
const SkillAnalysisEnhanced = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'analysis'>('upload');
  const [uploadedData, setUploadedData] = useState<UploadData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [analysisReport, setAnalysisReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  /**
   * 处理文件上传
   * @param data 上传的数据
   */
  const handleUpload = (data: UploadData) => {
    setUploadedData(data);
    setError(null);
    setSuccessMessage(null);
    console.log('上传数据:', data);
  };

  /**
   * 处理代码分析
   * 发送上传的数据到后端进行分析
   */
  const handleAnalyze = async () => {
    if (!uploadedData) {
      setError('请先上传数据');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const formData = new FormData();
      
      // 根据上传类型构建表单数据
      if (uploadedData.type === 'text') {
        formData.append('text_content', uploadedData.content as string);
        formData.append('analysis_type', 'text');
      } else {
        formData.append('file', uploadedData.content as File);
        formData.append('analysis_type', uploadedData.type);
      }

      // 发送分析请求
      const response = await fetch('/api/skills/analyze-code', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || errorData.detail || `分析失败: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        // 分析成功，显示成功消息
        setSuccessMessage('代码分析成功！正在生成技能报告...');
        console.log('技能分析成功:', result);
        
        // 获取详细的技能分析报告
        await fetchAnalysisReport();
        
        // 切换到分析结果页面
        setActiveTab('analysis');
      } else {
        setError(result.message || '分析失败，请检查上传的内容');
      }

    } catch (error) {
      console.error('分析失败:', error);
      setError(error instanceof Error ? error.message : '分析失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * 获取技能分析报告
   * 从后端获取用户的技能分析详细报告
   */
  const fetchAnalysisReport = async () => {
    try {
      const response = await fetch('/api/skills/analyze', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('获取分析报告失败');
      }

      const report = await response.json();
      setAnalysisReport(report);
      console.log('技能分析报告:', report);
    } catch (error) {
      console.error('获取分析报告失败:', error);
      setError('获取分析报告失败，请稍后重试');
    }
  };

  /**
   * 生成雷达图数据
   * 用于技能分布的可视化展示
   */
  const generateRadarData = () => {
    if (!analysisReport) return null;

    const categories = analysisReport.overview.categories;
    const data = categories.map(category => {
      const skillsInCategory = analysisReport.details.skills_by_category[category] || [];
      return skillsInCategory.reduce((sum, skill) => sum + skill.proficiency_level, 0) / skillsInCategory.length || 0;
    });

    return {
      labels: categories,
      datasets: [
        {
          label: '技能熟练度',
          data: data,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
        }
      ]
    };
  };

  /**
   * 生成环形图数据
   * 用于技能分布的比例展示
   */
  const generateDoughnutData = () => {
    if (!analysisReport) return null;

    const distribution = analysisReport.details.skill_distribution;
    
    return {
      labels: ['初级', '中级', '高级'],
      datasets: [
        {
          data: [distribution.beginner, distribution.intermediate, distribution.advanced],
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 205, 86, 1)'
          ],
          borderWidth: 1
        }
      ]
    };
  };

  /**
   * 生成柱状图数据
   * 用于顶级技能的展示
   */
  const generateBarData = () => {
    if (!analysisReport) return null;

    const topSkills = analysisReport.overview.top_skills;
    
    return {
      labels: topSkills.map(skill => skill.name),
      datasets: [
        {
          label: '熟练度',
          data: topSkills.map(skill => skill.level),
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }
      ]
    };
  };

  // 在组件加载时获取分析报告
  useEffect(() => {
    fetchAnalysisReport();
  }, []);

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* 标题 */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">🔍 技能分析系统</h1>
        <p className="text-gray-600">上传代码文件、输入文本或图片，获取详细的技能分析报告</p>
      </div>

      {/* 标签页导航 */}
      <div className="mb-6">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('upload')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'upload'
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📁 上传分析
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`px-6 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'analysis'
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
            disabled={!analysisReport}
          >
            📊 技能分析
          </button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">❌ {error}</p>
        </div>
      )}

      {/* 成功消息 */}
      {successMessage && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-green-600">✅ {successMessage}</p>
        </div>
      )}

             {/* 上传分析页面 */}
       {activeTab === 'upload' && (
         <div className="space-y-6">
           <CodeUploader 
             onUpload={handleUpload} 
             onAnalyze={handleAnalyze}
             isLoading={isLoading}
             uploadedData={uploadedData}
           />
         </div>
       )}

      {/* 分析结果页面 */}
      {activeTab === 'analysis' && analysisReport && (
        <div className="space-y-6">
          {/* 概览统计 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">总技能数</h3>
              <p className="text-2xl font-bold">{analysisReport.overview.total_skills}</p>
            </div>
            <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">平均熟练度</h3>
              <p className="text-2xl font-bold">{analysisReport.overview.average_proficiency.toFixed(1)}%</p>
            </div>
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">技能类别</h3>
              <p className="text-2xl font-bold">{analysisReport.overview.categories.length}</p>
            </div>
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 rounded-lg">
              <h3 className="text-lg font-semibold">改进领域</h3>
              <p className="text-2xl font-bold">{analysisReport.overview.improvement_areas.length}</p>
            </div>
          </div>

          {/* 图表区域 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 雷达图 */}
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="text-lg font-semibold mb-4">📊 技能分布雷达图</h3>
              {generateRadarData() && (
                <div className="h-64">
                  <Radar 
                    data={generateRadarData()!} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                      },
                    }}
                  />
                </div>
              )}
            </div>

            {/* 环形图 */}
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="text-lg font-semibold mb-4">🍩 技能水平分布</h3>
              {generateDoughnutData() && (
                <div className="h-64">
                  <Doughnut 
                    data={generateDoughnutData()!} 
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </div>
              )}
            </div>
          </div>

          {/* 柱状图 */}
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">🏆 顶级技能排名</h3>
            {generateBarData() && (
              <div className="h-64">
                <Bar 
                  data={generateBarData()!} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                      },
                    },
                  }}
                />
              </div>
            )}
          </div>

          {/* 学习建议 */}
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">💡 学习建议</h3>
            <div className="space-y-3">
              {analysisReport.recommendations.learning_suggestions.map((suggestion, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-md">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-gray-800">{suggestion.skill}</h4>
                      <p className="text-gray-600 text-sm">{suggestion.suggestion}</p>
                    </div>
                    <span className="text-sm text-gray-500">当前: {suggestion.current_level}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 技能详细信息 */}
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">📋 技能详细信息</h3>
            <div className="space-y-4">
              {Object.entries(analysisReport.details.skills_by_category).map(([category, skills]) => (
                <div key={category} className="border rounded-lg p-4">
                  <h4 className="font-semibold text-lg mb-3">{category}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {skills.map((skill, index) => (
                      <div key={index} className="bg-gray-50 p-3 rounded-md">
                        <div className="flex justify-between items-center">
                          <span className="font-medium">{skill.name}</span>
                          <span className="text-sm text-gray-500">{skill.proficiency_level}%</span>
                        </div>
                        <div className="mt-2 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${skill.proficiency_level}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 无分析报告时的提示 */}
      {activeTab === 'analysis' && !analysisReport && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📊</div>
          <h3 className="text-lg font-semibold text-gray-600 mb-2">暂无分析报告</h3>
          <p className="text-gray-500">请先上传代码文件进行分析</p>
          <button
            onClick={() => setActiveTab('upload')}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            🚀 立即上传
          </button>
        </div>
      )}
    </div>
  );
};

export default SkillAnalysisEnhanced; 