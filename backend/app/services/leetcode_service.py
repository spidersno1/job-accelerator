import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import json
import time
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import re
from functools import wraps
import redis
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 缓存配置
CACHE_EXPIRY = 3600  # 1小时
RATE_LIMIT_WINDOW = 60  # 1分钟
RATE_LIMIT_REQUESTS = 10  # 每分钟最多10个请求

# 在生产环境中应该使用Redis
class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            if time.time() - self.timestamps[key] < CACHE_EXPIRY:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        self.cache[key] = value
        self.timestamps[key] = time.time()

# 全局缓存实例
cache = SimpleCache()

# 速率限制器
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        now = time.time()
        # 清理过期的请求记录
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if now - req_time < RATE_LIMIT_WINDOW]
        
        if len(self.requests[key]) >= RATE_LIMIT_REQUESTS:
            return False
        
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(func):
    """速率限制装饰器"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # 使用第一个参数作为限制键（通常是用户名）
        key = str(args[0]) if args else "default"
        
        if not rate_limiter.is_allowed(key):
            raise LeetCodeServiceException(
                "请求过于频繁，请稍后再试",
                error_code="RATE_LIMIT_EXCEEDED"
            )
        
        return await func(self, *args, **kwargs)
    return wrapper

def cache_result(expiry: int = CACHE_EXPIRY):
    """缓存结果装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(self, *args, **kwargs)
            cache.set(cache_key, result)
            logger.info(f"Cache set for {cache_key}")
            
            return result
        return wrapper
    return decorator

@dataclass
class LeetCodeAnalysisResult:
    """LeetCode分析结果"""
    user_profile: Dict[str, Any]
    skill_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    learning_recommendations: List[Dict[str, Any]]
    competitive_ranking: Dict[str, Any]
    problem_solving_patterns: Dict[str, Any]
    
