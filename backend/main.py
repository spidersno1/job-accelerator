"""
程序员求职加速器Agent - 后端API主入口文件

这是整个后端系统的主入口文件，负责：
1. 配置FastAPI应用实例
2. 设置CORS中间件以支持跨域请求
3. 注册所有API路由模块
4. 配置数据库生命周期管理
5. 提供健康检查和基础信息接口

技术栈：
- FastAPI: 现代、高性能的Web框架
- SQLAlchemy: ORM数据库操作
- JWT: 用户认证和授权
- CORS: 跨域资源共享支持

作者: 程序员求职加速器团队
创建时间: 2024年
最后更新: 2025年1月
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os

from app.database import engine, Base
from app.routers import users, skills, learning, jobs, agent
from app.core.config import settings

# 加载环境变量配置文件
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    
    负责管理FastAPI应用的启动和关闭过程：
    - 启动时：创建数据库表结构
    - 关闭时：清理资源（如数据库连接、缓存等）
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时创建数据库表
    print("🚀 正在初始化数据库...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时清理资源
    print("🔄 正在清理应用资源...")
    # 这里可以添加清理逻辑，如关闭数据库连接池、清理缓存等
    print("✅ 资源清理完成")

# 创建FastAPI应用实例
app = FastAPI(
    title="程序员求职加速器Agent API",
    description="""
    AI驱动的程序员求职助手后端API系统
    
    主要功能模块：
    - 用户认证与管理
    - 技能分析与评估
    - 学习路径生成
    - 岗位智能匹配
    - AI助手对话
    
    支持多种技能分析方式：
    - GitHub代码仓库分析
    - LeetCode算法题解析
    - 代码文件上传分析
    - 文本内容分析
    - 图片OCR识别分析
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url="/redoc"  # ReDoc文档地址
)

# 配置跨域资源共享(CORS)中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问（生产环境应限制具体域名）
    allow_credentials=True,  # 允许携带认证信息
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"]  # 暴露所有响应头
)

# 注册API路由模块
# 每个模块负责特定的业务功能
app.include_router(users.router, prefix="/api/users", tags=["用户管理"])
app.include_router(skills.router, prefix="/api/skills", tags=["技能分析"])
app.include_router(learning.router, prefix="/api/learning", tags=["学习路径"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["岗位匹配"])
app.include_router(agent.router, prefix="/api/agent", tags=["AI助手"])

@app.get("/", summary="根路径", description="返回API基本信息")
async def root():
    """
    API根路径接口
    
    返回系统基本信息，用于验证API服务是否正常运行
    
    Returns:
        dict: 包含系统名称和版本信息的字典
    """
    return {
        "message": "程序员求职加速器Agent API", 
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", summary="健康检查", description="检查服务健康状态")
async def health_check():
    """
    健康检查接口
    
    用于监控系统运行状态，通常被负载均衡器或监控系统调用
    
    Returns:
        dict: 包含服务状态信息的字典
    """
    return {
        "status": "healthy", 
        "service": "job-accelerator-agent",
        "timestamp": "2025-01-01T00:00:00Z"
    }

# 应用启动入口
if __name__ == "__main__":
    """
    开发环境启动配置
    
    生产环境建议使用 gunicorn 或 uvicorn 作为WSGI服务器
    """
    print("🚀 启动程序员求职加速器Agent API服务...")
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,       # 监听端口
        reload=True      # 开发模式，代码变更时自动重载
    )
