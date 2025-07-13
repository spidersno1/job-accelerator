'use client';

import React, { useState, useEffect } from 'react';
import { getMatchedJobs, getJobDetails } from '../lib/api';

interface JobMatch {
  job_id: number;
  title: string;
  company: string;
  match_percentage: number;
  required_skills: any[];
}

interface JobDetails {
  id: number;
  title: string;
  company: string;
  location: string;
  salary_range: string;
  job_description: string;
  requirements: string;
  job_type: string;
  experience_level: string;
}

const JobMatching: React.FC = () => {
  const [matchedJobs, setMatchedJobs] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedJob, setSelectedJob] = useState<JobDetails | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchMatchedJobs();
  }, []);

  const fetchMatchedJobs = async () => {
    try {
      setLoading(true);
      const jobs = await getMatchedJobs(10);
      setMatchedJobs(jobs);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取匹配职位失败');
    } finally {
      setLoading(false);
    }
  };

  const handleJobClick = async (jobId: number) => {
    try {
      const jobDetails = await getJobDetails(jobId);
      setSelectedJob(jobDetails);
      setShowDetails(true);
    } catch (err) {
      console.error('获取职位详情失败:', err);
    }
  };

  const closeDetails = () => {
    setShowDetails(false);
    setSelectedJob(null);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
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
            <h3 className="text-sm font-medium text-red-800">获取匹配职位失败</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <div className="mt-4">
              <button
                onClick={fetchMatchedJobs}
                className="bg-red-100 text-red-800 px-3 py-2 rounded-md text-sm font-medium hover:bg-red-200"
              >
                重试
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">推荐职位</h2>
          <p className="text-sm text-gray-600 mt-1">基于您的技能匹配的职位</p>
        </div>
        
        <div className="divide-y divide-gray-200">
          {matchedJobs.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">暂无匹配职位</h3>
              <p className="mt-1 text-sm text-gray-500">请先添加您的技能信息</p>
            </div>
          ) : (
            matchedJobs.map((job) => (
              <div key={job.job_id} className="px-6 py-4 hover:bg-gray-50 cursor-pointer" onClick={() => handleJobClick(job.job_id)}>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-gray-900">{job.title}</h3>
                    <p className="text-sm text-gray-500">{job.company}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{job.match_percentage}%</div>
                      <div className="text-xs text-gray-500">匹配度</div>
                    </div>
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${job.match_percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 职位详情模态框 */}
      {showDetails && selectedJob && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">{selectedJob.title}</h3>
                <button
                  onClick={closeDetails}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">公司信息</h4>
                  <p className="text-sm text-gray-600">{selectedJob.company}</p>
                  <p className="text-sm text-gray-600">{selectedJob.location}</p>
                  <p className="text-sm text-gray-600">{selectedJob.salary_range}</p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-900">职位类型</h4>
                  <p className="text-sm text-gray-600">{selectedJob.job_type} • {selectedJob.experience_level}</p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-900">职位描述</h4>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{selectedJob.job_description}</p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-gray-900">技能要求</h4>
                  <p className="text-sm text-gray-600 whitespace-pre-wrap">{selectedJob.requirements}</p>
                </div>
              </div>
              
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={closeDetails}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  关闭
                </button>
                <button
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
                >
                  申请职位
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobMatching; 