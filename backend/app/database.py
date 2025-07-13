"""
数据库配置和模型导入模块

这个模块负责：
1. 导入数据库配置（引擎、会话、依赖注入）
2. 导入所有数据模型以确保它们注册到SQLAlchemy的元数据中
3. 提供统一的数据库访问接口

数据库架构：
- 使用SQLAlchemy ORM进行数据库操作
- 支持SQLite（开发）和PostgreSQL（生产）
- 自动创建表结构和关系

模型关系：
- User: 用户基础信息和认证
- Job: 岗位信息和要求
- Skill: 用户技能和熟练度
- LearningPath/LearningTask: 学习路径和任务
- SkillReport: 技能分析报告
- JobMatch: 岗位匹配结果

作者: 程序员求职加速器团队
创建时间: 2024年
最后更新: 2025年1月
"""

# 导入数据库基础配置
from .models.base import Base
from .config.database_config import engine, SessionLocal, get_db

# 导入所有数据模型以确保它们注册到Base.metadata
# 这样SQLAlchemy才能正确创建表结构和外键关系
from .models.user import User              # 用户模型：认证、个人信息
from .models.job import Job                # 岗位模型：职位信息、要求
from .models.skill import Skill            # 技能模型：技能评估、熟练度
from .models.learning import LearningPath, LearningTask  # 学习路径和任务模型
from .models.schemas import SkillReport, JobMatch        # 分析报告和匹配结果模型

# 注意：导入顺序很重要，确保外键依赖关系正确建立
# User -> Skill (一对多)
# User -> LearningPath (一对多)
# LearningPath -> LearningTask (一对多)
# User -> SkillReport (一对多)
# User -> JobMatch (一对多)
