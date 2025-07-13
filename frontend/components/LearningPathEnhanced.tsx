import { useState, useEffect } from 'react';
import { Play, Clock, Target, CheckCircle, Circle, BookOpen, Award, TrendingUp, Plus, Trash2 } from 'lucide-react';

type LearningResource = {
  title: string;
  type: string;
  url: string;
  description: string;
  difficulty: string;
  duration: string;
  provider: string;
  rating: number;
  tags: string[];
};

type LearningTask = {
  id: number;
  title: string;
  description: string;
  skill_target: string;
  target_proficiency: number;
  estimated_hours: number;
  status: string;
  progress: number;
  is_milestone: boolean;
  prerequisites: string[];
  resources: LearningResource[];
  practice_tasks: string[];
  assessment_criteria: string[];
  created_at: string;
  completed_at?: string;
};

type LearningPath = {
  id: number;
  title: string;
  description: string;
  target_job: string;
  difficulty_level: string;
  estimated_hours: number;
  estimated_weeks: number;
  progress: number;
  created_at: string;
  tasks: LearningTask[];
};

type ProgressOverview = {
  total_paths: number;
  total_tasks: number;
  completed_tasks: number;
  in_progress_tasks: number;
  total_hours: number;
  completed_hours: number;
  overall_progress: number;
};

