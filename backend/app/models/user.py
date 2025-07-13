from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from typing import Dict, Any
import json
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    leetcode_username = Column(String(50), comment="LeetCode用户名")
    leetcode_url = Column(String(100), comment="完整的LeetCode个人主页URL")
    current_role = Column(String(100))
    target_role = Column(String(100))
    experience_years = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 认证相关字段
    require_reauth = Column(Boolean, default=False)
    last_login_ip = Column(String(45))
    last_login_at = Column(DateTime(timezone=True))
    login_history = Column(Text)
    
    # 二次认证相关字段
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_method = Column(String(10))  # email/sms
    two_factor_secret = Column(String(100))
    two_factor_expires = Column(DateTime(timezone=True))
    
    # 邮箱验证相关字段
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255))
    email_verification_expires = Column(DateTime(timezone=True))
    
    # 密码重置相关字段
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True))
    
    # 账户安全相关字段
    account_locked = Column(Boolean, default=False)
    account_locked_until = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime(timezone=True))
    
    # 会话管理相关字段
    active_sessions = Column(Text)  # JSON格式存储活跃会话
    max_concurrent_sessions = Column(Integer, default=5)
    
    # 安全审计相关字段
    security_questions = Column(Text)  # JSON格式存储安全问题
    backup_email = Column(String(100))
    phone_number = Column(String(20))
    phone_verified = Column(Boolean, default=False)
    
    # 关系
    skills = relationship("Skill", back_populates="user")
    skill_reports = relationship("SkillReport", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")
    job_matches = relationship("JobMatch", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    
    def is_account_locked(self) -> bool:
        """检查账户是否被锁定"""
        if not self.account_locked:
            return False
        
        if self.account_locked_until and datetime.utcnow() > self.account_locked_until:
            # 锁定期已过，自动解锁
            self.account_locked = False
            self.account_locked_until = None
            self.failed_login_attempts = 0
            return False
        
        return True
    
    def lock_account(self, duration_minutes: int = 30):
        """锁定账户"""
        self.account_locked = True
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self):
        """解锁账户"""
        self.account_locked = False
        self.account_locked_until = None
        self.failed_login_attempts = 0
    
    def increment_failed_login(self):
        """增加失败登录计数"""
        self.failed_login_attempts += 1
        self.last_failed_login = datetime.utcnow()
        
        # 超过5次失败尝试，锁定账户30分钟
        if self.failed_login_attempts >= 5:
            self.lock_account(30)
    
    def reset_failed_login(self):
        """重置失败登录计数"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
    
    def get_active_sessions(self) -> list:
        """获取活跃会话列表"""
        if not self.active_sessions:
            return []
        try:
            return json.loads(self.active_sessions)
        except:
            return []
    
    def add_active_session(self, session_id: str, client_ip: str, device_info: dict):
        """添加活跃会话"""
        sessions = self.get_active_sessions()
        
        # 移除过期或超出限制的会话
        current_time = datetime.utcnow()
        sessions = [s for s in sessions if datetime.fromisoformat(s.get('last_activity', '')) > current_time - timedelta(hours=24)]
        
        # 如果达到最大并发会话数，移除最旧的会话
        if len(sessions) >= self.max_concurrent_sessions:
            sessions = sorted(sessions, key=lambda x: x.get('last_activity', ''), reverse=True)
            sessions = sessions[:self.max_concurrent_sessions-1]
        
        # 添加新会话
        sessions.append({
            'session_id': session_id,
            'client_ip': client_ip,
            'device_info': device_info,
            'created_at': current_time.isoformat(),
            'last_activity': current_time.isoformat()
        })
        
        self.active_sessions = json.dumps(sessions)
    
    def remove_active_session(self, session_id: str):
        """移除活跃会话"""
        sessions = self.get_active_sessions()
        sessions = [s for s in sessions if s.get('session_id') != session_id]
        self.active_sessions = json.dumps(sessions)
    
    def get_security_questions(self) -> list:
        """获取安全问题列表"""
        if not self.security_questions:
            return []
        try:
            return json.loads(self.security_questions)
        except:
            return []
    
    def set_security_questions(self, questions: list):
        """设置安全问题"""
        self.security_questions = json.dumps(questions)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'current_role': self.current_role,
            'target_role': self.target_role,
            'experience_years': self.experience_years,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'two_factor_enabled': self.two_factor_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'account_locked': self.account_locked
        }

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="sessions")
