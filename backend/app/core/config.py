"""
系统核心配置模块

这个模块使用Pydantic Settings管理所有应用配置，包括：
1. 数据库连接配置
2. JWT认证配置
3. 第三方API配置（GitHub、LeetCode、ModelScope等）
4. 应用运行配置

配置来源优先级：
1. 环境变量
2. .env文件
3. 默认值

使用方式：
from app.core.config import settings
print(settings.DATABASE_URL)

安全注意事项：
- 生产环境必须通过环境变量设置敏感信息
- 不要在代码中硬编码密钥和令牌
- 定期更新API密钥和访问令牌

作者: 程序员求职加速器团队
创建时间: 2024年
最后更新: 2025年1月
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    应用配置类
    
    使用Pydantic Settings自动从环境变量和.env文件加载配置
    所有配置项都有合理的默认值，可根据部署环境进行调整
    """
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./job_accelerator.db"
    """数据库连接URL，支持SQLite和PostgreSQL"""
    
    # JWT认证配置
    SECRET_KEY: str = "your-secret-key-here"
    """JWT签名密钥，生产环境必须设置为复杂的随机字符串"""
    
    ALGORITHM: str = "HS256"
    """JWT签名算法，推荐使用HS256"""
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """访问令牌过期时间（分钟）"""
    
    ENVIRONMENT: str = "development"
    """运行环境：development/staging/production"""
    
    # 前端URL配置
    FRONTEND_URL: str = "http://localhost:3000"
    """前端应用URL，用于CORS配置和回调"""
    
    # GitHub API配置
    GITHUB_TOKEN: Optional[str] = None
    """GitHub个人访问令牌，用于访问GitHub API，请在.env文件中设置"""
    
    GITHUB_API_LIMIT: int = 30
    """GitHub API调用速率限制（次/分钟）"""
    
    GITHUB_CACHE_TTL: int = 3600
    """GitHub数据缓存时间（秒）"""
    
    # LeetCode API配置
    LEETCODE_API_URL: str = "https://leetcode.com/api"
    """LeetCode API基础URL"""
    
    # ModelScope AI模型配置
    MODELSCOPE_API_KEY: Optional[str] = None
    """ModelScope API密钥，用于AI代码分析"""
    
    CODEGEEX_MODEL: str = "codegeex2-6b"
    """CodeGeeX模型名称，用于代码理解和生成"""
    
    # 知识星球API配置（可选）
    ZSXQ_API_KEY: Optional[str] = None
    """知识星球API密钥，用于社区功能"""
    
    ZSXQ_API_URL: str = "https://api.zsxq.com/v2"
    """知识星球API基础URL"""
    
    # 应用基础配置
    APP_NAME: str = "程序员求职加速器Agent"
    """应用名称"""
    
    DEBUG: bool = True
    """调试模式开关，生产环境应设置为False"""
    
    class Config:
        """Pydantic配置类"""
        env_file = ".env"  # 从.env文件加载配置
        case_sensitive = True  # 环境变量名大小写敏感

# 创建全局配置实例
settings = Settings()

# 配置验证函数
def validate_settings():
    """
    验证关键配置项是否正确设置
    
    在生产环境启动时调用，确保必要的配置项已正确设置
    """
    if settings.ENVIRONMENT == "production":
        if settings.SECRET_KEY == "your-secret-key-here":
            raise ValueError("生产环境必须设置复杂的SECRET_KEY")
        if settings.DEBUG:
            raise ValueError("生产环境不应开启DEBUG模式")
    
    # 验证数据库URL格式
    if not settings.DATABASE_URL.startswith(("sqlite://", "postgresql://", "mysql://")):
        raise ValueError("不支持的数据库类型")
    
    print(f"✅ 配置验证通过 - 环境: {settings.ENVIRONMENT}")

# 获取配置摘要（用于日志记录，不包含敏感信息）
def get_config_summary():
    """
    获取配置摘要信息
    
    返回不包含敏感信息的配置概览，用于日志记录和调试
    """
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_type": settings.DATABASE_URL.split("://")[0],
        "frontend_url": settings.FRONTEND_URL,
        "github_configured": bool(settings.GITHUB_TOKEN and settings.GITHUB_TOKEN != "your-token-here"),
        "modelscope_configured": bool(settings.MODELSCOPE_API_KEY),
        "zsxq_configured": bool(settings.ZSXQ_API_KEY)
    }
