from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_name = Column(String(100), nullable=False)
    skill_category = Column(String(50))  # 编程语言、框架、工具等
    proficiency_level = Column(Float, default=0.0)  # 0-100
    source = Column(String(50))  # github, leetcode, manual
    evidence = Column(Text)  # JSON格式存储证据
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="skills")

class SkillReport(Base):
    __tablename__ = "skill_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    report_data = Column(Text)  # JSON格式存储完整报告
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="skill_reports")
