"""
Groq免费API客户端

提供免费的高速AI推理服务作为备用方案
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging
import os
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class GroqClient:
    """Groq免费API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.base_url = "https://api.groq.com/openai/v1"
        self.session = None
        
        # 免费限制
        self.daily_limit = 100  # 每日免费请求限制
        self.rate_limit = 30    # 每分钟请求限制
        
        # 可用的免费模型
        self.available_models = [
            "llama3-8b-8192",      # 主推模型
            "mixtral-8x7b-32768",  # 备用模型
            "gemma-7b-it",         # 轻量模型
        ]
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def chat_completion(self, messages: list, model: str = "llama3-8b-8192", **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        if not self.api_key:
            raise Exception("Groq API Key未配置")
            
        if not self.session:
            await self.__aenter__()
            
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "stream": False
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "usage": data.get("usage", {}),
                        "model": model,
                        "finish_reason": data["choices"][0].get("finish_reason"),
                        "created": data.get("created")
                    }
                elif response.status == 429:
                    raise Exception("Groq API速率限制，请稍后重试")
                elif response.status == 401:
                    raise Exception("Groq API Key无效")
                else:
                    error_text = await response.text()
                    raise Exception(f"Groq API错误: {response.status} - {error_text}")
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Groq网络请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"Groq API调用失败: {e}")
            raise
    
    async def check_quota(self, user_id: int) -> bool:
        """检查用户免费额度"""
        try:
            from .usage_tracker import UsageTracker
            tracker = UsageTracker()
            
            daily_usage = await tracker.get_daily_usage(user_id, "groq")
            minute_usage = await tracker.get_minute_usage(user_id, "groq")
            
            # 检查每日限制
            if daily_usage >= self.daily_limit:
                logger.warning(f"用户 {user_id} Groq每日额度已用完: {daily_usage}/{self.daily_limit}")
                return False
            
            # 检查每分钟限制
            if minute_usage >= self.rate_limit:
                logger.warning(f"用户 {user_id} Groq每分钟额度已用完: {minute_usage}/{self.rate_limit}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查Groq额度失败: {e}")
            return False
    
    async def get_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            from .usage_tracker import UsageTracker
            tracker = UsageTracker()
            
            daily_usage = await tracker.get_daily_usage(user_id, "groq")
            minute_usage = await tracker.get_minute_usage(user_id, "groq")
            
            return {
                "daily_used": daily_usage,
                "daily_limit": self.daily_limit,
                "daily_remaining": max(0, self.daily_limit - daily_usage),
                "minute_used": minute_usage,
                "minute_limit": self.rate_limit,
                "minute_remaining": max(0, self.rate_limit - minute_usage),
                "usage_percentage": (daily_usage / self.daily_limit) * 100
            }
            
        except Exception as e:
            logger.error(f"获取Groq使用统计失败: {e}")
            return {
                "daily_used": 0,
                "daily_limit": self.daily_limit,
                "daily_remaining": self.daily_limit,
                "minute_used": 0,
                "minute_limit": self.rate_limit,
                "minute_remaining": self.rate_limit,
                "usage_percentage": 0
            }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.api_key:
                return False
                
            if not self.session:
                await self.__aenter__()
            
            # 发送一个简单的测试请求
            test_messages = [{"role": "user", "content": "test"}]
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": "llama3-8b-8192",
                    "messages": test_messages,
                    "max_tokens": 1
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status in [200, 429]  # 200成功，429限制但服务可用
                
        except Exception as e:
            logger.warning(f"Groq健康检查失败: {e}")
            return False
    
    def is_configured(self) -> bool:
        """检查是否已配置API Key"""
        return bool(self.api_key and self.api_key.strip())
    
    async def get_best_model(self, task_type: str = "general") -> str:
        """根据任务类型选择最佳模型"""
        model_preferences = {
            "general": "llama3-8b-8192",      # 通用任务
            "code": "llama3-8b-8192",         # 代码任务
            "creative": "mixtral-8x7b-32768", # 创意任务
            "fast": "gemma-7b-it",            # 快速响应
        }
        
        return model_preferences.get(task_type, "llama3-8b-8192") 