"""
基于规则的智能引擎

当免费AI模型不可用时的智能兜底方案
"""

import re
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RuleBasedEngine:
    """基于规则的智能引擎"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.intent_patterns = self._load_intent_patterns()
        self.response_templates = self._load_response_templates()
        self.context_memory = {}  # 简单的上下文记忆
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """加载知识库"""
        return {
            "技能分析": {
                "keywords": ["技能", "能力", "水平", "分析", "评估", "skill", "ability"],
                "responses": [
                    "根据你的GitHub和LeetCode数据，我可以为你分析技能水平。",
                    "技能分析可以帮助你了解自己的优势和不足。",
                    "建议你先完成技能分析，然后制定学习计划。",
                    "我可以从多个维度评估你的技术能力：编程语言、算法能力、项目经验等。"
                ],
                "suggestions": [
                    "查看技能分析报告",
                    "上传代码进行分析",
                    "连接GitHub账号",
                    "输入LeetCode用户名"
                ]
            },
            "学习规划": {
                "keywords": ["学习", "计划", "路径", "规划", "提升", "learning", "plan", "study"],
                "responses": [
                    "我可以根据你的目标制定个性化学习路径。",
                    "学习计划应该循序渐进，建议从基础开始。",
                    "每日坚持学习1-2小时，效果会更好。",
                    "根据你的技能水平和目标岗位，我会推荐最适合的学习资源。"
                ],
                "suggestions": [
                    "生成学习路径",
                    "设定学习目标",
                    "查看推荐资源",
                    "制定学习计划"
                ]
            },
            "求职指导": {
                "keywords": ["求职", "面试", "简历", "工作", "岗位", "job", "interview", "resume"],
                "responses": [
                    "求职前建议先完善技能，提高竞争力。",
                    "简历要突出项目经验和技术能力。",
                    "面试时要展现你的学习能力和解决问题的思路。",
                    "我可以帮你分析岗位要求，匹配你的技能水平。"
                ],
                "suggestions": [
                    "分析简历",
                    "岗位匹配",
                    "面试准备",
                    "技能提升建议"
                ]
            },
            "编程学习": {
                "keywords": ["编程", "代码", "算法", "开发", "语言", "programming", "code", "algorithm"],
                "responses": [
                    "编程学习要理论结合实践，多写项目。",
                    "建议从一门语言开始，深入学习后再扩展。",
                    "LeetCode刷题可以提高算法思维。",
                    "项目经验比单纯的理论学习更重要。"
                ],
                "suggestions": [
                    "选择编程语言",
                    "制定练习计划",
                    "推荐学习资源",
                    "项目实战指导"
                ]
            },
            "职业发展": {
                "keywords": ["职业", "发展", "晋升", "转行", "career", "development"],
                "responses": [
                    "职业发展需要明确目标和持续学习。",
                    "技术岗位要保持技术敏感度，关注行业趋势。",
                    "软技能和硬技能同样重要。",
                    "建议制定3-5年的职业规划。"
                ],
                "suggestions": [
                    "职业规划",
                    "技能提升",
                    "行业分析",
                    "发展建议"
                ]
            },
            "项目经验": {
                "keywords": ["项目", "经验", "作品", "portfolio", "project"],
                "responses": [
                    "项目经验是技术能力的最好证明。",
                    "建议从小项目开始，逐步增加复杂度。",
                    "开源项目是很好的学习和展示平台。",
                    "项目要有完整的文档和演示。"
                ],
                "suggestions": [
                    "项目创意",
                    "技术选型",
                    "项目管理",
                    "作品展示"
                ]
            }
        }
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """加载意图识别模式"""
        return {
            "greeting": [
                r"你好|hi|hello|嗨|您好",
                r"早上好|下午好|晚上好|morning|afternoon|evening",
                r"在吗|在不在|are you there"
            ],
            "question": [
                r".*\?|.*？",
                r"怎么.*|如何.*|什么.*|为什么.*|为啥.*",
                r"how.*|what.*|why.*|when.*|where.*"
            ],
            "request": [
                r"帮我.*|给我.*|我想.*|请.*",
                r"可以.*吗|能.*吗|能否.*",
                r"help.*|please.*|can you.*"
            ],
            "complaint": [
                r"不好|不行|有问题|bug|错误",
                r"慢|卡|不工作|failed|error",
                r"没用|不对|wrong"
            ],
            "praise": [
                r"好的|不错|很好|棒|excellent|good|great",
                r"谢谢|感谢|thank you|thanks",
                r"有用|有帮助|helpful"
            ]
        }
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """加载回复模板"""
        return {
            "greeting": [
                "你好！我是小智，你的AI学习助手。有什么可以帮助你的吗？",
                "嗨！很高兴为你服务，我可以帮你规划学习路径和职业发展。",
                "你好！我可以协助你进行技能分析、学习规划和求职指导。",
                "欢迎！我是专业的程序员求职助手，随时为你答疑解惑。"
            ],
            "question": [
                "这是个很好的问题！让我为你分析一下...",
                "根据我的理解，这个问题可以从几个角度来看...",
                "我来帮你解答这个问题。",
                "让我基于我的知识为你详细解释..."
            ],
            "request": [
                "当然可以！我很乐意帮助你。",
                "没问题，我来协助你完成这个任务。",
                "我会尽力帮助你实现这个目标。",
                "好的，让我为你提供详细的指导。"
            ],
            "complaint": [
                "抱歉给你带来了困扰，让我帮你解决这个问题。",
                "我理解你的困难，让我们一起找到解决方案。",
                "感谢你的反馈，我会努力改进。",
                "让我帮你分析问题所在，找到更好的解决办法。"
            ],
            "praise": [
                "谢谢你的认可！我会继续努力帮助你。",
                "很高兴能帮到你！还有其他需要协助的吗？",
                "感谢你的反馈！有任何问题随时找我。",
                "能够帮助你我很开心！继续加油！"
            ],
            "default": [
                "我理解你的意思，让我为你提供一些建议。",
                "基于你的情况，我建议你可以考虑以下几点。",
                "这确实是个值得思考的问题。",
                "让我根据我的知识为你提供一些想法。"
            ]
        }
    
    async def generate_response(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """生成规则化回复"""
        try:
            # 1. 预处理查询
            processed_query = self._preprocess_query(query)
            
            # 2. 意图识别
            intent = self._identify_intent(processed_query)
            
            # 3. 关键词匹配
            topic = self._match_topic(processed_query)
            
            # 4. 生成回复
            response = self._generate_contextual_response(
                processed_query, intent, topic, user_context
            )
            
            # 5. 生成建议
            suggestions = self._generate_suggestions(topic, user_context)
            
            # 6. 更新上下文记忆
            self._update_context_memory(query, response, user_context)
            
            return {
                "content": response,
                "intent": intent,
                "topic": topic,
                "suggestions": suggestions,
                "confidence": self._calculate_confidence(intent, topic),
                "source": "rule_based",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"规则引擎生成回复失败: {e}")
            return {
                "content": "抱歉，我现在有点忙，请稍后再试或者描述得更具体一些。",
                "intent": "unknown",
                "topic": "general",
                "suggestions": ["重新描述问题", "查看帮助文档"],
                "confidence": 0.1,
                "source": "rule_based_fallback"
            }
    
    def _preprocess_query(self, query: str) -> str:
        """预处理查询"""
        # 转换为小写
        processed = query.lower().strip()
        
        # 移除多余的空格
        processed = re.sub(r'\s+', ' ', processed)
        
        # 移除特殊字符（保留中文、英文、数字、常用标点）
        processed = re.sub(r'[^\w\s\u4e00-\u9fff\?\!\.，。？！]', '', processed)
        
        return processed
    
    def _identify_intent(self, query: str) -> str:
        """识别用户意图"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        return "unknown"
    
    def _match_topic(self, query: str) -> str:
        """匹配话题"""
        topic_scores = {}
        
        for topic, info in self.knowledge_base.items():
            score = 0
            for keyword in info["keywords"]:
                # 完全匹配得分更高
                if keyword in query:
                    score += 2
                # 部分匹配
                elif any(keyword in word for word in query.split()):
                    score += 1
            
            if score > 0:
                topic_scores[topic] = score
        
        if topic_scores:
            return max(topic_scores, key=topic_scores.get)
        
        return "general"
    
    def _generate_contextual_response(self, query: str, intent: str, topic: str, context: Dict) -> str:
        """生成上下文相关回复"""
        # 基础回复
        base_response = self._get_base_response(intent, topic)
        
        # 添加个性化内容
        if context:
            personal_touch = self._add_personal_context(base_response, context, topic)
            if personal_touch:
                base_response = personal_touch
        
        # 添加具体建议
        specific_advice = self._get_specific_advice(topic, context)
        if specific_advice:
            base_response += f"\n\n{specific_advice}"
        
        return base_response
    
    def _get_base_response(self, intent: str, topic: str) -> str:
        """获取基础回复"""
        # 优先使用话题相关回复
        if topic in self.knowledge_base:
            responses = self.knowledge_base[topic]["responses"]
            return random.choice(responses)
        
        # 使用意图相关回复
        if intent in self.response_templates:
            responses = self.response_templates[intent]
            return random.choice(responses)
        
        # 默认回复
        return random.choice(self.response_templates["default"])
    
    def _add_personal_context(self, response: str, context: Dict, topic: str) -> str:
        """添加个性化上下文"""
        if not context:
            return response
        
        # 根据用户技能水平调整回复
        skill_level = context.get("skill_level", "beginner")
        
        if skill_level == "advanced":
            if topic == "学习规划":
                return response + " 以你的技术水平，可以考虑更具挑战性的项目和技术深度学习。"
            elif topic == "求职指导":
                return response + " 凭借你的高级技能，可以考虑技术领导或架构师方向的职位。"
        elif skill_level == "beginner":
            if topic == "学习规划":
                return response + " 建议从基础开始，循序渐进地学习，不要急于求成。"
            elif topic == "编程学习":
                return response + " 新手建议先掌握一门编程语言的基础语法，多做练习。"
        
        # 根据目标岗位调整
        target_job = context.get("target_job", "")
        if target_job:
            if "前端" in target_job:
                return response + f" 针对{target_job}岗位，建议重点关注前端技术栈的学习。"
            elif "后端" in target_job:
                return response + f" 针对{target_job}岗位，建议重点学习后端开发和数据库技术。"
        
        return response
    
    def _get_specific_advice(self, topic: str, context: Dict) -> str:
        """获取具体建议"""
        advice_map = {
            "技能分析": "你可以通过GitHub分析、LeetCode分析等功能来全面了解自己的技能水平。",
            "学习规划": "建议设定明确的学习目标，制定详细的时间计划，并定期评估学习效果。",
            "求职指导": "完善你的技术简历，准备技术面试，关注目标公司的技术栈要求。",
            "编程学习": "推荐采用项目驱动的学习方式，在实践中掌握编程技能。",
            "职业发展": "持续关注行业趋势，培养核心竞争力，建立专业人脉网络。"
        }
        
        return advice_map.get(topic, "")
    
    def _generate_suggestions(self, topic: str, context: Dict) -> List[str]:
        """生成建议"""
        if topic in self.knowledge_base:
            base_suggestions = self.knowledge_base[topic].get("suggestions", [])
        else:
            base_suggestions = ["查看帮助文档", "联系技术支持"]
        
        # 根据上下文添加个性化建议
        if context:
            skill_level = context.get("skill_level", "")
            if skill_level == "beginner":
                base_suggestions.insert(0, "从基础教程开始")
            elif skill_level == "advanced":
                base_suggestions.insert(0, "查看高级技能指南")
        
        return base_suggestions[:4]  # 最多返回4个建议
    
    def _calculate_confidence(self, intent: str, topic: str) -> float:
        """计算置信度"""
        confidence = 0.5  # 基础置信度
        
        if intent != "unknown":
            confidence += 0.2
        
        if topic != "general":
            confidence += 0.2
        
        if topic in self.knowledge_base:
            confidence += 0.1
        
        return min(confidence, 0.9)  # 最高0.9
    
    def _update_context_memory(self, query: str, response: str, context: Dict):
        """更新上下文记忆"""
        try:
            user_id = context.get("user_id") if context else "anonymous"
            
            if user_id not in self.context_memory:
                self.context_memory[user_id] = []
            
            # 保存最近5轮对话
            self.context_memory[user_id].append({
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            # 只保留最近5轮
            if len(self.context_memory[user_id]) > 5:
                self.context_memory[user_id] = self.context_memory[user_id][-5:]
                
        except Exception as e:
            logger.error(f"更新上下文记忆失败: {e}")
    
    def get_context_memory(self, user_id: str) -> List[Dict]:
        """获取用户的上下文记忆"""
        return self.context_memory.get(user_id, [])
    
    def clear_context_memory(self, user_id: str):
        """清除用户的上下文记忆"""
        if user_id in self.context_memory:
            del self.context_memory[user_id] 