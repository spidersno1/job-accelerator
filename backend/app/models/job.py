from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(100))
    salary_range = Column(String(100))
    job_description = Column(Text)
    requirements = Column(Text)  # JSON格式存储技能要求
    job_type = Column(String(50))  # 全职、兼职、实习
    experience_level = Column(String(50))  # 初级、中级、高级
    source_url = Column(String(500))
    posted_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    matches = relationship("JobMatch", back_populates="job")

class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float)  # 匹配度分数 0-100
    skill_match = Column(Text)  # JSON格式存储技能匹配详情
    gap_analysis = Column(Text)  # JSON格式存储技能差距分析
    is_applied = Column(Boolean, default=False)
    applied_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="job_matches")
    job = relationship("Job", back_populates="matches")