class LeetCodeServiceException(Exception):
    """LeetCode服务异常"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class LeetCodeService:
    def __init__(self):
        self.base_url = "https://leetcode.com/api"
        self.graphql_url = "https://leetcode.com/graphql"
        self.headers = {
            "User-Agent": "JobAcceleratorAgent/2.0 (Commercial Grade)",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache"
        }
        
        # 技能权重配置
        self.skill_weights = {
            "algorithm": {
                "Easy": 1.0,
                "Medium": 2.5,
                "Hard": 5.0
            },
            "data_structure": {
                "Easy": 1.2,
                "Medium": 3.0,
                "Hard": 6.0
            },
            "problem_solving": {
                "consistency": 2.0,
                "efficiency": 1.5,
                "accuracy": 2.5
            }
        }
        
        # 技能分类映射
        self.skill_categories = {
            "Array": "数组处理",
            "String": "字符串处理",
            "Hash Table": "哈希表",
            "Dynamic Programming": "动态规划",
            "Two Pointers": "双指针",
            "Binary Search": "二分查找",
            "Sliding Window": "滑动窗口",
            "Backtracking": "回溯算法",
            "Greedy": "贪心算法",
            "Tree": "树结构",
            "Graph": "图算法",
            "Linked List": "链表",
            "Stack": "栈",
            "Queue": "队列",
            "Heap": "堆",
            "Trie": "字典树"
        }
    
    @rate_limit
    @cache_result(expiry=1800)  # 30分钟缓存
    async def get_comprehensive_analysis(self, username_or_url: str) -> LeetCodeAnalysisResult:
        """获取全面的LeetCode分析"""
        try:
            username = self._extract_username_from_url(username_or_url)
            if not username:
                raise LeetCodeServiceException(
                    "无效的用户名或URL",
                    error_code="INVALID_INPUT"
                )
            
            # 并行获取用户数据
            user_info, contest_info, submission_stats = await asyncio.gather(
                self._get_user_info(username),
                self._get_contest_info(username),
                self._get_submission_statistics(username),
                return_exceptions=True
            )
            
            # 处理异常
            if isinstance(user_info, Exception):
                raise LeetCodeServiceException(
                    f"获取用户信息失败: {str(user_info)}",
                    error_code="USER_INFO_ERROR"
                )
            
            if not user_info:
                raise LeetCodeServiceException(
                    f"用户'{username}'不存在",
                    error_code="USER_NOT_FOUND"
                )
            
            # 生成综合分析
            analysis_result = LeetCodeAnalysisResult(
                user_profile=await self._build_user_profile(user_info, contest_info),
                skill_analysis=await self._analyze_skills_advanced(user_info),
                performance_metrics=await self._calculate_performance_metrics(user_info, submission_stats),
                learning_recommendations=await self._generate_learning_recommendations(user_info),
                competitive_ranking=await self._analyze_competitive_ranking(contest_info),
                problem_solving_patterns=await self._analyze_problem_solving_patterns(user_info)
            )
            
            return analysis_result
            
        except LeetCodeServiceException:
            raise
        except Exception as e:
            logger.error(f"LeetCode分析失败: {str(e)}")
            raise LeetCodeServiceException(
                "分析过程中发生未知错误",
                error_code="INTERNAL_ERROR",
                details={"original_error": str(e)}
            )
    
    async def _build_user_profile(self, user_info: Dict[str, Any], contest_info: Dict[str, Any]) -> Dict[str, Any]:
        """构建用户档案"""
        profile = {
            "username": user_info.get("username"),
            "real_name": user_info.get("profile", {}).get("realName"),
            "avatar": user_info.get("profile", {}).get("avatar"),
            "location": user_info.get("profile", {}).get("location"),
            "company": user_info.get("profile", {}).get("company"),
            "school": user_info.get("profile", {}).get("school"),
            "website": user_info.get("profile", {}).get("website"),
            "github": user_info.get("profile", {}).get("github"),
            "linkedin": user_info.get("profile", {}).get("linkedin"),
            "twitter": user_info.get("profile", {}).get("twitter"),
            "about": user_info.get("profile", {}).get("aboutMe"),
            "skill_tags": user_info.get("profile", {}).get("skillTags", []),
            "ranking": user_info.get("profile", {}).get("ranking"),
            "reputation": user_info.get("profile", {}).get("reputation"),
            "contribution_points": user_info.get("contributions", {}).get("points", 0),
            "badges": user_info.get("badges", []),
            "created_at": user_info.get("profile", {}).get("createdAt"),
            "last_active": user_info.get("profile", {}).get("lastModified")
        }
        
        # 添加竞赛信息
        if contest_info and not isinstance(contest_info, Exception):
            profile.update({
                "contest_rating": contest_info.get("userContestRanking", {}).get("rating"),
                "contest_ranking": contest_info.get("userContestRanking", {}).get("globalRanking"),
                "contest_attended": contest_info.get("userContestRanking", {}).get("attendedContestsCount", 0),
                "contest_top_percentage": contest_info.get("userContestRanking", {}).get("topPercentage")
            })
        
        return profile
    
    async def _analyze_skills_advanced(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """高级技能分析"""
        skills = {
            "programming_languages": {},
            "algorithms": {},
            "data_structures": {},
            "problem_solving": {},
            "overall_assessment": {}
        }
        
        # 分析编程语言使用
        language_stats = user_info.get("languageProblemCount", [])
        total_problems = sum(lang.get("problemsSolved", 0) for lang in language_stats)
        
        for lang_stat in language_stats:
            lang_name = lang_stat.get("languageName")
            problems_solved = lang_stat.get("problemsSolved", 0)
            
            if problems_solved > 0:
                proficiency_score = min(100, (problems_solved / max(total_problems, 1)) * 100)
                skills["programming_languages"][lang_name] = {
                    "problems_solved": problems_solved,
                    "proficiency_score": proficiency_score,
                    "usage_percentage": (problems_solved / total_problems) * 100 if total_problems > 0 else 0,
                    "level": self._get_proficiency_level(proficiency_score)
                }
        
        # 分析算法技能
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        for stat in submit_stats:
            difficulty = stat.get("difficulty")
            count = stat.get("count", 0)
            submissions = stat.get("submissions", 0)
            
            if difficulty and count > 0:
                accuracy = (count / submissions) * 100 if submissions > 0 else 0
                weight = self.skill_weights["algorithm"].get(difficulty, 1.0)
                skill_score = min(100, count * weight * 0.8 + accuracy * 0.2)
                
                skills["algorithms"][f"{difficulty.lower()}_problems"] = {
                    "solved_count": count,
                    "total_submissions": submissions,
                    "accuracy_rate": accuracy,
                    "skill_score": skill_score,
                    "level": self._get_proficiency_level(skill_score)
                }
        
        # 分析数据结构掌握程度
        skills["data_structures"] = await self._analyze_data_structures(user_info)
        
        # 分析问题解决能力
        skills["problem_solving"] = await self._analyze_problem_solving_ability(user_info)
        
        # 生成整体评估
        skills["overall_assessment"] = await self._generate_overall_assessment(skills)
        
        return skills
    
    async def _analyze_data_structures(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据结构掌握程度"""
        data_structures = {}
        
        # 基于解题数量推断数据结构使用
        total_solved = sum(stat.get("count", 0) for stat in user_info.get("submitStats", {}).get("acSubmissionNum", []))
        
        if total_solved > 0:
            # 基础数据结构推断
            structure_thresholds = {
                "数组和字符串": {"min_problems": 10, "weight": 1.0},
                "链表": {"min_problems": 15, "weight": 1.2},
                "栈和队列": {"min_problems": 20, "weight": 1.3},
                "哈希表": {"min_problems": 25, "weight": 1.4},
                "树结构": {"min_problems": 30, "weight": 1.8},
                "图算法": {"min_problems": 40, "weight": 2.5},
                "堆和优先队列": {"min_problems": 35, "weight": 2.0},
                "字典树": {"min_problems": 45, "weight": 2.8}
            }
            
            for structure, config in structure_thresholds.items():
                if total_solved >= config["min_problems"]:
                    proficiency = min(100, (total_solved / config["min_problems"]) * config["weight"] * 20)
                    data_structures[structure] = {
                        "proficiency_score": proficiency,
                        "estimated_usage": min(100, total_solved * 0.1),
                        "level": self._get_proficiency_level(proficiency),
                        "confidence": "estimated"  # 标记为估算值
                    }
        
        return data_structures
    
    async def _analyze_problem_solving_ability(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析问题解决能力"""
        problem_solving = {}
        
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_stats = user_info.get("submitStats", {}).get("totalSubmissionNum", [])
        
        # 计算整体准确率
        total_accepted = sum(stat.get("count", 0) for stat in submit_stats)
        total_submissions = sum(stat.get("submissions", 0) for stat in total_stats)
        
        if total_submissions > 0:
            overall_accuracy = (total_accepted / total_submissions) * 100
            
            problem_solving["accuracy"] = {
                "rate": overall_accuracy,
                "level": self._get_accuracy_level(overall_accuracy),
                "total_accepted": total_accepted,
                "total_submissions": total_submissions
            }
        
        # 分析解题一致性
        consistency_score = self._calculate_consistency_score(submit_stats)
        problem_solving["consistency"] = {
            "score": consistency_score,
            "level": self._get_proficiency_level(consistency_score)
        }
        
        # 分析解题效率
        efficiency_score = self._calculate_efficiency_score(user_info)
        problem_solving["efficiency"] = {
            "score": efficiency_score,
            "level": self._get_proficiency_level(efficiency_score)
        }
        
        # 分析难度进阶能力
        progression_score = self._calculate_progression_score(submit_stats)
        problem_solving["progression"] = {
            "score": progression_score,
            "level": self._get_proficiency_level(progression_score)
        }
        
        return problem_solving
    
    async def _calculate_performance_metrics(self, user_info: Dict[str, Any], submission_stats: Any) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {}
        
        # 基础统计
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_solved = sum(stat.get("count", 0) for stat in submit_stats)
        
        metrics["basic_stats"] = {
            "total_problems_solved": total_solved,
            "easy_solved": next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Easy"), 0),
            "medium_solved": next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Medium"), 0),
            "hard_solved": next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Hard"), 0)
        }
        
        # 计算难度分布
        if total_solved > 0:
            easy_pct = (metrics["basic_stats"]["easy_solved"] / total_solved) * 100
            medium_pct = (metrics["basic_stats"]["medium_solved"] / total_solved) * 100
            hard_pct = (metrics["basic_stats"]["hard_solved"] / total_solved) * 100
            
            metrics["difficulty_distribution"] = {
                "easy_percentage": easy_pct,
                "medium_percentage": medium_pct,
                "hard_percentage": hard_pct,
                "balance_score": self._calculate_balance_score(easy_pct, medium_pct, hard_pct)
            }
        
        # 计算技能强度指数
        skill_intensity = self._calculate_skill_intensity(submit_stats)
        metrics["skill_intensity"] = {
            "score": skill_intensity,
            "level": self._get_proficiency_level(skill_intensity)
        }
        
        # 计算学习曲线
        learning_curve = self._calculate_learning_curve(user_info)
        metrics["learning_curve"] = learning_curve
        
        return metrics
    
    async def _generate_learning_recommendations(self, user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成学习建议"""
        recommendations = []
        
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_solved = sum(stat.get("count", 0) for stat in submit_stats)
        
        # 基于当前水平生成建议
        if total_solved < 50:
            recommendations.extend([
                {
                    "type": "foundation",
                    "priority": "high",
                    "title": "建立基础",
                    "description": "专注于数组、字符串和基础算法题目",
                    "suggested_topics": ["Array", "String", "Two Pointers", "Hash Table"],
                    "target_count": 50,
                    "estimated_time": "2-3周"
                },
                {
                    "type": "practice",
                    "priority": "medium",
                    "title": "每日练习",
                    "description": "建立每日刷题习惯，从简单题开始",
                    "suggested_schedule": "每天2-3题简单题",
                    "estimated_time": "持续进行"
                }
            ])
        
        elif total_solved < 200:
            recommendations.extend([
                {
                    "type": "intermediate",
                    "priority": "high",
                    "title": "中级算法",
                    "description": "学习动态规划、二分查找等中级算法",
                    "suggested_topics": ["Dynamic Programming", "Binary Search", "Backtracking"],
                    "target_count": 100,
                    "estimated_time": "1-2个月"
                },
                {
                    "type": "data_structure",
                    "priority": "medium",
                    "title": "数据结构强化",
                    "description": "深入学习树、图等复杂数据结构",
                    "suggested_topics": ["Tree", "Graph", "Heap"],
                    "estimated_time": "3-4周"
                }
            ])
        
        else:
            recommendations.extend([
                {
                    "type": "advanced",
                    "priority": "high",
                    "title": "高级算法",
                    "description": "挑战困难题目，学习高级算法技巧",
                    "suggested_topics": ["Advanced DP", "Graph Algorithms", "String Algorithms"],
                    "target_count": 50,
                    "estimated_time": "2-3个月"
                },
                {
                    "type": "contest",
                    "priority": "medium",
                    "title": "竞赛准备",
                    "description": "参加周赛，提升解题速度和准确率",
                    "suggested_schedule": "每周参加1-2次竞赛",
                    "estimated_time": "持续进行"
                }
            ])
        
        # 基于弱点生成针对性建议
        weak_areas = self._identify_weak_areas(submit_stats)
        for area in weak_areas:
            recommendations.append({
                "type": "improvement",
                "priority": "medium",
                "title": f"改进{area['name']}",
                "description": f"在{area['name']}方面需要加强练习",
                "suggested_topics": area["topics"],
                "target_improvement": f"提升{area['improvement_target']}%",
                "estimated_time": area["estimated_time"]
            })
        
        return recommendations
    
    async def _analyze_competitive_ranking(self, contest_info: Any) -> Dict[str, Any]:
        """分析竞赛排名"""
        if not contest_info or isinstance(contest_info, Exception):
            return {"status": "no_contest_data", "message": "无竞赛数据"}
        
        ranking_data = contest_info.get("userContestRanking", {})
        
        return {
            "current_rating": ranking_data.get("rating", 0),
            "global_ranking": ranking_data.get("globalRanking", 0),
            "contests_attended": ranking_data.get("attendedContestsCount", 0),
            "top_percentage": ranking_data.get("topPercentage", 0),
            "rating_trend": self._calculate_rating_trend(contest_info),
            "performance_level": self._get_contest_performance_level(ranking_data.get("rating", 0))
        }
    
    async def _analyze_problem_solving_patterns(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析解题模式"""
        patterns = {}
        
        # 分析解题时间分布
        patterns["time_distribution"] = self._analyze_time_patterns(user_info)
        
        # 分析解题策略
        patterns["solving_strategy"] = self._analyze_solving_strategy(user_info)
        
        # 分析错误模式
        patterns["error_patterns"] = self._analyze_error_patterns(user_info)
        
        # 分析学习路径
        patterns["learning_path"] = self._analyze_learning_path(user_info)
        
        return patterns
    
    # 辅助方法
    def _get_proficiency_level(self, score: float) -> str:
        """获取熟练度等级"""
        if score >= 90:
            return "专家"
        elif score >= 75:
            return "高级"
        elif score >= 60:
            return "中级"
        elif score >= 40:
            return "初级"
        else:
            return "入门"
    
    def _get_accuracy_level(self, accuracy: float) -> str:
        """获取准确率等级"""
        if accuracy >= 85:
            return "优秀"
        elif accuracy >= 70:
            return "良好"
        elif accuracy >= 55:
            return "中等"
        elif accuracy >= 40:
            return "需要改进"
        else:
            return "需要大幅改进"
    
    def _calculate_consistency_score(self, submit_stats: List[Dict[str, Any]]) -> float:
        """计算一致性分数"""
        if not submit_stats:
            return 0.0
        
        # 基于各难度题目的均衡性计算一致性
        difficulties = ["Easy", "Medium", "Hard"]
        counts = []
        
        for difficulty in difficulties:
            count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == difficulty), 0)
            counts.append(count)
        
        if sum(counts) == 0:
            return 0.0
        
        # 计算变异系数的倒数作为一致性指标
        mean_count = sum(counts) / len(counts)
        if mean_count == 0:
            return 0.0
        
        variance = sum((count - mean_count) ** 2 for count in counts) / len(counts)
        std_dev = variance ** 0.5
        cv = std_dev / mean_count if mean_count > 0 else 0
        
        # 转换为0-100的分数
        consistency_score = max(0, 100 - cv * 50)
        return min(100, consistency_score)
    
    def _calculate_efficiency_score(self, user_info: Dict[str, Any]) -> float:
        """计算效率分数"""
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_stats = user_info.get("submitStats", {}).get("totalSubmissionNum", [])
        
        if not submit_stats or not total_stats:
            return 0.0
        
        total_accepted = sum(stat.get("count", 0) for stat in submit_stats)
        total_submissions = sum(stat.get("submissions", 0) for stat in total_stats)
        
        if total_submissions == 0:
            return 0.0
        
        efficiency = (total_accepted / total_submissions) * 100
        return min(100, efficiency)
    
    def _calculate_progression_score(self, submit_stats: List[Dict[str, Any]]) -> float:
        """计算进阶能力分数"""
        if not submit_stats:
            return 0.0
        
        easy_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Easy"), 0)
        medium_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Medium"), 0)
        hard_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Hard"), 0)
        
        total_count = easy_count + medium_count + hard_count
        if total_count == 0:
            return 0.0
        
        # 基于难度分布计算进阶分数
        progression_score = (easy_count * 1 + medium_count * 3 + hard_count * 6) / total_count
        return min(100, progression_score * 10)
    
    def _calculate_balance_score(self, easy_pct: float, medium_pct: float, hard_pct: float) -> float:
        """计算难度平衡分数"""
        # 理想分布：30% Easy, 50% Medium, 20% Hard
        ideal_easy, ideal_medium, ideal_hard = 30, 50, 20
        
        deviation = (abs(easy_pct - ideal_easy) + 
                    abs(medium_pct - ideal_medium) + 
                    abs(hard_pct - ideal_hard)) / 3
        
        balance_score = max(0, 100 - deviation * 2)
        return balance_score
    
    def _calculate_skill_intensity(self, submit_stats: List[Dict[str, Any]]) -> float:
        """计算技能强度指数"""
        if not submit_stats:
            return 0.0
        
        total_weighted_score = 0
        for stat in submit_stats:
            difficulty = stat.get("difficulty")
            count = stat.get("count", 0)
            weight = self.skill_weights["algorithm"].get(difficulty, 1.0)
            total_weighted_score += count * weight
        
        # 归一化到0-100范围
        intensity = min(100, total_weighted_score / 10)
        return intensity
    
    def _calculate_learning_curve(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """计算学习曲线"""
        # 这里可以根据用户的提交历史分析学习曲线
        # 由于API限制，这里提供一个简化的实现
        
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_solved = sum(stat.get("count", 0) for stat in submit_stats)
        
        # 估算学习阶段
        if total_solved < 30:
            stage = "初学者"
            progress = (total_solved / 30) * 100
        elif total_solved < 100:
            stage = "进阶者"
            progress = ((total_solved - 30) / 70) * 100
        elif total_solved < 300:
            stage = "中级者"
            progress = ((total_solved - 100) / 200) * 100
        else:
            stage = "高级者"
            progress = min(100, ((total_solved - 300) / 500) * 100)
        
        return {
            "current_stage": stage,
            "stage_progress": progress,
            "total_problems": total_solved,
            "estimated_level": self._get_proficiency_level(progress)
        }
    
    def _identify_weak_areas(self, submit_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别薄弱环节"""
        weak_areas = []
        
        # 分析难度分布
        easy_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Easy"), 0)
        medium_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Medium"), 0)
        hard_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Hard"), 0)
        
        total_count = easy_count + medium_count + hard_count
        
        if total_count > 0:
            # 检查中等难度题目比例
            medium_pct = (medium_count / total_count) * 100
            if medium_pct < 40:  # 中等题目比例过低
                weak_areas.append({
                    "name": "中等难度算法",
                    "topics": ["Dynamic Programming", "Binary Search", "Two Pointers"],
                    "improvement_target": "30",
                    "estimated_time": "4-6周"
                })
            
            # 检查困难题目比例
            hard_pct = (hard_count / total_count) * 100
            if hard_pct < 10 and total_count > 100:  # 困难题目比例过低
                weak_areas.append({
                    "name": "高难度算法",
                    "topics": ["Advanced DP", "Graph Algorithms", "Tree Algorithms"],
                    "improvement_target": "20",
                    "estimated_time": "6-8周"
                })
        
        return weak_areas
    
    def _calculate_rating_trend(self, contest_info: Dict[str, Any]) -> str:
        """计算评分趋势"""
        # 这里可以根据历史竞赛数据计算趋势
        # 由于API限制，这里提供一个简化的实现
        current_rating = contest_info.get("userContestRanking", {}).get("rating", 0)
        
        if current_rating > 1800:
            return "稳定上升"
        elif current_rating > 1500:
            return "缓慢上升"
        elif current_rating > 1200:
            return "波动中"
        else:
            return "需要提升"
    
    def _get_contest_performance_level(self, rating: int) -> str:
        """获取竞赛表现等级"""
        if rating >= 2100:
            return "专家级"
        elif rating >= 1800:
            return "高级"
        elif rating >= 1500:
            return "中级"
        elif rating >= 1200:
            return "初级"
        else:
            return "入门"
    
    def _analyze_time_patterns(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析时间模式"""
        # 简化实现，实际应该基于提交时间戳
        return {
            "preferred_time": "估算中",
            "solving_speed": "中等",
            "consistency": "需要更多数据"
        }
    
    def _analyze_solving_strategy(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析解题策略"""
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_solved = sum(stat.get("count", 0) for stat in submit_stats)
        
        if total_solved < 50:
            strategy = "基础建设型"
        elif total_solved < 200:
            strategy = "稳步推进型"
        else:
            strategy = "全面发展型"
        
        return {
            "type": strategy,
            "characteristics": self._get_strategy_characteristics(strategy)
        }
    
    def _analyze_error_patterns(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析错误模式"""
        # 基于提交统计分析错误模式
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_stats = user_info.get("submitStats", {}).get("totalSubmissionNum", [])
        
        patterns = {}
        
        for difficulty in ["Easy", "Medium", "Hard"]:
            accepted = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == difficulty), 0)
            total = next((stat.get("submissions", 0) for stat in total_stats if stat.get("difficulty") == difficulty), 0)
            
            if total > 0:
                error_rate = ((total - accepted) / total) * 100
                patterns[difficulty.lower()] = {
                    "error_rate": error_rate,
                    "level": self._get_error_level(error_rate)
                }
        
        return patterns
    
    def _analyze_learning_path(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """分析学习路径"""
        submit_stats = user_info.get("submitStats", {}).get("acSubmissionNum", [])
        total_solved = sum(stat.get("count", 0) for stat in submit_stats)
        
        path_analysis = {
            "current_phase": self._determine_learning_phase(total_solved),
            "next_milestone": self._get_next_milestone(total_solved),
            "recommended_focus": self._get_recommended_focus(submit_stats)
        }
        
        return path_analysis
    
    def _get_strategy_characteristics(self, strategy: str) -> List[str]:
        """获取策略特征"""
        characteristics_map = {
            "基础建设型": ["注重基础", "循序渐进", "稳扎稳打"],
            "稳步推进型": ["均衡发展", "持续进步", "目标明确"],
            "全面发展型": ["广度优先", "挑战困难", "追求卓越"]
        }
        return characteristics_map.get(strategy, ["需要更多数据"])
    
    def _get_error_level(self, error_rate: float) -> str:
        """获取错误等级"""
        if error_rate <= 20:
            return "优秀"
        elif error_rate <= 40:
            return "良好"
        elif error_rate <= 60:
            return "中等"
        else:
            return "需要改进"
    
    def _determine_learning_phase(self, total_solved: int) -> str:
        """确定学习阶段"""
        if total_solved < 50:
            return "基础学习"
        elif total_solved < 200:
            return "技能提升"
        elif total_solved < 500:
            return "深度练习"
        else:
            return "专业精进"
    
    def _get_next_milestone(self, total_solved: int) -> Dict[str, Any]:
        """获取下一个里程碑"""
        milestones = [50, 100, 200, 300, 500, 1000]
        
        for milestone in milestones:
            if total_solved < milestone:
                return {
                    "target": milestone,
                    "remaining": milestone - total_solved,
                    "progress": (total_solved / milestone) * 100,
                    "estimated_time": f"{(milestone - total_solved) // 10 + 1}周"
                }
        
        return {
            "target": "继续挑战",
            "remaining": 0,
            "progress": 100,
            "estimated_time": "持续进行"
        }
    
    def _get_recommended_focus(self, submit_stats: List[Dict[str, Any]]) -> List[str]:
        """获取推荐关注点"""
        easy_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Easy"), 0)
        medium_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Medium"), 0)
        hard_count = next((stat.get("count", 0) for stat in submit_stats if stat.get("difficulty") == "Hard"), 0)
        
        total_count = easy_count + medium_count + hard_count
        focus_areas = []
        
        if total_count == 0:
            focus_areas = ["开始刷题", "建立基础"]
        elif easy_count / total_count > 0.7:
            focus_areas = ["中等难度题目", "算法深度学习"]
        elif medium_count / total_count > 0.6:
            focus_areas = ["困难题目", "高级算法"]
        else:
            focus_areas = ["全面发展", "竞赛准备"]
        
        return focus_areas
    
    async def _generate_overall_assessment(self, skills: Dict[str, Any]) -> Dict[str, Any]:
        """生成整体评估"""
        # 计算综合分数
        lang_scores = [lang_data.get("proficiency_score", 0) for lang_data in skills.get("programming_languages", {}).values()]
        algo_scores = [algo_data.get("skill_score", 0) for algo_data in skills.get("algorithms", {}).values()]
        
        avg_lang_score = sum(lang_scores) / len(lang_scores) if lang_scores else 0
        avg_algo_score = sum(algo_scores) / len(algo_scores) if algo_scores else 0
        
        overall_score = (avg_lang_score * 0.3 + avg_algo_score * 0.7)
        
        return {
            "overall_score": overall_score,
            "level": self._get_proficiency_level(overall_score),
            "strengths": self._identify_strengths(skills),
            "areas_for_improvement": self._identify_improvements(skills),
            "next_steps": self._suggest_next_steps(overall_score)
        }
    
    def _identify_strengths(self, skills: Dict[str, Any]) -> List[str]:
        """识别优势"""
        strengths = []
        
        # 分析编程语言优势
        for lang, data in skills.get("programming_languages", {}).items():
            if data.get("proficiency_score", 0) > 70:
                strengths.append(f"{lang}编程")
        
        # 分析算法优势
        for algo, data in skills.get("algorithms", {}).items():
            if data.get("skill_score", 0) > 75:
                strengths.append(f"{algo.replace('_', ' ').title()}")
        
        if not strengths:
            strengths = ["基础扎实", "学习态度积极"]
        
        return strengths
    
    def _identify_improvements(self, skills: Dict[str, Any]) -> List[str]:
        """识别改进点"""
        improvements = []
        
        # 分析需要改进的领域
        for algo, data in skills.get("algorithms", {}).items():
            if data.get("skill_score", 0) < 50:
                improvements.append(f"{algo.replace('_', ' ').title()}")
        
        problem_solving = skills.get("problem_solving", {})
        if problem_solving.get("accuracy", {}).get("rate", 0) < 70:
            improvements.append("解题准确率")
        
        if not improvements:
            improvements = ["继续保持", "挑战更高难度"]
        
        return improvements
    
    def _suggest_next_steps(self, overall_score: float) -> List[str]:
        """建议下一步"""
        if overall_score < 40:
            return ["加强基础练习", "每日坚持刷题", "学习基本算法"]
        elif overall_score < 70:
            return ["提升解题效率", "学习中级算法", "参加编程竞赛"]
        else:
            return ["挑战困难题目", "深入学习高级算法", "准备技术面试"]
    
    # 保持原有的方法
    async def analyze_user_skills(self, username_or_url: str) -> List[Dict[str, Any]]:
        """分析LeetCode用户的技能 - 兼容性方法"""
        try:
            analysis_result = await self.get_comprehensive_analysis(username_or_url)
            
            # 转换为原有格式
            skills = []
            
            # 添加编程语言技能
            for lang, data in analysis_result.skill_analysis.get("programming_languages", {}).items():
                skills.append({
                    "skill_name": f"{lang}编程",
                    "category": "programming_language",
                    "proficiency": data.get("proficiency_score", 0),
                    "source": "leetcode",
                    "evidence": {
                        "problems_solved": data.get("problems_solved", 0),
                        "usage_percentage": data.get("usage_percentage", 0)
                    }
                })
            
            # 添加算法技能
            for algo, data in analysis_result.skill_analysis.get("algorithms", {}).items():
                skills.append({
                    "skill_name": algo.replace("_", " ").title(),
                    "category": "algorithm",
                    "proficiency": data.get("skill_score", 0),
                    "source": "leetcode",
                    "evidence": {
                        "solved_count": data.get("solved_count", 0),
                        "accuracy_rate": data.get("accuracy_rate", 0)
                    }
                })
            
            return skills
            
        except Exception as e:
            logger.error(f"LeetCode技能分析失败: {str(e)}")
            return []
    
    async def _get_user_info(self, username: str) -> Dict[str, Any]:
        """获取用户信息 - 增强版"""
        query = """
        query userPublicProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    realName
                    avatar
                    location
                    company
                    school
                    website
                    github
                    linkedin
                    twitter
                    aboutMe
                    skillTags
                    ranking
                    reputation
                    createdAt
                    lastModified
                }
                contributions {
                    points
                }
                badges {
                    id
                    displayName
                    icon
                    creationDate
                }
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                    totalSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
                languageProblemCount {
                    languageName
                    problemsSolved
                }
            }
        }
        """
        
        variables = {"username": username}
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={"query": query, "variables": variables}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        matched_user = data.get("data", {}).get("matchedUser")
                        
                        if not matched_user:
                            error_msg = f"LeetCode用户'{username}'不存在"
                            if data.get("errors"):
                                error_msg += f" (错误: {data['errors'][0]['message']})"
                            raise LeetCodeServiceException(error_msg, "USER_NOT_FOUND")
                        
                        return matched_user
                    else:
                        error_text = await response.text()
                        raise LeetCodeServiceException(
                            f"LeetCode API请求失败: {response.status}",
                            "API_ERROR",
                            {"status": response.status, "response": error_text}
                        )
        except aiohttp.ClientError as e:
            raise LeetCodeServiceException(
                f"网络请求失败: {str(e)}",
                "NETWORK_ERROR"
            )
        except asyncio.TimeoutError:
            raise LeetCodeServiceException(
                "请求超时，请稍后重试",
                "TIMEOUT_ERROR"
            )
    
    async def _get_contest_info(self, username: str) -> Dict[str, Any]:
        """获取竞赛信息"""
        query = """
        query userContestRanking($username: String!) {
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                topPercentage
                badge {
                    name
                }
            }
        }
        """
        
        variables = {"username": username}
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.graphql_url,
                    headers=self.headers,
                    json={"query": query, "variables": variables}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {})
                    else:
                        return {}
        except:
            return {}
    
    async def _get_submission_statistics(self, username: str) -> Dict[str, Any]:
        """获取提交统计"""
        # 这里可以添加更详细的提交统计查询
        # 目前返回空字典，因为基本信息已经在_get_user_info中获取
        return {}
    
    def _extract_username_from_url(self, url: str) -> str:
        """从URL中提取用户名 - 增强版"""
        if not url:
            return ""
        
        # 如果不是URL，直接返回
        if not url.startswith(('http://', 'https://')):
            # 验证用户名格式
            if re.match(r'^[a-zA-Z0-9_-]+$', url):
                return url
            return ""
        
        # 支持多种URL格式
        patterns = [
            r'leetcode\.(?:com|cn)/(?:u|profile)/([a-zA-Z0-9_-]+)',
            r'leetcode\.(?:com|cn)/([a-zA-Z0-9_-]+)(?:/)?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
