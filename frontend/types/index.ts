// 用户相关类型
export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  github_username?: string
  leetcode_username?: string
  current_role?: string
  target_role?: string
  experience_years?: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
  github_username?: string
  leetcode_username?: string
  current_role?: string
  target_role?: string
  experience_years?: number
}

export interface UserUpdate {
  full_name?: string
  github_username?: string
  leetcode_username?: string
  current_role?: string
  target_role?: string
  experience_years?: number
}

// 认证相关类型
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

// 技能相关类型
export interface Skill {
  id: number
  user_id: number
  skill_name: string
  skill_category: string
  proficiency_level: number
  source: string
  evidence: string
  created_at: string
}

export interface SkillReport {
  id: number
  user_id: number
  report_data: string
  generated_at: string
}

export interface LearningTaskDetail {
  task_name: string
  description: string
  task_type: string
  difficulty: '简单' | '中等' | '困难'
  estimated_hours: number
  resources: string
  status?: 'not_started' | 'in_progress' | 'completed'
  progress?: number
}

export interface LearningPathDetail {
  path_name: string
  description: string
  estimated_duration: number
  overall_progress: number
  tasks: LearningTaskDetail[]
  ai_suggestions?: string[]
}

export interface SkillsMatchProps {
  skills: Skill[]
  learningPath?: LearningPathDetail
}

export interface SkillsRadarProps {
  report: SkillReport | null
}

// 学习路径相关类型
export interface LearningPath {
  id: number
  user_id: number
  target_role: string
  path_name: string
  description?: string
  estimated_duration?: number
  current_progress: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface LearningTask {
  id: number
  learning_path_id: number
  task_name: string
  description?: string
  task_type?: string
  difficulty?: string
  estimated_hours?: number
  resources?: string
  is_completed: boolean
  completed_at?: string
  order_index?: number
  created_at: string
}

// 岗位相关类型
export interface Job {
  id: number
  title: string
  company: string
  location?: string
  salary_range?: string
  job_description?: string
  requirements?: string
  job_type?: string
  experience_level?: string
  source_url?: string
  posted_date?: string
  is_active: boolean
  created_at: string
}

export interface JobMatch {
  id: number
  user_id: number
  job_id: number
  match_score: number
  skill_match?: string
  gap_analysis?: string
  is_applied: boolean
  applied_date?: string
  created_at: string
}

// AI Agent相关类型
export interface AgentRequest {
  user_id: number
  request_type: string
  parameters?: Record<string, any>
}

export interface AgentResponse {
  success: boolean
  data?: Record<string, any>
  message?: string
}

// API响应类型
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}
