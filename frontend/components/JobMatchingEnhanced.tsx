import { useState, useEffect } from 'react';
import { MapPin, Building, DollarSign, Clock, ExternalLink, RefreshCw, Search, Target } from 'lucide-react';

type JobMatch = {
  job_id: number;
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  experience_level?: string;
  job_type?: string;
  match_percentage: number;
  skills_matched?: string[];
  skills_missing?: string[];
  source_url?: string;
  source_site?: string;
  posted_date?: string;
};

type CrawlResult = {
  status: string;
  message: string;
  total_crawled: number;
  newly_saved: number;
  user_skills: string[];
  locations: string[];
  match_results: JobMatch[];
  crawl_time: string;
};

const JobMatchingEnhanced = () => {
  const [jobMatches, setJobMatches] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobMatch | null>(null);
  const [crawlResult, setCrawlResult] = useState<CrawlResult | null>(null);
  const [activeTab, setActiveTab] = useState<'matches' | 'crawler'>('matches');

  useEffect(() => {
    fetchJobMatches();
  }, []);

  const fetchJobMatches = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/jobs/match-simple', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setJobMatches(data);
    } catch (error) {
      console.error('获取职位匹配失败:', error);
      setError('获取职位匹配失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const crawlJobsBySkills = async () => {
    setCrawling(true);
    setError(null);
    setCrawlResult(null);

    try {
      const response = await fetch('/api/jobs/crawl-by-skills', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          locations: ['北京', '上海', '广州', '深圳'],
          max_jobs_per_site: 20
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setCrawlResult(result);
      
      if (result.status === 'success' && result.match_results?.length > 0) {
        // 合并新的匹配结果
        setJobMatches(prev => [...result.match_results, ...prev]);
      }
    } catch (error) {
      console.error('爬取职位失败:', error);
      setError('爬取职位失败，请稍后重试');
    } finally {
      setCrawling(false);
    }
  };

  const getMatchColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600 bg-green-100';
    if (percentage >= 60) return 'text-blue-600 bg-blue-100';
    if (percentage >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return '未知';
    try {
      return new Date(dateString).toLocaleDateString('zh-CN');
    } catch {
      return dateString;
    }
  };

  return (
    <div className="job-matching-enhanced">
      {/* 标签页导航 */}
      <div className="tabs mb-6">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('matches')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'matches' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🎯 职位匹配
          </button>
          <button
            onClick={() => setActiveTab('crawler')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'crawler' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            🔍 智能爬取
          </button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="error-message mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* 职位匹配标签页 */}
      {activeTab === 'matches' && (
        <div className="matches-tab">
          {/* 操作按钮 */}
          <div className="actions mb-6 flex space-x-4">
            <button
              onClick={fetchJobMatches}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>{loading ? '刷新中...' : '刷新匹配'}</span>
            </button>
          </div>

          {/* 职位匹配列表 */}
          {loading ? (
            <div className="loading text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-gray-600">正在加载职位匹配...</p>
            </div>
          ) : jobMatches.length === 0 ? (
            <div className="empty-state text-center py-8">
              <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">暂无职位匹配数据</p>
              <p className="text-sm text-gray-500 mt-2">请先完善您的技能信息</p>
            </div>
          ) : (
            <div className="job-matches-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobMatches.map((match, index) => (
                <div
                  key={index}
                  className="job-match-card bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedJob(match)}
                >
                  {/* 匹配度标识 */}
                  <div className="match-score mb-4">
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getMatchColor(match.match_percentage)}`}>
                      {match.match_percentage}% 匹配
                    </span>
                  </div>

                  {/* 职位信息 */}
                  <div className="job-info">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{match.title}</h3>
                    
                    <div className="job-details space-y-2 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Building className="h-4 w-4" />
                        <span>{match.company}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <MapPin className="h-4 w-4" />
                        <span>{match.location}</span>
                      </div>
                      
                      {match.salary_range && (
                        <div className="flex items-center space-x-2">
                          <DollarSign className="h-4 w-4" />
                          <span>{match.salary_range}</span>
                        </div>
                      )}
                      
                      {match.experience_level && (
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4" />
                          <span>{match.experience_level}</span>
                        </div>
                      )}
                    </div>

                    {/* 技能匹配 */}
                    <div className="skills-match mt-4">
                      {match.skills_matched && match.skills_matched.length > 0 && (
                        <div className="matched-skills mb-2">
                          <p className="text-xs text-green-600 font-medium mb-1">匹配技能:</p>
                          <div className="flex flex-wrap gap-1">
                            {match.skills_matched.slice(0, 3).map((skill, idx) => (
                              <span key={idx} className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
                                {skill}
                              </span>
                            ))}
                            {match.skills_matched.length > 3 && (
                              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                +{match.skills_matched.length - 3}
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* 来源信息 */}
                    {match.source_site && (
                      <div className="source-info mt-3 pt-3 border-t border-gray-200">
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>来源: {match.source_site}</span>
                          {match.posted_date && (
                            <span>{formatDate(match.posted_date)}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 智能爬取标签页 */}
      {activeTab === 'crawler' && (
        <div className="crawler-tab">
          <div className="crawler-section bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4">🔍 智能职位爬取</h3>
            <p className="text-gray-600 mb-6">
              基于您的技能自动从主流招聘网站爬取相关职位，并进行智能匹配分析。
            </p>

            {/* 爬取按钮 */}
            <div className="crawler-actions mb-6">
              <button
                onClick={crawlJobsBySkills}
                disabled={crawling}
                className="flex items-center space-x-2 px-6 py-3 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400"
              >
                <Search className={`h-5 w-5 ${crawling ? 'animate-spin' : ''}`} />
                <span>{crawling ? '正在爬取...' : '开始智能爬取'}</span>
              </button>
            </div>

            {/* 爬取结果 */}
            {crawlResult && (
              <div className="crawl-result p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-3">爬取结果</h4>
                
                <div className="result-stats grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="stat-item">
                    <p className="text-sm text-gray-600">总爬取数</p>
                    <p className="text-2xl font-bold text-blue-600">{crawlResult.total_crawled}</p>
                  </div>
                  <div className="stat-item">
                    <p className="text-sm text-gray-600">新增职位</p>
                    <p className="text-2xl font-bold text-green-600">{crawlResult.newly_saved}</p>
                  </div>
                  <div className="stat-item">
                    <p className="text-sm text-gray-600">匹配职位</p>
                    <p className="text-2xl font-bold text-purple-600">{crawlResult.match_results?.length || 0}</p>
                  </div>
                  <div className="stat-item">
                    <p className="text-sm text-gray-600">搜索技能</p>
                    <p className="text-2xl font-bold text-orange-600">{crawlResult.user_skills?.length || 0}</p>
                  </div>
                </div>

                {/* 搜索技能 */}
                {crawlResult.user_skills && crawlResult.user_skills.length > 0 && (
                  <div className="search-skills mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">搜索技能:</p>
                    <div className="flex flex-wrap gap-2">
                      {crawlResult.user_skills.map((skill, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* 爬取时间 */}
                <div className="crawl-time text-sm text-gray-500">
                  爬取时间: {new Date(crawlResult.crawl_time).toLocaleString('zh-CN')}
                </div>
              </div>
            )}

            {/* 爬取说明 */}
            <div className="crawler-info mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">📋 爬取说明</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 基于您的高熟练度技能(≥60%)进行搜索</li>
                <li>• 从拉勾网、智联招聘、BOSS直聘等主流网站爬取</li>
                <li>• 自动去重，避免重复职位</li>
                <li>• 实时进行匹配度分析</li>
                <li>• 遵守网站robots.txt协议，合法合规</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 职位详情模态框 */}
      {selectedJob && (
        <div className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="modal-content bg-white p-6 rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="modal-header flex justify-between items-start mb-4">
              <h2 className="text-xl font-semibold">{selectedJob.title}</h2>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="modal-body space-y-4">
              {/* 匹配度 */}
              <div className="match-score">
                <span className={`inline-block px-4 py-2 rounded-full text-lg font-medium ${getMatchColor(selectedJob.match_percentage)}`}>
                  {selectedJob.match_percentage}% 匹配度
                </span>
              </div>

              {/* 基本信息 */}
              <div className="job-basic-info grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">公司</p>
                  <p className="font-medium">{selectedJob.company}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">地点</p>
                  <p className="font-medium">{selectedJob.location}</p>
                </div>
                {selectedJob.salary_range && (
                  <div>
                    <p className="text-sm text-gray-600">薪资</p>
                    <p className="font-medium">{selectedJob.salary_range}</p>
                  </div>
                )}
                {selectedJob.experience_level && (
                  <div>
                    <p className="text-sm text-gray-600">经验要求</p>
                    <p className="font-medium">{selectedJob.experience_level}</p>
                  </div>
                )}
              </div>

              {/* 技能匹配详情 */}
              <div className="skills-details">
                {selectedJob.skills_matched && selectedJob.skills_matched.length > 0 && (
                  <div className="matched-skills mb-4">
                    <h4 className="font-medium text-green-700 mb-2">✅ 匹配技能</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedJob.skills_matched.map((skill, index) => (
                        <span key={index} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {selectedJob.skills_missing && selectedJob.skills_missing.length > 0 && (
                  <div className="missing-skills">
                    <h4 className="font-medium text-red-700 mb-2">❌ 缺少技能</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedJob.skills_missing.map((skill, index) => (
                        <span key={index} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 操作按钮 */}
              <div className="modal-actions flex space-x-4">
                {selectedJob.source_url && (
                  <a
                    href={selectedJob.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                  >
                    <ExternalLink className="h-4 w-4" />
                    <span>查看原职位</span>
                  </a>
                )}
                <button
                  onClick={() => setSelectedJob(null)}
                  className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobMatchingEnhanced; 