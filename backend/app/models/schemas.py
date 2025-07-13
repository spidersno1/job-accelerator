from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import re  # 添加re模块导入

# 用户相关模型
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = 0

class GitHubConnectRequest(BaseModel):
    username: str
    token: Optional[str] = None

class GitHubAnalysisRequest(BaseModel):
    token: str

class LeetCodeAnalysisRequest(BaseModel):
    username_or_url: str
    validate_url: bool = True  # 新增字段控制是否验证URL格式

    @validator('username_or_url')
    def validate_leetcode_input(cls, v):
        if not v:
            raise ValueError('LeetCode用户名或URL不能为空')
        
        # 如果是URL格式则验证
        if v.startswith(('http://', 'https://')):
            patterns = [
                r'leetcode\.(?:com|cn)/(?:u|profile)/([^\/]+)',  # /u/ or /profile/
                r'leetcode\.(?:com|cn)/([^\/]+)(?:/)?$'          # /username
            ]
            
            for pattern in patterns:
                if re.search(pattern, v):
                    return v
            
            raise ValueError('无效的LeetCode URL格式')
        
        # 用户名验证 - 只允许字母数字和下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        
        return v

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    github_username: Optional[str] = None
    github_token: Optional[str] = None
    leetcode_username: Optional[str] = None
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[int] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    github_skills: Optional[str] = None
    
    class Config:
        from_attributes = True

# 认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 技能相关模型
class SkillBase(BaseModel):
    skill_name: str
    proficiency: int  # 0-100
    category: Optional[str] = None
    evidence: Optional[Dict[str, Any]] = None

# 其他现有模型保持不变...

class SkillReport(BaseModel):
    id: int
    user_id: int
    report_data: str  # JSON格式
    generated_at: datetime

    class Config:
        from_attributes = True

class LearningTask(BaseModel):
    id: int
    learning_path_id: int
    task_name: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[int] = None
    resources: Optional[str] = None  # JSON格式
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    order_index: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LearningPath(BaseModel):
    id: int
    user_id: int
    target_role: str
    path_name: str
    description: Optional[str] = None
    estimated_duration: Optional[int] = None
    current_progress: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tasks: Optional[List[LearningTask]] = None

    class Config:
        from_attributes = True

class LearningPathCreate(BaseModel):
    target_role: str
    path_name: str
    description: Optional[str] = None
    estimated_duration: Optional[int] = None

class LearningPathUpdate(BaseModel):
    path_name: Optional[str] = None
    description: Optional[str] = None
    estimated_duration: Optional[int] = None
    current_progress: Optional[int] = None
    is_active: Optional[bool] = None

class LearningTaskCreate(BaseModel):
    task_name: str
    description: Optional[str] = None
    task_type: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[int] = None
    resources: Optional[str] = None
    order_index: Optional[int] = None

class LearningTaskUpdate(BaseModel):
    task_name: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_hours: Optional[int] = None
    resources: Optional[str] = None
    is_completed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    order_index: Optional[int] = None

class Job(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None  # JSON格式
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobMatch(BaseModel):
    id: int
    user_id: int
    job_id: int
    match_score: Optional[float] = None
    skill_match: Optional[str] = None  # JSON格式
    gap_analysis: Optional[str] = None  # JSON格式
    is_applied: Optional[bool] = None
    applied_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_description: Optional[str] = None
    requirements: Optional[str] = None  # JSON格式
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    source_url: Optional[str] = None
    posted_date: Optional[datetime] = None

class JobMatchCreate(BaseModel):
    user_id: int
    job_id: int
    match_score: Optional[float] = None
    skill_match: Optional[str] = None  # JSON格式
    gap_analysis: Optional[str] = None  # JSON格式
    is_applied: Optional[bool] = None
    applied_date: Optional[datetime] = None

class JobMatchUpdate(BaseModel):
    match_score: Optional[float] = None
    skill_match: Optional[str] = None  # JSON格式
    gap_analysis: Optional[str] = None  # JSON格式
    is_applied: Optional[bool] = None
    applied_date: Optional[datetime] = None

class AgentRequest(BaseModel):
    request_type: str
    parameters: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
