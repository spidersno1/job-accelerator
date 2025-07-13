"""
LeetCode分析模块

分析用户LeetCode账号，提取算法能力、解题统计、难度分布等数据
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class LeetCodeProblem:
    """LeetCode题目信息"""
    id: int
    title: str
    difficulty: str
    category: str
    status: str  # "accepted", "attempted", "not_started"
    submission_date: Optional[datetime] = None
    runtime: Optional[int] = None
    memory: Optional[int] = None


@dataclass
class LeetCodeProfile:
    """LeetCode用户档案信息"""
    username: str
    ranking: int
    rating: int
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    acceptance_rate: float
    total_submissions: int
    total_questions: int


class LeetCodeAnalyzer:
    """LeetCode账号分析器"""
    
    def __init__(self):
        self.base_url = "https://leetcode.com/graphql"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def get_user_profile(self, username: str) -> Optional[LeetCodeProfile]:
        """获取用户档案信息"""
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    ranking
                    realName
                    aboutMe
                    location
                    websites
                    skillTags
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
            }
        }
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query,
                    "variables": {"username": username}
                }
                
                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_data = data.get("data", {}).get("matchedUser")
                        
                        if user_data:
                            submit_stats = user_data.get("submitStats", {})
                            ac_submissions = {item["difficulty"]: item for item in submit_stats.get("acSubmissionNum", [])}
                            total_submissions = {item["difficulty"]: item for item in submit_stats.get("totalSubmissionNum", [])}
                            
                            return LeetCodeProfile(
                                username=user_data["username"],
                                ranking=user_data.get("profile", {}).get("ranking", 0),
                                rating=0,  # 需要额外查询
                                total_solved=ac_submissions.get("All", {}).get("count", 0),
                                easy_solved=ac_submissions.get("Easy", {}).get("count", 0),
                                medium_solved=ac_submissions.get("Medium", {}).get("count", 0),
                                hard_solved=ac_submissions.get("Hard", {}).get("count", 0),
                                acceptance_rate=self._calculate_acceptance_rate(ac_submissions, total_submissions),
                                total_submissions=total_submissions.get("All", {}).get("submissions", 0),
                                total_questions=total_submissions.get("All", {}).get("count", 0)
                            )
                    else:
                        logger.error(f"获取LeetCode档案失败: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"获取LeetCode档案异常: {e}")
            return None
    
    def _calculate_acceptance_rate(self, ac_submissions: Dict, total_submissions: Dict) -> float:
        """计算接受率"""
        total_ac = ac_submissions.get("All", {}).get("submissions", 0)
        total_sub = total_submissions.get("All", {}).get("submissions", 0)
        
        if total_sub == 0:
            return 0.0
        
        return round(total_ac / total_sub * 100, 2)
    
    async def get_user_submissions(self, username: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取用户提交记录"""
        query = """
        query getUserSubmissions($username: String!, $limit: Int!) {
            recentSubmissionList(username: $username, limit: $limit) {
                id
                title
                titleSlug
                status
                timestamp
                lang
                runtime
                memory
            }
        }
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query,
                    "variables": {"username": username, "limit": limit}
                }
                
                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("recentSubmissionList", [])
                    else:
                        logger.error(f"获取提交记录失败: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"获取提交记录异常: {e}")
            return []
    
    async def get_problem_details(self, title_slug: str) -> Optional[Dict[str, Any]]:
        """获取题目详细信息"""
        query = """
        query getProblemDetails($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                title
                titleSlug
                difficulty
                categoryTitle
                topicTags {
                    name
                    slug
                }
                stats
            }
        }
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "query": query,
                    "variables": {"titleSlug": title_slug}
                }
                
                async with session.post(self.base_url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("question")
                    else:
                        logger.error(f"获取题目详情失败: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"获取题目详情异常: {e}")
            return None
    
    def analyze_algorithm_skills(self, profile: LeetCodeProfile, submissions: List[Dict]) -> Dict[str, Any]:
        """分析算法技能"""
        # 按难度分析
        difficulty_analysis = {
            "easy": {
                "solved": profile.easy_solved,
                "percentage": round(profile.easy_solved / max(profile.total_solved, 1) * 100, 2)
            },
            "medium": {
                "solved": profile.medium_solved,
                "percentage": round(profile.medium_solved / max(profile.total_solved, 1) * 100, 2)
            },
            "hard": {
                "solved": profile.hard_solved,
                "percentage": round(profile.hard_solved / max(profile.total_solved, 1) * 100, 2)
            }
        }
        
        # 分析编程语言使用
        language_stats = {}
        for submission in submissions:
            lang = submission.get("lang", "Unknown")
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        # 计算技能评分
        skill_score = 0
        if profile.total_solved > 0:
            # 基础分数
            skill_score += profile.total_solved * 10
            # 难度加权
            skill_score += profile.easy_solved * 5
            skill_score += profile.medium_solved * 15
            skill_score += profile.hard_solved * 30
            # 接受率加权
            skill_score += profile.acceptance_rate * 2
        
        return {
            "difficulty_distribution": difficulty_analysis,
            "languages": language_stats,
            "skill_score": skill_score,
            "acceptance_rate": profile.acceptance_rate,
            "ranking_percentage": self._calculate_ranking_percentage(profile.ranking)
        }
    
    def _calculate_ranking_percentage(self, ranking: int) -> float:
        """计算排名百分比（估算）"""
        # 假设LeetCode总用户数约为500万
        total_users = 5000000
        if ranking == 0:
            return 0.0
        return round((total_users - ranking) / total_users * 100, 2)
    
    def analyze_learning_progress(self, profile: LeetCodeProfile) -> Dict[str, Any]:
        """分析学习进度"""
        # 计算完成度
        completion_rate = round(profile.total_solved / max(profile.total_questions, 1) * 100, 2)
        
        # 评估水平
        level = "初级"
        if profile.total_solved >= 100:
            level = "中级"
        if profile.total_solved >= 300:
            level = "高级"
        if profile.total_solved >= 500:
            level = "专家"
        
        # 建议下一步
        suggestions = []
        if profile.easy_solved < 50:
            suggestions.append("建议多练习简单题目，打好基础")
        if profile.medium_solved < 100:
            suggestions.append("可以开始挑战中等难度题目")
        if profile.hard_solved < 20:
            suggestions.append("尝试一些困难题目，提升算法思维")
        
        return {
            "completion_rate": completion_rate,
            "level": level,
            "suggestions": suggestions,
            "next_milestone": self._get_next_milestone(profile.total_solved)
        }
    
    def _get_next_milestone(self, solved: int) -> Dict[str, Any]:
        """获取下一个里程碑"""
        milestones = [50, 100, 200, 300, 500, 1000]
        for milestone in milestones:
            if solved < milestone:
                return {
                    "target": milestone,
                    "remaining": milestone - solved,
                    "description": f"距离{milestone}题还有{milestone - solved}题"
                }
        return {"target": "已达成所有里程碑", "remaining": 0, "description": "恭喜！"}
    
    async def analyze_leetcode_account(self, username: str) -> Dict[str, Any]:
        """完整分析LeetCode账号"""
        logger.info(f"开始分析LeetCode账号: {username}")
        
        # 获取用户档案
        profile = await self.get_user_profile(username)
        if not profile:
            return {"error": "无法获取用户档案"}
        
        # 获取提交记录
        submissions = await self.get_user_submissions(username)
        
        # 分析算法技能
        skills_analysis = self.analyze_algorithm_skills(profile, submissions)
        
        # 分析学习进度
        progress_analysis = self.analyze_learning_progress(profile)
        
        return {
            "profile": profile,
            "recent_submissions": submissions[:10],  # 最近10次提交
            "skills": skills_analysis,
            "progress": progress_analysis,
            "summary": {
                "total_solved": profile.total_solved,
                "acceptance_rate": profile.acceptance_rate,
                "skill_score": skills_analysis["skill_score"],
                "level": progress_analysis["level"],
                "ranking": profile.ranking
            }
        } 