"""
Ollama本地AI模型客户端

支持本地部署的免费AI模型，零成本运行
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaClient:
    """Ollama本地AI模型客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 11434):
        self.base_url = f"http://{host}:{port}"
        self.session = None
        self.available_models = [
            "qwen2.5:7b",      # 中文优化模型
            "llama3.1:8b",     # 通用模型
            "codellama:7b",    # 代码专用模型
        ]
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama健康检查失败: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """获取可用模型列表"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("models", [])
                else:
                    logger.error(f"获取模型列表失败: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"获取模型列表异常: {e}")
            return []
    
    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "top_k": kwargs.get("top_k", 40),
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama API错误: {response.status} - {error_text}")
                    
        except asyncio.TimeoutError:
            raise Exception("Ollama响应超时，请检查模型是否正在运行")
        except Exception as e:
            logger.error(f"Ollama聊天调用失败: {e}")
            raise
    
    async def generate(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """文本生成"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                }
            }
            
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama生成错误: {response.status} - {error_text}")
                    
        except asyncio.TimeoutError:
            raise Exception("Ollama生成超时")
        except Exception as e:
            logger.error(f"Ollama生成调用失败: {e}")
            raise
    
    async def pull_model(self, model: str) -> bool:
        """拉取模型"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            payload = {"name": model}
            
            async with self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=600)  # 10分钟超时
            ) as response:
                if response.status == 200:
                    logger.info(f"模型 {model} 拉取成功")
                    return True
                else:
                    logger.error(f"模型 {model} 拉取失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"拉取模型 {model} 异常: {e}")
            return False
    
    async def get_best_model(self, task_type: str = "general") -> str:
        """根据任务类型选择最佳模型"""
        model_preferences = {
            "general": "qwen2.5:7b",      # 通用任务优先中文模型
            "code": "codellama:7b",       # 代码任务
            "english": "llama3.1:8b",     # 英文任务
            "chinese": "qwen2.5:7b",      # 中文任务
        }
        
        preferred_model = model_preferences.get(task_type, "qwen2.5:7b")
        
        # 检查模型是否可用
        available_models = await self.list_models()
        available_names = [m.get("name", "") for m in available_models]
        
        if preferred_model in available_names:
            return preferred_model
        
        # 如果首选模型不可用，返回第一个可用模型
        for model in self.available_models:
            if model in available_names:
                return model
        
        # 如果没有可用模型，返回默认模型
        return "qwen2.5:7b" 