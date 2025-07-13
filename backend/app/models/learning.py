from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_role = Column(String(100), nullable=False)
    path_name = Column(String(200), nullable=False)
    description = Column(Text)
    estimated_duration = Column(Integer)  # 预计天数
    current_progress = Column(Integer, default=0)  # 当前进度百分比
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="learning_paths")
    tasks = relationship("LearningTask", back_populates="learning_path")

class LearningTask(Base):
    __tablename__ = "learning_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    task_name = Column(String(200), nullable=False)
    description = Column(Text)
    task_type = Column(String(50))  # 学习、练习、项目等
    difficulty = Column(String(20))  # 简单、中等、困难
    estimated_hours = Column(Integer)
    resources = Column(Text)  # JSON格式存储资源链接
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    order_index = Column(Integer)  # 任务顺序
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    learning_path = relationship("LearningPath", back_populates="tasks")