const LearningPathEnhanced = () => {
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [selectedPath, setSelectedPath] = useState<LearningPath | null>(null);
  const [progressOverview, setProgressOverview] = useState<ProgressOverview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'paths' | 'create'>('overview');
  const [showCreateForm, setShowCreateForm] = useState(false);

  // 创建学习路径表单状态
  const [createForm, setCreateForm] = useState({
    type: 'skills', // 'skills' | 'job'
    target_skills: {} as Record<string, number>,
    job_id: '',
    learning_style: 'balanced'
  });

  useEffect(() => {
    fetchLearningPaths();
    fetchProgressOverview();
  }, []);

  const fetchLearningPaths = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/learning-path/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setLearningPaths(data);
    } catch (error) {
      console.error('获取学习路径失败:', error);
      setError('获取学习路径失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const fetchProgressOverview = async () => {
    try {
      const response = await fetch('/api/learning-path/progress/overview', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setProgressOverview(data.overview);
    } catch (error) {
      console.error('获取进度概览失败:', error);
    }
  };

  const fetchPathDetail = async (pathId: number) => {
    try {
      const response = await fetch(`/api/learning-path/${pathId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSelectedPath(data);
    } catch (error) {
      console.error('获取路径详情失败:', error);
      setError('获取路径详情失败');
    }
  };

  const updateTaskProgress = async (taskId: number, progress: number) => {
    try {
      const response = await fetch(`/api/learning-path/tasks/${taskId}/progress`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          progress: progress,
          status: progress >= 100 ? 'completed' : 'in_progress'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 刷新数据
      if (selectedPath) {
        fetchPathDetail(selectedPath.id);
      }
      fetchProgressOverview();
    } catch (error) {
      console.error('更新任务进度失败:', error);
      setError('更新任务进度失败');
    }
  };

  const createLearningPath = async () => {
    try {
      const endpoint = createForm.type === 'job' 
        ? '/api/learning-path/generate-by-job'
        : '/api/learning-path/generate-by-skills';

      const body = createForm.type === 'job' 
        ? {
            job_id: parseInt(createForm.job_id),
            learning_style: createForm.learning_style
          }
        : {
            target_skills: createForm.target_skills,
            learning_style: createForm.learning_style
          };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.status === 'success') {
        setShowCreateForm(false);
        setCreateForm({
          type: 'skills',
          target_skills: {},
          job_id: '',
          learning_style: 'balanced'
        });
        fetchLearningPaths();
        setActiveTab('paths');
      }
    } catch (error) {
      console.error('创建学习路径失败:', error);
      setError('创建学习路径失败');
    }
  };

  const deleteLearningPath = async (pathId: number) => {
    if (!confirm('确定要删除这个学习路径吗？')) return;

    try {
      const response = await fetch(`/api/learning-path/${pathId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      fetchLearningPaths();
      if (selectedPath?.id === pathId) {
        setSelectedPath(null);
      }
    } catch (error) {
      console.error('删除学习路径失败:', error);
      setError('删除学习路径失败');
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-600 bg-green-100';
      case 'intermediate': return 'text-blue-600 bg-blue-100';
      case 'advanced': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'in_progress': return <Play className="h-5 w-5 text-blue-500" />;
      default: return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  const addTargetSkill = () => {
    const skillName = prompt('请输入技能名称:');
    const skillLevel = prompt('请输入目标水平 (0-100):');
    
    if (skillName && skillLevel && !isNaN(parseInt(skillLevel))) {
      const level = parseInt(skillLevel);
      if (level >= 0 && level <= 100) {
        setCreateForm(prev => ({
          ...prev,
          target_skills: {
            ...prev.target_skills,
            [skillName]: level
          }
        }));
      }
    }
  };

  const removeTargetSkill = (skillName: string) => {
    setCreateForm(prev => ({
      ...prev,
      target_skills: Object.fromEntries(
        Object.entries(prev.target_skills).filter(([name]) => name !== skillName)
      )
    }));
  };

  return (
    <div className="learning-path-enhanced">
      {/* 标签页导航 */}
      <div className="tabs mb-6">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'overview' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📊 学习概览
          </button>
          <button
            onClick={() => setActiveTab('paths')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'paths' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🛤️ 学习路径
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'create' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            ➕ 创建路径
          </button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="error-message mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={() => setError(null)}
            className="text-red-500 hover:text-red-700 text-sm mt-2"
          >
            关闭
          </button>
        </div>
      )}

      {/* 学习概览标签页 */}
      {activeTab === 'overview' && (
        <div className="overview-tab">
          {progressOverview && (
            <div className="overview-cards grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="stat-card bg-blue-50 p-6 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-blue-600">学习路径</p>
                    <p className="text-2xl font-bold text-blue-800">{progressOverview.total_paths}</p>
                  </div>
                  <BookOpen className="h-8 w-8 text-blue-500" />
                </div>
              </div>
              
              <div className="stat-card bg-green-50 p-6 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-green-600">已完成任务</p>
                    <p className="text-2xl font-bold text-green-800">{progressOverview.completed_tasks}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-500" />
                </div>
              </div>
              
              <div className="stat-card bg-orange-50 p-6 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-orange-600">学习时长</p>
                    <p className="text-2xl font-bold text-orange-800">{progressOverview.completed_hours}h</p>
                  </div>
                  <Clock className="h-8 w-8 text-orange-500" />
                </div>
              </div>
              
              <div className="stat-card bg-purple-50 p-6 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-purple-600">总体进度</p>
                    <p className="text-2xl font-bold text-purple-800">{progressOverview.overall_progress}%</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-purple-500" />
                </div>
              </div>
            </div>
          )}

          {/* 学习路径列表预览 */}
          <div className="paths-preview">
            <h3 className="text-xl font-semibold mb-4">我的学习路径</h3>
            {learningPaths.length === 0 ? (
              <div className="empty-state text-center py-8">
                <BookOpen className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">还没有学习路径</p>
                <button
                  onClick={() => setActiveTab('create')}
                  className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  创建第一个学习路径
                </button>
              </div>
            ) : (
              <div className="paths-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {learningPaths.slice(0, 6).map((path) => (
                  <div key={path.id} className="path-card bg-white p-6 rounded-lg shadow-md">
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-semibold text-lg">{path.title}</h4>
                      <span className={`px-2 py-1 rounded-full text-xs ${getDifficultyColor(path.difficulty_level)}`}>
                        {path.difficulty_level}
                      </span>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-3">{path.description}</p>
                    
                    <div className="progress-info mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>进度</span>
                        <span>{path.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${path.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="path-stats flex justify-between text-sm text-gray-500">
                      <span>{path.estimated_hours}小时</span>
                      <span>{path.tasks.length}个任务</span>
                    </div>
                    
                    <button
                      onClick={() => {
                        fetchPathDetail(path.id);
                        setActiveTab('paths');
                      }}
                      className="mt-4 w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                    >
                      查看详情
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 学习路径标签页 */}
      {activeTab === 'paths' && (
        <div className="paths-tab">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold">学习路径管理</h3>
            <button
              onClick={() => setActiveTab('create')}
              className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
            >
              <Plus className="h-4 w-4" />
              <span>创建新路径</span>
            </button>
          </div>

          {/* 路径列表 */}
          <div className="paths-list grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 路径卡片 */}
            <div className="paths-column">
              <h4 className="font-medium mb-4">所有路径</h4>
              <div className="space-y-4">
                {learningPaths.map((path) => (
                  <div 
                    key={path.id} 
                    className={`path-item p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedPath?.id === path.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => fetchPathDetail(path.id)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h5 className="font-medium">{path.title}</h5>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteLearningPath(path.id);
                        }}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">{path.target_job}</p>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className={`px-2 py-1 rounded-full ${getDifficultyColor(path.difficulty_level)}`}>
                        {path.difficulty_level}
                      </span>
                      <span className="text-gray-500">{path.progress}% 完成</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 路径详情 */}
            <div className="path-detail-column">
              {selectedPath ? (
                <div className="path-detail bg-white p-6 rounded-lg shadow-md">
                  <h4 className="font-semibold text-lg mb-4">{selectedPath.title}</h4>
                  
                  <div className="path-info mb-6">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">目标职位:</span>
                        <p className="font-medium">{selectedPath.target_job}</p>
                      </div>
                      <div>
                        <span className="text-gray-600">预计时长:</span>
                        <p className="font-medium">{selectedPath.estimated_hours}小时</p>
                      </div>
                      <div>
                        <span className="text-gray-600">难度:</span>
                        <span className={`px-2 py-1 rounded-full text-xs ${getDifficultyColor(selectedPath.difficulty_level)}`}>
                          {selectedPath.difficulty_level}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">进度:</span>
                        <p className="font-medium">{selectedPath.progress}%</p>
                      </div>
                    </div>
                  </div>

                  {/* 任务列表 */}
                  <div className="tasks-section">
                    <h5 className="font-medium mb-3">学习任务</h5>
                    <div className="tasks-list space-y-3 max-h-96 overflow-y-auto">
                      {selectedPath.tasks.map((task) => (
                        <div key={task.id} className="task-item p-3 border rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(task.status)}
                              <span className="font-medium">{task.title}</span>
                              {task.is_milestone && (
                                <Award className="h-4 w-4 text-yellow-500" />
                              )}
                            </div>
                            <span className="text-sm text-gray-500">{task.estimated_hours}h</span>
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                          
                          <div className="progress-section mb-2">
                            <div className="flex justify-between text-sm mb-1">
                              <span>进度</span>
                              <span>{task.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${task.progress}%` }}
                              ></div>
                            </div>
                          </div>
                          
                          <div className="task-actions flex space-x-2">
                            <button
                              onClick={() => updateTaskProgress(task.id, Math.min(task.progress + 25, 100))}
                              className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
                            >
                              +25%
                            </button>
                            <button
                              onClick={() => updateTaskProgress(task.id, 100)}
                              className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600"
                            >
                              完成
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-detail text-center py-8">
                  <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">选择一个学习路径查看详情</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 创建路径标签页 */}
      {activeTab === 'create' && (
        <div className="create-tab">
          <div className="create-form bg-white p-6 rounded-lg shadow-md max-w-2xl mx-auto">
            <h3 className="text-xl font-semibold mb-6">创建学习路径</h3>
            
            {/* 创建类型选择 */}
            <div className="form-group mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">创建方式</label>
              <div className="flex space-x-4">
                <button
                  onClick={() => setCreateForm(prev => ({ ...prev, type: 'skills' }))}
                  className={`px-4 py-2 rounded-md ${
                    createForm.type === 'skills' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  基于技能目标
                </button>
                <button
                  onClick={() => setCreateForm(prev => ({ ...prev, type: 'job' }))}
                  className={`px-4 py-2 rounded-md ${
                    createForm.type === 'job' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  基于目标职位
                </button>
              </div>
            </div>

            {/* 基于技能创建 */}
            {createForm.type === 'skills' && (
              <div className="skills-form mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">目标技能</label>
                <div className="skills-list mb-4">
                  {Object.entries(createForm.target_skills).map(([skill, level]) => (
                    <div key={skill} className="skill-item flex items-center justify-between p-2 bg-gray-50 rounded mb-2">
                      <span>{skill}: {level}%</span>
                      <button
                        onClick={() => removeTargetSkill(skill)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  onClick={addTargetSkill}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
                >
                  <Plus className="h-4 w-4" />
                  <span>添加技能</span>
                </button>
              </div>
            )}

            {/* 基于职位创建 */}
            {createForm.type === 'job' && (
              <div className="job-form mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">目标职位ID</label>
                <input
                  type="number"
                  value={createForm.job_id}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, job_id: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="请输入职位ID"
                />
              </div>
            )}

            {/* 学习风格 */}
            <div className="form-group mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">学习风格</label>
              <select
                value={createForm.learning_style}
                onChange={(e) => setCreateForm(prev => ({ ...prev, learning_style: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="fast">快速学习</option>
                <option value="balanced">平衡学习</option>
                <option value="thorough">深入学习</option>
              </select>
            </div>

            {/* 创建按钮 */}
            <div className="form-actions flex space-x-4">
              <button
                onClick={createLearningPath}
                disabled={
                  (createForm.type === 'skills' && Object.keys(createForm.target_skills).length === 0) ||
                  (createForm.type === 'job' && !createForm.job_id)
                }
                className="px-6 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                创建学习路径
              </button>
              <button
                onClick={() => setActiveTab('paths')}
                className="px-6 py-3 bg-gray-500 text-white rounded-md hover:bg-gray-600"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LearningPathEnhanced; 