"""
免费AI Agent核心服务

整合本地Ollama、免费Groq API和规则引擎的零成本AI助手
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from .ollama_client import OllamaClient
from .groq_client import GroqClient
from .rule_based_engine import RuleBasedEngine
from .usage_tracker import usage_tracker

logger = logging.getLogger(__name__)

class FreeAIAgentService:
    """免费AI Agent核心服务"""
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.groq = GroqClient()
        self.rule_engine = RuleBasedEngine()
        
        # 系统提示词
        self.system_prompt = """你是小智，一个专业的程序员求职助手。你的主要职责是：

1. 技能分析：帮助用户分析编程技能水平，识别优势和不足
2. 学习规划：制定个性化学习计划和职业发展路径
3. 求职指导：提供简历优化、面试准备、岗位匹配建议
4. 编程学习：推荐学习资源、解答技术问题、指导项目实践

请用友善、专业的语调回答，提供实用的建议。如果不确定答案，请诚实说明并建议用户寻求其他资源。
保持回答简洁明了，重点突出，避免冗长的解释。"""
        
        # 模型选择策略
        self.model_strategy = {
            "simple": "rule_based",     # 简单问题用规则引擎
            "complex": "ollama",        # 复杂问题优先用本地模型
            "fallback": "groq",         # 备用云端模型
            "emergency": "rule_based"   # 紧急兜底
        }
    
    async def chat(self, message: str, user_id: int, context: Dict = None) -> Dict[str, Any]:
        """智能聊天 - 零成本策略"""
        try:
            # 1. 记录对话开始
            start_time = datetime.now()
            
            # 2. 获取用户上下文
            user_context = await self._get_user_context(user_id, context)
            
            # 3. 智能选择回复方式
            response = await self._get_intelligent_response(message, user_id, user_context)
            
            # 4. 记录使用统计
            await usage_tracker.increment_usage(user_id, response["source"])
            
            # 5. 计算响应时间
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "response": response["content"],
                "source": response["source"],
                "suggestions": response.get("suggestions", []),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "model": response.get("model", "unknown"),
                    "confidence": response.get("confidence", 0.0),
                    "response_time": response_time,
                    "intent": response.get("intent", "unknown"),
                    "topic": response.get("topic", "general")
                }
            }
            
        except Exception as e:
            logger.error(f"AI聊天失败: {e}")
            # 紧急兜底回复
            emergency_response = await self.rule_engine.generate_response(
                message, {"user_id": user_id}
            )
            
            return {
                "success": False,
                "response": emergency_response["content"],
                "source": "rule_based_emergency",
                "suggestions": emergency_response.get("suggestions", []),
                "error": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "fallback": True
                }
            }
    
    async def _get_intelligent_response(self, message: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """智能选择最佳回复方式"""
        # 1. 判断问题复杂度
        complexity = self._assess_query_complexity(message)
        
        # 2. 检查简单问题（优先使用规则引擎）
        if complexity == "simple":
            logger.debug(f"使用规则引擎处理简单问题: {message[:50]}...")
            return await self.rule_engine.generate_response(message, context)
        
        # 3. 尝试本地Ollama模型（复杂问题首选）
        if complexity in ["complex", "medium"]:
            try:
                if await self._is_ollama_available():
                    logger.debug(f"使用Ollama处理复杂问题: {message[:50]}...")
                    response_content = await self._ollama_chat(message, context)
                    return {
                        "content": response_content,
                        "source": "ollama_local",
                        "model": await self.ollama.get_best_model("general"),
                        "confidence": 0.9,
                        "suggestions": self._extract_suggestions(response_content)
                    }
            except Exception as e:
                logger.warning(f"Ollama调用失败，尝试备用方案: {e}")
        
        # 4. 检查Groq免费额度
        if await self._check_groq_available(user_id):
            try:
                logger.debug(f"使用Groq处理问题: {message[:50]}...")
                response_data = await self._groq_chat(message, context)
                return {
                    "content": response_data["content"],
                    "source": "groq_api",
                    "model": response_data["model"],
                    "confidence": 0.95,
                    "suggestions": self._extract_suggestions(response_data["content"])
                }
            except Exception as e:
                logger.warning(f"Groq调用失败，降级到规则引擎: {e}")
        
        # 5. 最后降级到规则引擎
        logger.debug(f"降级到规则引擎: {message[:50]}...")
        rule_response = await self.rule_engine.generate_response(message, context)
        rule_response["fallback_reason"] = "ai_models_unavailable"
        return rule_response
    
    def _assess_query_complexity(self, message: str) -> str:
        """评估查询复杂度"""
        message_lower = message.lower().strip()
        
        # 简单问题模式
        simple_patterns = [
            r"^(你好|hi|hello|嗨).*",
            r"^(谢谢|感谢|thanks?).*",
            r"^(再见|bye|拜拜).*",
            r"^(是|好的|ok|行|可以)$",
            r"^(不|不是|no|不行)$"
        ]
        
        # 复杂问题模式
        complex_patterns = [
            r".*(如何.*实现|怎么.*开发|设计.*架构).*",
            r".*(算法.*优化|性能.*提升|代码.*重构).*",
            r".*(职业.*规划|学习.*路径|技能.*提升).*",
            r".*(面试.*准备|简历.*优化|项目.*经验).*"
        ]
        
        import re
        
        # 检查简单模式
        for pattern in simple_patterns:
            if re.match(pattern, message_lower):
                return "simple"
        
        # 检查复杂模式
        for pattern in complex_patterns:
            if re.search(pattern, message_lower):
                return "complex"
        
        # 根据长度和问号数量判断
        if len(message) < 20:
            return "simple"
        elif len(message) > 100 or message.count('?') > 1 or message.count('？') > 1:
            return "complex"
        else:
            return "medium"
    
    async def _is_ollama_available(self) -> bool:
        """检查Ollama是否可用"""
        try:
            return await self.ollama.health_check()
        except Exception as e:
            logger.debug(f"Ollama不可用: {e}")
            return False
    
    async def _check_groq_available(self, user_id: int) -> bool:
        """检查Groq是否可用"""
        try:
            if not self.groq.is_configured():
                return False
            
            # 检查用户额度
            if not await self.groq.check_quota(user_id):
                return False
            
            return True
        except Exception as e:
            logger.debug(f"Groq不可用: {e}")
            return False
    
    async def _ollama_chat(self, message: str, context: Dict) -> str:
        """使用Ollama进行对话"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 添加上下文信息
        context_info = self._format_context(context)
        if context_info:
            messages.append({"role": "system", "content": context_info})
        
        messages.append({"role": "user", "content": message})
        
        # 选择最佳模型
        best_model = await self.ollama.get_best_model("general")
        
        async with self.ollama as client:
            response = await client.chat(best_model, messages, temperature=0.7)
            return response["message"]["content"]
    
    async def _groq_chat(self, message: str, context: Dict) -> Dict[str, Any]:
        """使用Groq进行对话"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # 添加上下文信息
        context_info = self._format_context(context)
        if context_info:
            messages.append({"role": "system", "content": context_info})
        
        messages.append({"role": "user", "content": message})
        
        # 选择最佳模型
        best_model = await self.groq.get_best_model("general")
        
        async with self.groq as client:
            return await client.chat_completion(messages, model=best_model, max_tokens=1000)
    
    def _format_context(self, context: Dict) -> str:
        """格式化用户上下文"""
        if not context:
            return ""
        
        context_parts = []
        
        if "skill_level" in context:
            context_parts.append(f"用户技能水平: {context['skill_level']}")
        
        if "target_job" in context:
            context_parts.append(f"目标岗位: {context['target_job']}")
        
        if "learning_progress" in context:
            context_parts.append(f"学习进度: {context['learning_progress']}")
        
        if "recent_topics" in context:
            context_parts.append(f"最近讨论: {', '.join(context['recent_topics'][-3:])}")
        
        if context_parts:
            return "用户背景信息:\n" + "\n".join(context_parts)
        
        return ""
    
    def _extract_suggestions(self, response_content: str) -> List[str]:
        """从回复中提取建议"""
        suggestions = []
        
        # 简单的建议提取逻辑
        if "技能分析" in response_content:
            suggestions.append("查看技能分析报告")
        if "学习" in response_content:
            suggestions.append("制定学习计划")
        if "求职" in response_content or "面试" in response_content:
            suggestions.append("查看求职指导")
        if "项目" in response_content:
            suggestions.append("获取项目建议")
        
        # 默认建议
        if not suggestions:
            suggestions = ["继续对话", "查看更多功能"]
        
        return suggestions[:3]  # 最多3个建议
    
    async def _get_user_context(self, user_id: int, additional_context: Dict = None) -> Dict:
        """获取用户上下文"""
        context = additional_context or {}
        context["user_id"] = user_id
        
        try:
            # 从数据库获取用户信息
            from app.models.user import User
            from app.models.skill import Skill
            from app.database import get_db
            
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if user:
                # 获取技能信息
                skills = db.query(Skill).filter(Skill.user_id == user_id).all()
                if skills:
                    skill_levels = [skill.proficiency_level for skill in skills]
                    avg_skill = sum(skill_levels) / len(skill_levels)
                    
                    if avg_skill >= 80:
                        context["skill_level"] = "advanced"
                    elif avg_skill >= 50:
                        context["skill_level"] = "intermediate"
                    else:
                        context["skill_level"] = "beginner"
                    
                    # 获取主要技能
                    top_skills = sorted(skills, key=lambda x: x.proficiency_level, reverse=True)[:3]
                    context["top_skills"] = [skill.name for skill in top_skills]
            
            # 获取对话历史中的话题
            context_memory = self.rule_engine.get_context_memory(str(user_id))
            if context_memory:
                recent_topics = []
                for conv in context_memory[-3:]:  # 最近3轮对话
                    # 简单的话题提取
                    content = conv.get("query", "").lower()
                    if "学习" in content:
                        recent_topics.append("学习规划")
                    elif "求职" in content:
                        recent_topics.append("求职指导")
                    elif "技能" in content:
                        recent_topics.append("技能分析")
                
                context["recent_topics"] = recent_topics
            
        except Exception as e:
            logger.error(f"获取用户上下文失败: {e}")
        
        return context
    
    async def generate_daily_task(self, user_id: int) -> Dict[str, Any]:
        """生成每日任务 - 免费版"""
        try:
            # 获取用户上下文
            context = await self._get_user_context(user_id)
            
            # 使用规则引擎生成任务（零成本）
            task = await self._generate_rule_based_task(user_id, context)
            
            # 记录使用量
            await usage_tracker.increment_usage(user_id, "rule_based")
            
            return {
                "success": True,
                "task": task,
                "source": "rule_based",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成每日任务失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_task": self._get_fallback_task()
            }
    
    async def _generate_rule_based_task(self, user_id: int, context: Dict) -> Dict[str, Any]:
        """基于规则生成任务"""
        import random
        
        # 任务模板
        task_templates = {
            "beginner": [
                {
                    "title": "学习编程基础",
                    "description": "选择一门编程语言，学习基本语法和概念",
                    "type": "learning",
                    "estimated_minutes": 60,
                    "resources": ["官方教程", "在线课程", "练习题"],
                    "objectives": ["掌握基本语法", "理解编程概念", "完成简单练习"]
                },
                {
                    "title": "完成编程练习",
                    "description": "在LeetCode或其他平台完成3道简单题目",
                    "type": "practice",
                    "estimated_minutes": 90,
                    "resources": ["LeetCode", "牛客网", "HackerRank"],
                    "objectives": ["解决算法问题", "提高编程思维", "积累经验"]
                }
            ],
            "intermediate": [
                {
                    "title": "项目实践",
                    "description": "开发一个小项目，应用所学知识",
                    "type": "project",
                    "estimated_minutes": 120,
                    "resources": ["GitHub", "技术文档", "开源项目"],
                    "objectives": ["应用技能", "积累项目经验", "提升实战能力"]
                },
                {
                    "title": "算法学习",
                    "description": "学习一个新的算法或数据结构",
                    "type": "learning",
                    "estimated_minutes": 75,
                    "resources": ["算法书籍", "视频教程", "在线课程"],
                    "objectives": ["掌握新算法", "理解数据结构", "提升思维能力"]
                }
            ],
            "advanced": [
                {
                    "title": "技术深入",
                    "description": "深入学习某个技术领域的高级特性",
                    "type": "advanced",
                    "estimated_minutes": 90,
                    "resources": ["技术博客", "官方文档", "开源代码"],
                    "objectives": ["掌握高级特性", "理解底层原理", "提升专业深度"]
                },
                {
                    "title": "代码优化",
                    "description": "优化现有项目的性能和代码质量",
                    "type": "optimization",
                    "estimated_minutes": 100,
                    "resources": ["性能分析工具", "代码审查", "最佳实践"],
                    "objectives": ["提升代码质量", "优化性能", "学习最佳实践"]
                }
            ]
        }
        
        # 根据用户水平选择任务
        skill_level = context.get("skill_level", "beginner")
        templates = task_templates.get(skill_level, task_templates["beginner"])
        
        # 随机选择一个任务模板
        template = random.choice(templates)
        
        # 根据用户技能定制任务
        if context.get("top_skills"):
            main_skill = context["top_skills"][0]
            template["description"] = template["description"].replace("编程语言", main_skill)
            template["title"] = template["title"].replace("编程", main_skill)
        
        # 生成具体任务
        task = {
            "id": f"task_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "title": template["title"],
            "description": template["description"],
            "type": template["type"],
            "estimated_minutes": template["estimated_minutes"],
            "resources": template["resources"],
            "objectives": template["objectives"],
            "created_at": datetime.now(),
            "due_date": datetime.now() + timedelta(days=1),
            "status": "pending",
            "difficulty": skill_level,
            "points": self._calculate_task_points(template, skill_level)
        }
        
        return task
    
    def _calculate_task_points(self, template: Dict, skill_level: str) -> int:
        """计算任务积分"""
        base_points = {
            "learning": 10,
            "practice": 15,
            "project": 25,
            "advanced": 30,
            "optimization": 20
        }
        
        level_multiplier = {
            "beginner": 1.0,
            "intermediate": 1.2,
            "advanced": 1.5
        }
        
        task_type = template.get("type", "learning")
        points = base_points.get(task_type, 10)
        multiplier = level_multiplier.get(skill_level, 1.0)
        
        return int(points * multiplier)
    
    def _get_fallback_task(self) -> Dict[str, Any]:
        """获取兜底任务"""
        return {
            "id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": "每日编程练习",
            "description": "完成一道编程题目，保持编程手感",
            "type": "practice",
            "estimated_minutes": 30,
            "resources": ["LeetCode", "牛客网"],
            "objectives": ["保持编程习惯"],
            "status": "pending",
            "points": 10
        }
    
    async def get_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            stats = await usage_tracker.get_all_usage_stats(user_id)
            
            # 添加模型可用性信息
            stats["model_availability"] = {
                "ollama": await self._is_ollama_available(),
                "groq": await self._check_groq_available(user_id),
                "rule_based": True  # 规则引擎始终可用
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取使用统计失败: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "services": {}
            }
            
            # 检查Ollama
            try:
                ollama_healthy = await self.ollama.health_check()
                health_status["services"]["ollama"] = {
                    "status": "healthy" if ollama_healthy else "unavailable",
                    "available_models": await self.ollama.list_models() if ollama_healthy else []
                }
            except Exception as e:
                health_status["services"]["ollama"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # 检查Groq
            try:
                groq_healthy = await self.groq.health_check()
                health_status["services"]["groq"] = {
                    "status": "healthy" if groq_healthy else "unavailable",
                    "configured": self.groq.is_configured()
                }
            except Exception as e:
                health_status["services"]["groq"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # 检查规则引擎
            health_status["services"]["rule_engine"] = {
                "status": "healthy",
                "knowledge_topics": len(self.rule_engine.knowledge_base)
            }
            
            # 判断整体状态
            available_services = sum(1 for service in health_status["services"].values() 
                                   if service["status"] == "healthy")
            
            if available_services == 0:
                health_status["overall_status"] = "critical"
            elif available_services < len(health_status["services"]):
                health_status["overall_status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            } 