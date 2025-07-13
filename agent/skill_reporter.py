"""
技能报告模块

整合GitHub和LeetCode分析结果，生成综合技能报告
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class SkillCategory:
    """技能分类"""
    name: str
    level: str  # "初级", "中级", "高级", "专家"
    score: float
    description: str
    evidence: List[str]
    recommendations: List[str]


@dataclass
class SkillReport:
    """技能报告"""
    user_id: str
    generated_at: datetime
    overall_score: float
    skill_categories: List[SkillCategory]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    market_position: str
    summary: Dict[str, Any]


class SkillReporter:
    """技能报告生成器"""
    
    def __init__(self):
        self.skill_weights = {
            "programming_languages": 0.25,
            "algorithm_skills": 0.20,
            "project_experience": 0.20,
            "problem_solving": 0.15,
            "code_quality": 0.10,
            "learning_ability": 0.10
        }
        
        self.language_levels = {
            "Python": {"beginner": 0, "intermediate": 50, "advanced": 200, "expert": 500},
            "JavaScript": {"beginner": 0, "intermediate": 30, "advanced": 150, "expert": 400},
            "Java": {"beginner": 0, "intermediate": 40, "advanced": 180, "expert": 450},
            "C++": {"beginner": 0, "intermediate": 20, "advanced": 100, "expert": 300},
            "Go": {"beginner": 0, "intermediate": 10, "advanced": 50, "expert": 150},
            "Rust": {"beginner": 0, "intermediate": 5, "advanced": 30, "expert": 100}
        }
    
    def generate_skill_report(self, 
                            user_id: str,
                            github_data: Dict[str, Any],
                            leetcode_data: Dict[str, Any]) -> SkillReport:
        """生成综合技能报告"""
        logger.info(f"开始生成技能报告: {user_id}")
        
        # 分析各个技能类别
        programming_languages = self._analyze_programming_languages(github_data, leetcode_data)
        algorithm_skills = self._analyze_algorithm_skills(leetcode_data)
        project_experience = self._analyze_project_experience(github_data)
        problem_solving = self._analyze_problem_solving(leetcode_data)
        code_quality = self._analyze_code_quality(github_data)
        learning_ability = self._analyze_learning_ability(github_data, leetcode_data)
        
        skill_categories = [
            programming_languages,
            algorithm_skills,
            project_experience,
            problem_solving,
            code_quality,
            learning_ability
        ]
        
        # 计算总体评分
        overall_score = self._calculate_overall_score(skill_categories)
        
        # 识别优势和劣势
        strengths, weaknesses = self._identify_strengths_weaknesses(skill_categories)
        
        # 生成建议
        recommendations = self._generate_recommendations(skill_categories, strengths, weaknesses)
        
        # 市场定位
        market_position = self._determine_market_position(overall_score, skill_categories)
        
        # 生成摘要
        summary = self._generate_summary(skill_categories, overall_score, market_position)
        
        return SkillReport(
            user_id=user_id,
            generated_at=datetime.now(),
            overall_score=overall_score,
            skill_categories=skill_categories,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            market_position=market_position,
            summary=summary
        )
    
    def _analyze_programming_languages(self, github_data: Dict, leetcode_data: Dict) -> SkillCategory:
        """分析编程语言技能"""
        languages = {}
        
        # 从GitHub数据提取语言信息
        if "skills" in github_data and "languages" in github_data["skills"]:
            for lang, info in github_data["skills"]["languages"].items():
                languages[lang] = {
                    "count": info["count"],
                    "weight": info["weight"],
                    "source": "github"
                }
        
        # 从LeetCode数据提取语言信息
        if "skills" in leetcode_data and "languages" in leetcode_data["skills"]:
            for lang, count in leetcode_data["skills"]["languages"].items():
                if lang in languages:
                    languages[lang]["leetcode_count"] = count
                else:
                    languages[lang] = {
                        "count": 0,
                        "weight": 0,
                        "leetcode_count": count,
                        "source": "leetcode"
                    }
        
        # 计算语言技能评分
        total_score = 0
        evidence = []
        recommendations = []
        
        for lang, info in languages.items():
            # 计算该语言的评分
            github_score = info.get("count", 0) * 10
            leetcode_score = info.get("leetcode_count", 0) * 5
            lang_score = github_score + leetcode_score
            
            # 确定语言水平
            level_thresholds = self.language_levels.get(lang, {"beginner": 0, "intermediate": 50, "advanced": 200, "expert": 500})
            
            if lang_score >= level_thresholds["expert"]:
                level = "专家"
            elif lang_score >= level_thresholds["advanced"]:
                level = "高级"
            elif lang_score >= level_thresholds["intermediate"]:
                level = "中级"
            else:
                level = "初级"
            
            total_score += lang_score
            evidence.append(f"{lang}: {level}水平 (GitHub: {info.get('count', 0)}个项目, LeetCode: {info.get('leetcode_count', 0)}题)")
            
            if level == "初级":
                recommendations.append(f"建议加强{lang}编程技能，多写项目和多刷题")
        
        # 确定整体语言水平
        if total_score >= 1000:
            overall_level = "专家"
        elif total_score >= 500:
            overall_level = "高级"
        elif total_score >= 200:
            overall_level = "中级"
        else:
            overall_level = "初级"
        
        return SkillCategory(
            name="编程语言",
            level=overall_level,
            score=total_score,
            description=f"掌握{len(languages)}种编程语言，总体水平{overall_level}",
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _analyze_algorithm_skills(self, leetcode_data: Dict) -> SkillCategory:
        """分析算法技能"""
        if "profile" not in leetcode_data:
            return SkillCategory(
                name="算法技能",
                level="初级",
                score=0,
                description="暂无LeetCode数据",
                evidence=[],
                recommendations=["建议注册LeetCode账号并开始刷题"]
            )
        
        profile = leetcode_data["profile"]
        skills = leetcode_data.get("skills", {})
        
        # 计算算法技能评分
        score = skills.get("skill_score", 0)
        acceptance_rate = skills.get("acceptance_rate", 0)
        ranking_percentage = skills.get("ranking_percentage", 0)
        
        # 确定水平
        if score >= 5000:
            level = "专家"
        elif score >= 2000:
            level = "高级"
        elif score >= 500:
            level = "中级"
        else:
            level = "初级"
        
        evidence = [
            f"已解决{profile.total_solved}道题目",
            f"接受率: {acceptance_rate}%",
            f"排名前{ranking_percentage}%",
            f"简单题: {profile.easy_solved}, 中等题: {profile.medium_solved}, 困难题: {profile.hard_solved}"
        ]
        
        recommendations = []
        if profile.total_solved < 100:
            recommendations.append("建议多刷题，至少完成100道题目")
        if acceptance_rate < 80:
            recommendations.append("建议提高解题质量，提升接受率")
        if profile.hard_solved < 10:
            recommendations.append("建议挑战更多困难题目")
        
        return SkillCategory(
            name="算法技能",
            level=level,
            score=score,
            description=f"算法解题能力{level}，已解决{profile.total_solved}道题目",
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _analyze_project_experience(self, github_data: Dict) -> SkillCategory:
        """分析项目经验"""
        if "repos" not in github_data:
            return SkillCategory(
                name="项目经验",
                level="初级",
                score=0,
                description="暂无GitHub项目数据",
                evidence=[],
                recommendations=["建议在GitHub上创建项目展示技能"]
            )
        
        repos = github_data["repos"]
        total_repos = len(repos)
        total_stars = sum(repo.stars for repo in repos)
        total_forks = sum(repo.forks for repo in repos)
        
        # 计算项目经验评分
        score = total_repos * 50 + total_stars * 10 + total_forks * 5
        
        # 确定水平
        if score >= 2000:
            level = "专家"
        elif score >= 800:
            level = "高级"
        elif score >= 300:
            level = "中级"
        else:
            level = "初级"
        
        evidence = [
            f"总项目数: {total_repos}",
            f"总星标数: {total_stars}",
            f"总分叉数: {total_forks}",
            f"平均星标: {total_stars / total_repos if total_repos > 0 else 0:.1f}"
        ]
        
        recommendations = []
        if total_repos < 5:
            recommendations.append("建议创建更多项目展示技能")
        if total_stars < 50:
            recommendations.append("建议提升项目质量，获得更多星标")
        
        return SkillCategory(
            name="项目经验",
            level=level,
            score=score,
            description=f"项目经验{level}，拥有{total_repos}个GitHub项目",
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _analyze_problem_solving(self, leetcode_data: Dict) -> SkillCategory:
        """分析问题解决能力"""
        if "profile" not in leetcode_data:
            return SkillCategory(
                name="问题解决",
                level="初级",
                score=0,
                description="暂无解题数据",
                evidence=[],
                recommendations=["建议开始刷题训练问题解决能力"]
            )
        
        profile = leetcode_data["profile"]
        skills = leetcode_data.get("skills", {})
        
        # 计算问题解决能力评分
        score = profile.total_solved * 20 + skills.get("acceptance_rate", 0) * 2
        
        # 确定水平
        if score >= 3000:
            level = "专家"
        elif score >= 1500:
            level = "高级"
        elif score >= 500:
            level = "中级"
        else:
            level = "初级"
        
        evidence = [
            f"解题总数: {profile.total_solved}",
            f"接受率: {skills.get('acceptance_rate', 0)}%",
            f"困难题解决数: {profile.hard_solved}"
        ]
        
        recommendations = []
        if profile.hard_solved < 20:
            recommendations.append("建议多解决困难题目，提升问题解决能力")
        
        return SkillCategory(
            name="问题解决",
            level=level,
            score=score,
            description=f"问题解决能力{level}，解题接受率{skills.get('acceptance_rate', 0)}%",
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _analyze_code_quality(self, github_data: Dict) -> SkillCategory:
        """分析代码质量"""
        if "repos" not in github_data:
            return SkillCategory(
                name="代码质量",
                level="初级",
                score=0,
                description="暂无代码质量数据",
                evidence=[],
                recommendations=["建议创建高质量项目展示代码能力"]
            )
        
        repos = github_data["repos"]
        
        # 计算代码质量评分（基于项目质量指标）
        total_stars = sum(repo.stars for repo in repos)
        total_forks = sum(repo.forks for repo in repos)
        avg_stars = total_stars / len(repos) if repos else 0
        
        score = avg_stars * 100 + total_forks * 10
        
        # 确定水平
        if score >= 1000:
            level = "专家"
        elif score >= 400:
            level = "高级"
        elif score >= 150:
            level = "中级"
        else:
            level = "初级"
        
        evidence = [
            f"平均星标: {avg_stars:.1f}",
            f"总分叉: {total_forks}",
            f"项目数: {len(repos)}"
        ]
        
        recommendations = []
        if avg_stars < 5:
            recommendations.append("建议提升代码质量，编写更优秀的项目")
        
        return SkillCategory(
            name="代码质量",
            level=level,
            score=score,
            description=f"代码质量{level}，项目平均星标{avg_stars:.1f}",
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _analyze_learning_ability(self, github_data: Dict, leetcode_data: Dict) -> SkillCategory:
        """分析学习能力"""
        # 基于活跃度和进步速度评估学习能力
        github_activity = github_data.get("activity", {})
        leetcode_progress = leetcode_data.get("progress", {})
        
        activity_score = github_activity.get("activity_score", 0)
        completion_rate = leetcode_progress.get("completion_rate", 0)
        
        score = activity_score * 10 + completion_rate * 5
        
        # 确定水平
        if score >= 500:
            level = "专家"
        elif score >= 200:
            level = "高级"
        elif score >= 100:
            level = "中级"
        else:
            level = "初级"
        
        evidence = [
            f"GitHub活跃度评分: {activity_score:.1f}",
            f"LeetCode完成率: {completion_rate}%"
        ]
        
        recommendations = []
        if activity_score < 10:
            recommendations.append("建议提高GitHub活跃度，多参与开源项目")
        if completion_rate < 20:
            recommendations.append("建议提高LeetCode刷题频率")
        
        return SkillCategory(
            name="学习能力",
            level=level,
            score=score,
            description=f"学习能力{level}，持续学习和进步能力强",
            evidence=evidence,
            recommendations=recommendations
        )
    
    def _calculate_overall_score(self, skill_categories: List[SkillCategory]) -> float:
        """计算总体评分"""
        total_score = 0
        total_weight = 0
        
        for category in skill_categories:
            weight = self.skill_weights.get(category.name.lower().replace(" ", "_"), 0.1)
            total_score += category.score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _identify_strengths_weaknesses(self, skill_categories: List[SkillCategory]) -> tuple[List[str], List[str]]:
        """识别优势和劣势"""
        strengths = []
        weaknesses = []
        
        for category in skill_categories:
            if category.level in ["高级", "专家"]:
                strengths.append(f"{category.name}: {category.level}")
            elif category.level == "初级":
                weaknesses.append(f"{category.name}: 需要提升")
        
        return strengths, weaknesses
    
    def _generate_recommendations(self, skill_categories: List[SkillCategory], 
                                strengths: List[str], weaknesses: List[str]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 添加各技能类别的建议
        for category in skill_categories:
            recommendations.extend(category.recommendations)
        
        # 基于整体情况添加建议
        if len(strengths) >= 3:
            recommendations.append("技能组合良好，建议专注提升特定领域的深度")
        elif len(weaknesses) >= 3:
            recommendations.append("建议制定系统性学习计划，全面提升技能")
        
        return list(set(recommendations))  # 去重
    
    def _determine_market_position(self, overall_score: float, skill_categories: List[SkillCategory]) -> str:
        """确定市场定位"""
        if overall_score >= 2000:
            return "高级开发工程师"
        elif overall_score >= 1000:
            return "中级开发工程师"
        elif overall_score >= 500:
            return "初级开发工程师"
        else:
            return "入门级开发者"
    
    def _generate_summary(self, skill_categories: List[SkillCategory], 
                         overall_score: float, market_position: str) -> Dict[str, Any]:
        """生成摘要"""
        return {
            "overall_score": overall_score,
            "market_position": market_position,
            "skill_count": len(skill_categories),
            "expert_skills": len([c for c in skill_categories if c.level == "专家"]),
            "advanced_skills": len([c for c in skill_categories if c.level == "高级"]),
            "intermediate_skills": len([c for c in skill_categories if c.level == "中级"]),
            "beginner_skills": len([c for c in skill_categories if c.level == "初级"]),
            "top_skills": sorted(skill_categories, key=lambda x: x.score, reverse=True)[:3]
        }
    
    def export_report(self, report: SkillReport, format: str = "json") -> str:
        """导出报告"""
        if format == "json":
            return json.dumps({
                "user_id": report.user_id,
                "generated_at": report.generated_at.isoformat(),
                "overall_score": report.overall_score,
                "market_position": report.market_position,
                "skill_categories": [
                    {
                        "name": cat.name,
                        "level": cat.level,
                        "score": cat.score,
                        "description": cat.description,
                        "evidence": cat.evidence,
                        "recommendations": cat.recommendations
                    }
                    for cat in report.skill_categories
                ],
                "strengths": report.strengths,
                "weaknesses": report.weaknesses,
                "recommendations": report.recommendations,
                "summary": report.summary
            }, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}") 