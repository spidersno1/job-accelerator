import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { 
  Search, 
  TrendingUp, 
  Award, 
  Code, 
  Target, 
  BookOpen,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  Brain,
  Trophy,
  Star,
  RefreshCw,
  Download,
  Share2,
  Filter,
  BarChart3,
  PieChart as PieChartIcon,
  Activity
} from 'lucide-react';

// LeetCode 数据类型定义
export interface LeetCodeData {
  stats: {
    easy: number;
    medium: number;
    hard: number;
  };
  languages: string[];
}

// 类型定义
interface LeetCodeAnalysisResult {
  user_profile: {
    username: string;
    real_name?: string;
    avatar?: string;
    location?: string;
    company?: string;
    ranking?: number;
    reputation?: number;
    contest_rating?: number;
    contest_ranking?: number;
    contest_attended?: number;
    badges?: Array<{
      id: string;
      displayName: string;
      icon: string;
    }>;
  };
  skill_analysis: {
    programming_languages: Record<string, {
      problems_solved: number;
      proficiency_score: number;
      usage_percentage: number;
      level: string;
    }>;
    algorithms: Record<string, {
      solved_count: number;
      total_submissions: number;
      accuracy_rate: number;
      skill_score: number;
      level: string;
    }>;
    data_structures: Record<string, {
      proficiency_score: number;
      estimated_usage: number;
      level: string;
      confidence: string;
    }>;
    problem_solving: {
      accuracy: {
        rate: number;
        level: string;
        total_accepted: number;
        total_submissions: number;
      };
      consistency: {
        score: number;
        level: string;
      };
      efficiency: {
        score: number;
        level: string;
      };
      progression: {
        score: number;
        level: string;
      };
    };
    overall_assessment: {
      overall_score: number;
      level: string;
      strengths: string[];
      areas_for_improvement: string[];
      next_steps: string[];
    };
  };
  performance_metrics: {
    basic_stats: {
      total_problems_solved: number;
      easy_solved: number;
      medium_solved: number;
      hard_solved: number;
    };
    difficulty_distribution: {
      easy_percentage: number;
      medium_percentage: number;
      hard_percentage: number;
      balance_score: number;
    };
    skill_intensity: {
      score: number;
      level: string;
    };
    learning_curve: {
      current_stage: string;
      stage_progress: number;
      total_problems: number;
      estimated_level: string;
    };
  };
  learning_recommendations: Array<{
    type: string;
    priority: string;
    title: string;
    description: string;
    suggested_topics?: string[];
    target_count?: number;
    estimated_time: string;
  }>;
  competitive_ranking: {
    current_rating: number;
    global_ranking: number;
    contests_attended: number;
    top_percentage: number;
    rating_trend: string;
    performance_level: string;
    status?: string;
  };
  problem_solving_patterns: {
    time_distribution: any;
    solving_strategy: {
      type: string;
      characteristics: string[];
    };
    error_patterns: Record<string, {
      error_rate: number;
      level: string;
    }>;
    learning_path: {
      current_phase: string;
      next_milestone: {
        target: number | string;
        remaining: number;
        progress: number;
        estimated_time: string;
      };
      recommended_focus: string[];
    };
  };
}

interface LeetCodeAnalysisProps {
  onAnalysisComplete?: (result: LeetCodeAnalysisResult) => void;
}

