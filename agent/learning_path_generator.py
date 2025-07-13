"""
学习路径生成模块

基于技能报告和招聘需求，生成定制化学习路径
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class LearningTask:
    """学习任务"""
    id: str
    title: str
    description: str
    category: str
    difficulty: str  # "初级", "中级", "高级"
    estimated_hours: int
    resources: List[str]
    prerequisites: List[str]
    learning_objectives: List[str]
    completion_criteria: List[str]


@dataclass
class LearningPath:
    """学习路径"""
    id: str
    user_id: str
    target_position: str
    current_level: str
    target_level: str
    total_duration: int  # 总时长（小时）
    total_tasks: int
    tasks: List[LearningTask]
    milestones: List[Dict[str, Any]]
    created_at: datetime
    estimated_completion: datetime


class LearningPathGenerator:
    """学习路径生成器"""
    
    def __init__(self):
        self.skill_roadmaps = {
            "前端开发": {
                "初级": ["HTML/CSS基础", "JavaScript基础", "响应式设计", "Git基础"],
                "中级": ["React/Vue框架", "TypeScript", "构建工具", "API集成"],
                "高级": ["性能优化", "架构设计", "测试驱动开发", "微前端"]
            },
            "后端开发": {
                "初级": ["Python/Java基础", "数据库基础", "API设计", "版本控制"],
                "中级": ["框架深入", "数据库优化", "缓存技术", "消息队列"],
                "高级": ["分布式系统", "微服务架构", "DevOps", "系统设计"]
            },
            "全栈开发": {
                "初级": ["前端基础", "后端基础", "数据库", "部署基础"],
                "中级": ["前后端分离", "状态管理", "API网关", "容器化"],
                "高级": ["全栈架构", "性能优化", "安全加固", "监控告警"]
            },
            "算法工程师": {
                "初级": ["数据结构", "基础算法", "Python编程", "数学基础"],
                "中级": ["机器学习", "深度学习", "数据处理", "模型评估"],
                "高级": ["算法优化", "大规模系统", "论文复现", "创新研究"]
            }
        }
        
        self.resource_templates = {
            "HTML/CSS基础": [
                "MDN Web Docs - HTML基础教程",
                "CSS Grid布局完全指南",
                "Flexbox布局实战"
            ],
            "JavaScript基础": [
                "JavaScript高级程序设计",
                "ES6+新特性详解",
                "异步编程与Promise"
            ],
            "React/Vue框架": [
                "React官方文档",
                "Vue.js实战教程",
                "状态管理Redux/Vuex"
            ],
            "Python/Java基础": [
                "Python官方教程",
                "Java核心技术",
                "面向对象编程"
            ],
            "数据库基础": [
                "SQL必知必会",
                "MySQL性能优化",
                "NoSQL数据库入门"
            ],
            "数据结构": [
                "算法导论",
                "数据结构与算法分析",
                "LeetCode刷题指南"
            ],
            "机器学习": [
                "机器学习实战",
                "统计学习方法",
                "Scikit-learn官方文档"
            ]
        }
    
    def generate_learning_path(self, 
                             user_id: str,
                             skill_report: Dict[str, Any],
                             target_position: str,
                             target_level: str = "中级",
                             available_hours_per_week: int = 20) -> LearningPath:
        """生成学习路径"""
        logger.info(f"开始生成学习路径: {user_id} -> {target_position}")
        
        # 分析当前技能水平
        current_level = self._analyze_current_level(skill_report)
        
        # 确定需要学习的技能
        required_skills = self._identify_required_skills(
            skill_report, target_position, current_level, target_level
        )
        
        # 生成学习任务
        tasks = self._generate_learning_tasks(required_skills, current_level, target_level)
        
        # 计算总时长
        total_duration = sum(task.estimated_hours for task in tasks)
        
        # 生成里程碑
        milestones = self._generate_milestones(tasks, total_duration)
        
        # 估算完成时间
        weeks_needed = total_duration / available_hours_per_week
        estimated_completion = datetime.now() + timedelta(weeks=weeks_needed)
        
        return LearningPath(
            id=f"path_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id=user_id,
            target_position=target_position,
            current_level=current_level,
            target_level=target_level,
            total_duration=total_duration,
            total_tasks=len(tasks),
            tasks=tasks,
            milestones=milestones,
            created_at=datetime.now(),
            estimated_completion=estimated_completion
        )
    
    def _analyze_current_level(self, skill_report: Dict[str, Any]) -> str:
        """分析当前技能水平"""
        overall_score = skill_report.get("overall_score", 0)
        
        if overall_score >= 2000:
            return "高级"
        elif overall_score >= 1000:
            return "中级"
        else:
            return "初级"
    
    def _identify_required_skills(self, skill_report: Dict[str, Any], 
                                target_position: str, current_level: str, target_level: str) -> List[str]:
        """识别需要学习的技能"""
        required_skills = []
        
        # 获取目标岗位的技能要求
        position_skills = self.skill_roadmaps.get(target_position, {})
        
        # 根据当前水平和目标水平确定需要学习的技能
        level_order = ["初级", "中级", "高级"]
        current_index = level_order.index(current_level)
        target_index = level_order.index(target_level)
        
        for i in range(current_index + 1, target_index + 1):
            level = level_order[i]
            if level in position_skills:
                required_skills.extend(position_skills[level])
        
        # 基于技能报告的弱点补充技能
        weaknesses = skill_report.get("weaknesses", [])
        for weakness in weaknesses:
            if "编程语言" in weakness:
                required_skills.append("编程语言进阶")
            elif "算法" in weakness:
                required_skills.append("算法与数据结构")
            elif "项目" in weakness:
                required_skills.append("项目实战")
        
        return list(set(required_skills))  # 去重
    
    def _generate_learning_tasks(self, required_skills: List[str], 
                               current_level: str, target_level: str) -> List[LearningTask]:
        """生成学习任务"""
        tasks = []
        task_id = 1
        
        for skill in required_skills:
            # 根据技能和水平确定任务难度
            difficulty = self._determine_task_difficulty(skill, current_level, target_level)
            
            # 估算学习时长
            estimated_hours = self._estimate_learning_hours(skill, difficulty)
            
            # 获取学习资源
            resources = self.resource_templates.get(skill, [
                f"{skill}官方文档",
                f"{skill}实战教程",
                f"{skill}最佳实践"
            ])
            
            # 生成学习目标
            learning_objectives = self._generate_learning_objectives(skill, difficulty)
            
            # 生成完成标准
            completion_criteria = self._generate_completion_criteria(skill, difficulty)
            
            task = LearningTask(
                id=f"task_{task_id:03d}",
                title=skill,
                description=f"学习{skill}相关知识和技能",
                category=self._categorize_skill(skill),
                difficulty=difficulty,
                estimated_hours=estimated_hours,
                resources=resources,
                prerequisites=self._get_prerequisites(skill),
                learning_objectives=learning_objectives,
                completion_criteria=completion_criteria
            )
            
            tasks.append(task)
            task_id += 1
        
        return tasks
    
    def _determine_task_difficulty(self, skill: str, current_level: str, target_level: str) -> str:
        """确定任务难度"""
        level_order = ["初级", "中级", "高级"]
        current_index = level_order.index(current_level)
        target_index = level_order.index(target_level)
        
        # 根据目标水平确定难度
        if target_level == "高级":
            return "高级"
        elif target_level == "中级":
            return "中级"
        else:
            return "初级"
    
    def _estimate_learning_hours(self, skill: str, difficulty: str) -> int:
        """估算学习时长"""
        base_hours = {
            "初级": 20,
            "中级": 40,
            "高级": 60
        }
        
        # 根据技能类型调整时长
        skill_multipliers = {
            "HTML/CSS基础": 0.8,
            "JavaScript基础": 1.2,
            "React/Vue框架": 1.5,
            "Python/Java基础": 1.0,
            "数据库基础": 1.3,
            "数据结构": 1.4,
            "机器学习": 2.0
        }
        
        multiplier = skill_multipliers.get(skill, 1.0)
        return int(base_hours[difficulty] * multiplier)
    
    def _categorize_skill(self, skill: str) -> str:
        """技能分类"""
        categories = {
            "前端": ["HTML", "CSS", "JavaScript", "React", "Vue", "TypeScript"],
            "后端": ["Python", "Java", "数据库", "API", "框架"],
            "算法": ["数据结构", "算法", "机器学习", "深度学习"],
            "工具": ["Git", "Docker", "构建工具", "测试"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in skill for keyword in keywords):
                return category
        
        return "其他"
    
    def _get_prerequisites(self, skill: str) -> List[str]:
        """获取前置要求"""
        prerequisites = {
            "React/Vue框架": ["JavaScript基础"],
            "TypeScript": ["JavaScript基础"],
            "数据库优化": ["数据库基础"],
            "机器学习": ["Python基础", "数学基础"],
            "深度学习": ["机器学习", "数学基础"]
        }
        
        return prerequisites.get(skill, [])
    
    def _generate_learning_objectives(self, skill: str, difficulty: str) -> List[str]:
        """生成学习目标"""
        objectives = {
            "初级": [
                f"理解{skill}的基本概念和原理",
                f"掌握{skill}的基础语法和用法",
                f"能够独立完成简单的{skill}项目"
            ],
            "中级": [
                f"深入理解{skill}的高级特性",
                f"掌握{skill}的最佳实践和设计模式",
                f"能够解决复杂的{skill}相关问题"
            ],
            "高级": [
                f"精通{skill}的底层原理和实现",
                f"能够设计和优化{skill}相关系统",
                f"具备{skill}领域的创新能力"
            ]
        }
        
        return objectives.get(difficulty, [])
    
    def _generate_completion_criteria(self, skill: str, difficulty: str) -> List[str]:
        """生成完成标准"""
        criteria = {
            "初级": [
                f"完成{skill}基础教程学习",
                f"通过相关测试或练习",
                f"完成一个小型{skill}项目"
            ],
            "中级": [
                f"完成{skill}进阶课程学习",
                f"解决多个{skill}相关问题",
                f"完成一个中等规模的{skill}项目"
            ],
            "高级": [
                f"完成{skill}高级课程学习",
                f"解决复杂的{skill}技术难题",
                f"完成一个大型{skill}项目或贡献开源项目"
            ]
        }
        
        return criteria.get(difficulty, [])
    
    def _generate_milestones(self, tasks: List[LearningTask], total_duration: int) -> List[Dict[str, Any]]:
        """生成里程碑"""
        milestones = []
        completed_hours = 0
        
        # 按25%, 50%, 75%, 100%设置里程碑
        milestone_percentages = [25, 50, 75, 100]
        
        for percentage in milestone_percentages:
            target_hours = total_duration * percentage / 100
            completed_tasks = []
            
            for task in tasks:
                if completed_hours + task.estimated_hours <= target_hours:
                    completed_tasks.append(task.title)
                    completed_hours += task.estimated_hours
                else:
                    break
            
            milestones.append({
                "percentage": percentage,
                "target_hours": target_hours,
                "completed_tasks": completed_tasks,
                "description": f"完成{percentage}%的学习目标"
            })
        
        return milestones
    
    def export_learning_path(self, learning_path: LearningPath, format: str = "json") -> str:
        """导出学习路径"""
        if format == "json":
            return json.dumps({
                "id": learning_path.id,
                "user_id": learning_path.user_id,
                "target_position": learning_path.target_position,
                "current_level": learning_path.current_level,
                "target_level": learning_path.target_level,
                "total_duration": learning_path.total_duration,
                "total_tasks": learning_path.total_tasks,
                "created_at": learning_path.created_at.isoformat(),
                "estimated_completion": learning_path.estimated_completion.isoformat(),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "category": task.category,
                        "difficulty": task.difficulty,
                        "estimated_hours": task.estimated_hours,
                        "resources": task.resources,
                        "prerequisites": task.prerequisites,
                        "learning_objectives": task.learning_objectives,
                        "completion_criteria": task.completion_criteria
                    }
                    for task in learning_path.tasks
                ],
                "milestones": learning_path.milestones
            }, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def get_learning_progress(self, learning_path: LearningPath, completed_tasks: List[str]) -> Dict[str, Any]:
        """获取学习进度"""
        total_tasks = len(learning_path.tasks)
        completed_count = len(completed_tasks)
        progress_percentage = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0
        
        # 计算已完成时长
        completed_hours = sum(
            task.estimated_hours for task in learning_path.tasks 
            if task.id in completed_tasks
        )
        
        # 估算剩余时间
        remaining_hours = learning_path.total_duration - completed_hours
        remaining_weeks = remaining_hours / 20  # 假设每周20小时
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "progress_percentage": progress_percentage,
            "completed_hours": completed_hours,
            "remaining_hours": remaining_hours,
            "remaining_weeks": remaining_weeks,
            "estimated_completion": datetime.now() + timedelta(weeks=remaining_weeks)
        } 