const LeetCodeAnalysis: React.FC<LeetCodeAnalysisProps> = ({ onAnalysisComplete }) => {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<LeetCodeAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchHistory, setSearchHistory] = useState<string[]>([]);

  // 颜色主题
  const colors = {
    primary: '#3B82F6',
    secondary: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    success: '#22C55E',
    info: '#06B6D4',
    purple: '#8B5CF6',
    pink: '#EC4899'
  };

  const difficultyColors = {
    Easy: colors.success,
    Medium: colors.warning,
    Hard: colors.danger
  };

  // 分析LeetCode用户
  const analyzeLeetCode = useCallback(async () => {
    if (!username.trim()) {
      setError('请输入LeetCode用户名或URL');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/skills/analyze-leetcode', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          username_or_url: username.trim()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || errorData.detail || '分析失败');
      }

      const result = await response.json();
      setAnalysisResult(result);
      
      // 更新搜索历史
      setSearchHistory(prev => {
        const newHistory = [username, ...prev.filter(item => item !== username)];
        return newHistory.slice(0, 5); // 只保留最近5个
      });

      // 调用回调函数
      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }

    } catch (err) {
      console.error('LeetCode分析失败:', err);
      setError(err instanceof Error ? err.message : '分析失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  }, [username, onAnalysisComplete]);

  // 获取等级颜色
  const getLevelColor = (level: string) => {
    switch (level) {
      case '专家':
        return colors.purple;
      case '高级':
        return colors.primary;
      case '中级':
        return colors.secondary;
      case '初级':
        return colors.warning;
      default:
        return colors.info;
    }
  };

  // 获取优先级颜色
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return colors.danger;
      case 'medium':
        return colors.warning;
      case 'low':
        return colors.success;
      default:
        return colors.info;
    }
  };

  // 渲染用户档案
  const renderUserProfile = () => {
    if (!analysisResult) return null;

    const { user_profile } = analysisResult;

    return (
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-500" />
            用户档案
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="font-medium">用户名:</span>
                <span>{user_profile.username}</span>
              </div>
              {user_profile.real_name && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">真实姓名:</span>
                  <span>{user_profile.real_name}</span>
                </div>
              )}
              {user_profile.company && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">公司:</span>
                  <span>{user_profile.company}</span>
                </div>
              )}
              {user_profile.location && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">地区:</span>
                  <span>{user_profile.location}</span>
                </div>
              )}
            </div>
            
            <div className="space-y-2">
              {user_profile.ranking && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">全球排名:</span>
                  <Badge variant="outline">{user_profile.ranking.toLocaleString()}</Badge>
                </div>
              )}
              {user_profile.reputation && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">声誉:</span>
                  <Badge variant="outline">{user_profile.reputation}</Badge>
                </div>
              )}
              {user_profile.contest_rating && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">竞赛评分:</span>
                  <Badge 
                    variant="outline"
                    style={{ 
                      backgroundColor: user_profile.contest_rating > 1800 ? colors.purple : 
                                     user_profile.contest_rating > 1500 ? colors.primary : 
                                     user_profile.contest_rating > 1200 ? colors.secondary : colors.warning,
                      color: 'white'
                    }}
                  >
                    {user_profile.contest_rating}
                  </Badge>
                </div>
              )}
              {user_profile.contest_attended && (
                <div className="flex items-center gap-2">
                  <span className="font-medium">参赛次数:</span>
                  <span>{user_profile.contest_attended}</span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              {user_profile.badges && user_profile.badges.length > 0 && (
                <div>
                  <span className="font-medium">徽章:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {user_profile.badges.slice(0, 3).map((badge, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {badge.displayName}
                      </Badge>
                    ))}
                    {user_profile.badges.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{user_profile.badges.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // 渲染技能分析
  const renderSkillAnalysis = () => {
    if (!analysisResult) return null;

    const { skill_analysis } = analysisResult;

    return (
      <div className="space-y-6">
        {/* 编程语言技能 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5 text-blue-500" />
              编程语言技能
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(skill_analysis.programming_languages).map(([lang, data]) => (
                <div key={lang} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{lang}</span>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="outline"
                        style={{ 
                          backgroundColor: getLevelColor(data.level),
                          color: 'white'
                        }}
                      >
                        {data.level}
                      </Badge>
                      <span className="text-sm text-gray-600">
                        {data.problems_solved} 题
                      </span>
                    </div>
                  </div>
                  <Progress value={data.proficiency_score} className="h-2" />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>熟练度: {data.proficiency_score.toFixed(1)}</span>
                    <span>使用率: {data.usage_percentage.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 算法技能 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-500" />
              算法技能
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(skill_analysis.algorithms).map(([algo, data]) => (
                <div key={algo} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium capitalize">
                      {algo.replace('_', ' ')}
                    </span>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="outline"
                        style={{ 
                          backgroundColor: getLevelColor(data.level),
                          color: 'white'
                        }}
                      >
                        {data.level}
                      </Badge>
                      <span className="text-sm text-gray-600">
                        {data.solved_count} 题
                      </span>
                    </div>
                  </div>
                  <Progress value={data.skill_score} className="h-2" />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>技能分数: {data.skill_score.toFixed(1)}</span>
                    <span>准确率: {data.accuracy_rate.toFixed(1)}%</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 解题能力 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-green-500" />
              解题能力分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">准确率</span>
                  <Badge 
                    variant="outline"
                    style={{ 
                      backgroundColor: getLevelColor(skill_analysis.problem_solving.accuracy.level),
                      color: 'white'
                    }}
                  >
                    {skill_analysis.problem_solving.accuracy.level}
                  </Badge>
                </div>
                <Progress value={skill_analysis.problem_solving.accuracy.rate} className="h-2" />
                <div className="text-sm text-gray-600">
                  {skill_analysis.problem_solving.accuracy.rate.toFixed(1)}% 
                  ({skill_analysis.problem_solving.accuracy.total_accepted}/
                  {skill_analysis.problem_solving.accuracy.total_submissions})
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">一致性</span>
                  <Badge 
                    variant="outline"
                    style={{ 
                      backgroundColor: getLevelColor(skill_analysis.problem_solving.consistency.level),
                      color: 'white'
                    }}
                  >
                    {skill_analysis.problem_solving.consistency.level}
                  </Badge>
                </div>
                <Progress value={skill_analysis.problem_solving.consistency.score} className="h-2" />
                <div className="text-sm text-gray-600">
                  {skill_analysis.problem_solving.consistency.score.toFixed(1)}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">效率</span>
                  <Badge 
                    variant="outline"
                    style={{ 
                      backgroundColor: getLevelColor(skill_analysis.problem_solving.efficiency.level),
                      color: 'white'
                    }}
                  >
                    {skill_analysis.problem_solving.efficiency.level}
                  </Badge>
                </div>
                <Progress value={skill_analysis.problem_solving.efficiency.score} className="h-2" />
                <div className="text-sm text-gray-600">
                  {skill_analysis.problem_solving.efficiency.score.toFixed(1)}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">进阶能力</span>
                  <Badge 
                    variant="outline"
                    style={{ 
                      backgroundColor: getLevelColor(skill_analysis.problem_solving.progression.level),
                      color: 'white'
                    }}
                  >
                    {skill_analysis.problem_solving.progression.level}
                  </Badge>
                </div>
                <Progress value={skill_analysis.problem_solving.progression.score} className="h-2" />
                <div className="text-sm text-gray-600">
                  {skill_analysis.problem_solving.progression.score.toFixed(1)}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 整体评估 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-500" />
              整体评估
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold mb-2">
                  {skill_analysis.overall_assessment.overall_score.toFixed(1)}
                </div>
                <Badge 
                  variant="outline"
                  className="text-lg px-4 py-2"
                  style={{ 
                    backgroundColor: getLevelColor(skill_analysis.overall_assessment.level),
                    color: 'white'
                  }}
                >
                  {skill_analysis.overall_assessment.level}
                </Badge>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-green-600 mb-2">优势领域</h4>
                  <div className="space-y-1">
                    {skill_analysis.overall_assessment.strengths.map((strength, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm">{strength}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-orange-600 mb-2">改进领域</h4>
                  <div className="space-y-1">
                    {skill_analysis.overall_assessment.areas_for_improvement.map((area, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-orange-500" />
                        <span className="text-sm">{area}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-blue-600 mb-2">下一步建议</h4>
                <div className="space-y-1">
                  {skill_analysis.overall_assessment.next_steps.map((step, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <Target className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  // 渲染性能指标
  const renderPerformanceMetrics = () => {
    if (!analysisResult) return null;

    const { performance_metrics } = analysisResult;
    
    // 准备难度分布数据
    const difficultyData = [
      {
        name: '简单',
        count: performance_metrics.basic_stats.easy_solved,
        percentage: performance_metrics.difficulty_distribution.easy_percentage,
        color: difficultyColors.Easy
      },
      {
        name: '中等',
        count: performance_metrics.basic_stats.medium_solved,
        percentage: performance_metrics.difficulty_distribution.medium_percentage,
        color: difficultyColors.Medium
      },
      {
        name: '困难',
        count: performance_metrics.basic_stats.hard_solved,
        percentage: performance_metrics.difficulty_distribution.hard_percentage,
        color: difficultyColors.Hard
      }
    ];

    return (
      <div className="space-y-6">
        {/* 基础统计 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-blue-500" />
              基础统计
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {performance_metrics.basic_stats.total_problems_solved}
                </div>
                <div className="text-sm text-gray-600">总题数</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {performance_metrics.basic_stats.easy_solved}
                </div>
                <div className="text-sm text-gray-600">简单</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {performance_metrics.basic_stats.medium_solved}
                </div>
                <div className="text-sm text-gray-600">中等</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {performance_metrics.basic_stats.hard_solved}
                </div>
                <div className="text-sm text-gray-600">困难</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 难度分布图表 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChartIcon className="h-5 w-5 text-purple-500" />
              难度分布
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={difficultyData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name} ${percentage.toFixed(1)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {difficultyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={difficultyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#8884d8">
                      {difficultyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 技能强度和学习曲线 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                技能强度
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center space-y-4">
                <div className="text-3xl font-bold">
                  {performance_metrics.skill_intensity.score.toFixed(1)}
                </div>
                <Badge 
                  variant="outline"
                  className="text-lg px-4 py-2"
                  style={{ 
                    backgroundColor: getLevelColor(performance_metrics.skill_intensity.level),
                    color: 'white'
                  }}
                >
                  {performance_metrics.skill_intensity.level}
                </Badge>
                <Progress value={performance_metrics.skill_intensity.score} className="h-3" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                学习曲线
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="font-medium">当前阶段</span>
                  <Badge variant="outline">
                    {performance_metrics.learning_curve.current_stage}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">估计水平</span>
                  <Badge 
                    variant="outline"
                    style={{ 
                      backgroundColor: getLevelColor(performance_metrics.learning_curve.estimated_level),
                      color: 'white'
                    }}
                  >
                    {performance_metrics.learning_curve.estimated_level}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>阶段进度</span>
                    <span>{performance_metrics.learning_curve.stage_progress.toFixed(1)}%</span>
                  </div>
                  <Progress value={performance_metrics.learning_curve.stage_progress} className="h-2" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 难度平衡分析 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-indigo-500" />
              难度平衡分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-2xl font-bold mb-2">
                  {performance_metrics.difficulty_distribution.balance_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">平衡分数</div>
              </div>
              <Progress value={performance_metrics.difficulty_distribution.balance_score} className="h-3" />
              <div className="text-sm text-gray-600 text-center">
                理想分布: 简单 30%, 中等 50%, 困难 20%
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  // 渲染学习建议
  const renderLearningRecommendations = () => {
    if (!analysisResult) return null;

    const { learning_recommendations } = analysisResult;

    return (
      <div className="space-y-4">
        {learning_recommendations.map((recommendation, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-blue-500" />
                  {recommendation.title}
                </div>
                <Badge 
                  variant="outline"
                  style={{ 
                    backgroundColor: getPriorityColor(recommendation.priority),
                    color: 'white'
                  }}
                >
                  {recommendation.priority === 'high' ? '高优先级' : 
                   recommendation.priority === 'medium' ? '中优先级' : '低优先级'}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-gray-700">{recommendation.description}</p>
                
                {recommendation.suggested_topics && (
                  <div>
                    <span className="font-medium text-sm">建议主题:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {recommendation.suggested_topics.map((topic, topicIndex) => (
                        <Badge key={topicIndex} variant="secondary" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between text-sm">
                  {recommendation.target_count && (
                    <span className="text-gray-600">
                      目标: {recommendation.target_count} 题
                    </span>
                  )}
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    <span className="text-gray-600">{recommendation.estimated_time}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  // 渲染竞赛分析
  const renderCompetitiveAnalysis = () => {
    if (!analysisResult) return null;

    const { competitive_ranking } = analysisResult;

    // 检查是否有竞赛数据
    if (!competitive_ranking.contests_attended || competitive_ranking.contests_attended === 0) {
      return (
        <Card>
          <CardContent className="text-center py-8">
            <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">暂无竞赛数据</p>
          </CardContent>
        </Card>
      );
    }

    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              竞赛表现
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {competitive_ranking.current_rating}
                </div>
                <div className="text-sm text-gray-600">当前评分</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {competitive_ranking.global_ranking?.toLocaleString() || 'N/A'}
                </div>
                <div className="text-sm text-gray-600">全球排名</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {competitive_ranking.contests_attended}
                </div>
                <div className="text-sm text-gray-600">参赛次数</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {competitive_ranking.top_percentage?.toFixed(1) || 'N/A'}%
                </div>
                <div className="text-sm text-gray-600">前百分比</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-500" />
                评分趋势
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <Badge 
                  variant="outline"
                  className="text-lg px-4 py-2"
                  style={{ 
                    backgroundColor: competitive_ranking.rating_trend === '稳定上升' ? colors.success :
                                   competitive_ranking.rating_trend === '缓慢上升' ? colors.warning :
                                   competitive_ranking.rating_trend === '波动中' ? colors.info : colors.danger,
                    color: 'white'
                  }}
                >
                  {competitive_ranking.rating_trend}
                </Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5 text-purple-500" />
                表现等级
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <Badge 
                  variant="outline"
                  className="text-lg px-4 py-2"
                  style={{ 
                    backgroundColor: getLevelColor(competitive_ranking.performance_level),
                    color: 'white'
                  }}
                >
                  {competitive_ranking.performance_level}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  // 渲染解题模式
  const renderProblemSolvingPatterns = () => {
    if (!analysisResult) return null;

    const { problem_solving_patterns } = analysisResult;

    return (
      <div className="space-y-6">
        {/* 解题策略 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-500" />
              解题策略
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <Badge variant="outline" className="text-lg px-4 py-2">
                  {problem_solving_patterns.solving_strategy.type}
                </Badge>
              </div>
              <div>
                <h4 className="font-medium mb-2">策略特征:</h4>
                <div className="space-y-1">
                  {problem_solving_patterns.solving_strategy.characteristics.map((char, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="text-sm">{char}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 错误模式 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              错误模式分析
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(problem_solving_patterns.error_patterns).map(([difficulty, data]) => (
                <div key={difficulty} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium capitalize">{difficulty}</span>
                    <Badge 
                      variant="outline"
                      style={{ 
                        backgroundColor: data.error_rate <= 20 ? colors.success :
                                       data.error_rate <= 40 ? colors.warning :
                                       data.error_rate <= 60 ? colors.info : colors.danger,
                        color: 'white'
                      }}
                    >
                      {data.level}
                    </Badge>
                  </div>
                  <Progress value={100 - data.error_rate} className="h-2" />
                  <div className="text-sm text-gray-600">
                    错误率: {data.error_rate.toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 学习路径 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-500" />
              学习路径
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">当前阶段:</span>
                  <div className="mt-1">
                    <Badge variant="outline">
                      {problem_solving_patterns.learning_path.current_phase}
                    </Badge>
                  </div>
                </div>
                <div>
                  <span className="font-medium">下一里程碑:</span>
                  <div className="mt-1">
                    <Badge variant="outline">
                      {problem_solving_patterns.learning_path.next_milestone.target}
                    </Badge>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>里程碑进度</span>
                  <span>{problem_solving_patterns.learning_path.next_milestone.progress.toFixed(1)}%</span>
                </div>
                <Progress value={problem_solving_patterns.learning_path.next_milestone.progress} className="h-2" />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>剩余: {problem_solving_patterns.learning_path.next_milestone.remaining} 题</span>
                  <span>预计: {problem_solving_patterns.learning_path.next_milestone.estimated_time}</span>
                </div>
              </div>

              <div>
                <span className="font-medium">推荐关注:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {problem_solving_patterns.learning_path.recommended_focus.map((focus, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {focus}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* 搜索区域 */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-blue-500" />
            LeetCode 分析
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <Input
                placeholder="输入 LeetCode 用户名或个人主页 URL"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && analyzeLeetCode()}
              />
            </div>
            <Button 
              onClick={analyzeLeetCode}
              disabled={isLoading}
              className="flex items-center gap-2"
            >
              {isLoading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              {isLoading ? '分析中...' : '开始分析'}
            </Button>
          </div>

          {/* 搜索历史 */}
          {searchHistory.length > 0 && (
            <div className="flex flex-wrap gap-2">
              <span className="text-sm text-gray-600">最近搜索:</span>
              {searchHistory.map((item, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="cursor-pointer hover:bg-gray-100"
                  onClick={() => setUsername(item)}
                >
                  {item}
                </Badge>
              ))}
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <Alert className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* 分析结果 */}
      {analysisResult && (
        <div className="space-y-6">
          {/* 用户档案 */}
          {renderUserProfile()}

          {/* 标签页 */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="overview">概览</TabsTrigger>
              <TabsTrigger value="skills">技能分析</TabsTrigger>
              <TabsTrigger value="performance">性能指标</TabsTrigger>
              <TabsTrigger value="recommendations">学习建议</TabsTrigger>
              <TabsTrigger value="competitive">竞赛分析</TabsTrigger>
              <TabsTrigger value="patterns">解题模式</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* 快速统计 */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">解题统计</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {analysisResult.performance_metrics.basic_stats.total_problems_solved}
                    </div>
                    <div className="text-sm text-gray-600">题目总数</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">整体水平</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {analysisResult.skill_analysis.overall_assessment.overall_score.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600">
                      {analysisResult.skill_analysis.overall_assessment.level}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">学习阶段</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-lg font-bold text-green-600 mb-2">
                      {analysisResult.performance_metrics.learning_curve.current_stage}
                    </div>
                    <div className="text-sm text-gray-600">
                      进度: {analysisResult.performance_metrics.learning_curve.stage_progress.toFixed(1)}%
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* 快速建议 */}
              <Card>
                <CardHeader>
                  <CardTitle>快速建议</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {analysisResult.skill_analysis.overall_assessment.next_steps.slice(0, 3).map((step, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Target className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">{step}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="skills">
              {renderSkillAnalysis()}
            </TabsContent>

            <TabsContent value="performance">
              {renderPerformanceMetrics()}
            </TabsContent>

            <TabsContent value="recommendations">
              {renderLearningRecommendations()}
            </TabsContent>

            <TabsContent value="competitive">
              {renderCompetitiveAnalysis()}
            </TabsContent>

            <TabsContent value="patterns">
              {renderProblemSolvingPatterns()}
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
};

export default LeetCodeAnalysis;
