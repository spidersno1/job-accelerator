"""
每日任务生成模块

基于学习路径和用户进度，生成AI督学任务
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import random
import json

logger = logging.getLogger(__name__)


@dataclass
class DailyTask:
    """每日任务"""
    id: str
    title: str
    description: str
    category: str
    difficulty: str
    estimated_minutes: int
    learning_objectives: List[str]
    resources: List[str]
    practice_exercises: List[str]
    completion_criteria: List[str]
    created_at: datetime
    due_date: datetime
    is_completed: bool = False
    completed_at: Optional[datetime] = None


@dataclass
class WeeklyPlan:
    """周计划"""
    id: str
    user_id: str
    week_start: datetime
    week_end: datetime
    daily_tasks: List[DailyTask]
    weekly_goals: List[str]
    progress_summary: Dict[str, Any]
    created_at: datetime


class DailyTaskGenerator:
    """每日任务生成器"""
    
    def __init__(self):
        self.task_templates = {
            "理论学习": {
                "templates": [
                    "学习{skill}的核心概念和原理",
                    "阅读{skill}相关文档和教程",
                    "理解{skill}的设计模式和最佳实践",
                    "掌握{skill}的基础语法和用法"
                ],
                "estimated_minutes": 60,
                "difficulty": "初级"
            },
            "实践练习": {
                "templates": [
                    "完成{skill}相关的编程练习",
                    "实现{skill}的示例项目",
                    "解决{skill}相关的技术问题",
                    "编写{skill}的测试用例"
                ],
                "estimated_minutes": 90,
                "difficulty": "中级"
            },
            "项目实战": {
                "templates": [
                    "开发一个{skill}相关的完整项目",
                    "优化现有{skill}项目的性能",
                    "重构{skill}代码，提升代码质量",
                    "集成{skill}到现有系统中"
                ],
                "estimated_minutes": 120,
                "difficulty": "高级"
            },
            "知识巩固": {
                "templates": [
                    "复习{skill}的重要知识点",
                    "总结{skill}的学习心得",
                    "整理{skill}的常见问题和解决方案",
                    "分享{skill}的学习经验"
                ],
                "estimated_minutes": 45,
                "difficulty": "初级"
            },
            "技能提升": {
                "templates": [
                    "挑战{skill}的高级特性",
                    "学习{skill}的进阶用法",
                    "探索{skill}的新功能和特性",
                    "研究{skill}的底层实现原理"
                ],
                "estimated_minutes": 75,
                "difficulty": "高级"
            }
        }
        
        self.exercise_templates = {
            "编程练习": [
                "编写一个简单的{skill}程序",
                "实现{skill}的基本功能",
                "调试{skill}代码中的错误",
                "优化{skill}代码的性能"
            ],
            "算法练习": [
                "解决{skill}相关的算法问题",
                "实现{skill}的数据结构",
                "分析{skill}算法的时间复杂度",
                "优化{skill}算法的空间复杂度"
            ],
            "项目练习": [
                "创建{skill}的演示项目",
                "完善{skill}项目的功能",
                "测试{skill}项目的稳定性",
                "部署{skill}项目到生产环境"
            ]
        }
        
        self.resource_categories = {
            "文档": ["官方文档", "API参考", "最佳实践指南"],
            "教程": ["入门教程", "进阶教程", "实战教程"],
            "视频": ["在线课程", "技术分享", "实战演示"],
            "书籍": ["技术书籍", "参考手册", "学习资料"],
            "社区": ["技术论坛", "问答平台", "开源项目"]
        }
    
    def generate_weekly_plan(self, 
                           user_id: str,
                           learning_path: Dict[str, Any],
                           current_progress: Dict[str, Any],
                           available_hours_per_day: int = 2) -> WeeklyPlan:
        """生成周计划"""
        logger.info(f"开始生成周计划: {user_id}")
        
        # 确定本周的学习重点
        current_tasks = self._get_current_learning_tasks(learning_path, current_progress)
        
        # 生成每日任务
        daily_tasks = []
        week_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day in range(7):
            task_date = week_start + timedelta(days=day)
            day_tasks = self._generate_daily_tasks(
                current_tasks, 
                available_hours_per_day,
                task_date
            )
            daily_tasks.extend(day_tasks)
        
        # 生成周目标
        weekly_goals = self._generate_weekly_goals(current_tasks, learning_path)
        
        # 生成进度摘要
        progress_summary = self._generate_progress_summary(daily_tasks, weekly_goals)
        
        return WeeklyPlan(
            id=f"week_{user_id}_{week_start.strftime('%Y%m%d')}",
            user_id=user_id,
            week_start=week_start,
            week_end=week_start + timedelta(days=6),
            daily_tasks=daily_tasks,
            weekly_goals=weekly_goals,
            progress_summary=progress_summary,
            created_at=datetime.now()
        )
    
    def _get_current_learning_tasks(self, learning_path: Dict[str, Any], 
                                  current_progress: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取当前学习任务"""
        tasks = learning_path.get("tasks", [])
        completed_tasks = current_progress.get("completed_tasks", [])
        
        # 过滤出未完成的任务
        current_tasks = []
        for task in tasks:
            if task["id"] not in completed_tasks:
                current_tasks.append(task)
        
        # 按优先级排序（考虑前置要求）
        return self._sort_tasks_by_priority(current_tasks, completed_tasks)
    
    def _sort_tasks_by_priority(self, tasks: List[Dict[str, Any]], 
                              completed_tasks: List[str]) -> List[Dict[str, Any]]:
        """按优先级排序任务"""
        def calculate_priority(task):
            priority = 0
            # 前置要求越少，优先级越高
            prerequisites = task.get("prerequisites", [])
            unmet_prerequisites = [p for p in prerequisites if p not in completed_tasks]
            priority -= len(unmet_prerequisites) * 10
            
            # 难度越高，优先级越高
            difficulty = task.get("difficulty", "初级")
            if difficulty == "高级":
                priority += 5
            elif difficulty == "中级":
                priority += 3
            
            return priority
        
        return sorted(tasks, key=calculate_priority, reverse=True)
    
    def _generate_daily_tasks(self, current_tasks: List[Dict[str, Any]], 
                            available_hours_per_day: int, task_date: datetime) -> List[DailyTask]:
        """生成每日任务"""
        daily_tasks = []
        available_minutes = available_hours_per_day * 60
        
        # 选择当天的学习任务
        selected_tasks = self._select_daily_tasks(current_tasks, available_minutes)
        
        for i, task in enumerate(selected_tasks):
            # 生成任务内容
            task_content = self._generate_task_content(task)
            
            # 创建每日任务
            daily_task = DailyTask(
                id=f"daily_{task_date.strftime('%Y%m%d')}_{i+1:02d}",
                title=task_content["title"],
                description=task_content["description"],
                category=task_content["category"],
                difficulty=task_content["difficulty"],
                estimated_minutes=task_content["estimated_minutes"],
                learning_objectives=task_content["learning_objectives"],
                resources=task_content["resources"],
                practice_exercises=task_content["practice_exercises"],
                completion_criteria=task_content["completion_criteria"],
                created_at=datetime.now(),
                due_date=task_date.replace(hour=23, minute=59, second=59)
            )
            
            daily_tasks.append(daily_task)
        
        return daily_tasks
    
    def _select_daily_tasks(self, current_tasks: List[Dict[str, Any]], 
                          available_minutes: int) -> List[Dict[str, Any]]:
        """选择每日任务"""
        selected_tasks = []
        remaining_minutes = available_minutes
        
        for task in current_tasks:
            if remaining_minutes <= 0:
                break
            
            # 估算任务时长
            estimated_minutes = self._estimate_task_minutes(task)
            
            if estimated_minutes <= remaining_minutes:
                selected_tasks.append(task)
                remaining_minutes -= estimated_minutes
        
        return selected_tasks
    
    def _estimate_task_minutes(self, task: Dict[str, Any]) -> int:
        """估算任务时长"""
        difficulty = task.get("difficulty", "中级")
        base_minutes = {
            "初级": 45,
            "中级": 75,
            "高级": 120
        }
        
        return base_minutes.get(difficulty, 60)
    
    def _generate_task_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成任务内容"""
        skill = task.get("title", "")
        difficulty = task.get("difficulty", "中级")
        
        # 选择任务类型
        task_types = list(self.task_templates.keys())
        task_type = random.choice(task_types)
        
        # 生成标题和描述
        template = random.choice(self.task_templates[task_type]["templates"])
        title = template.format(skill=skill)
        description = f"通过{task_type}的方式学习{skill}，提升相关技能水平"
        
        # 生成学习目标
        learning_objectives = self._generate_learning_objectives(skill, task_type, difficulty)
        
        # 生成学习资源
        resources = self._generate_resources(skill, task_type)
        
        # 生成练习题目
        practice_exercises = self._generate_practice_exercises(skill, task_type)
        
        # 生成完成标准
        completion_criteria = self._generate_completion_criteria(skill, task_type, difficulty)
        
        return {
            "title": title,
            "description": description,
            "category": task_type,
            "difficulty": difficulty,
            "estimated_minutes": self.task_templates[task_type]["estimated_minutes"],
            "learning_objectives": learning_objectives,
            "resources": resources,
            "practice_exercises": practice_exercises,
            "completion_criteria": completion_criteria
        }
    
    def _generate_learning_objectives(self, skill: str, task_type: str, difficulty: str) -> List[str]:
        """生成学习目标"""
        objectives = []
        
        if task_type == "理论学习":
            objectives = [
                f"理解{skill}的基本概念和原理",
                f"掌握{skill}的核心知识点",
                f"了解{skill}的应用场景和优势"
            ]
        elif task_type == "实践练习":
            objectives = [
                f"通过实践掌握{skill}的用法",
                f"解决{skill}相关的实际问题",
                f"提升{skill}的编程技能"
            ]
        elif task_type == "项目实战":
            objectives = [
                f"在真实项目中应用{skill}",
                f"提升{skill}的项目开发能力",
                f"掌握{skill}的最佳实践"
            ]
        
        return objectives
    
    def _generate_resources(self, skill: str, task_type: str) -> List[str]:
        """生成学习资源"""
        resources = []
        
        # 根据任务类型选择资源类别
        if task_type == "理论学习":
            resource_cats = ["文档", "教程", "书籍"]
        elif task_type == "实践练习":
            resource_cats = ["教程", "视频", "社区"]
        else:
            resource_cats = ["文档", "视频", "社区"]
        
        for cat in resource_cats:
            if cat in self.resource_categories:
                resource = random.choice(self.resource_categories[cat])
                resources.append(f"{skill}{resource}")
        
        return resources[:3]  # 限制资源数量
    
    def _generate_practice_exercises(self, skill: str, task_type: str) -> List[str]:
        """生成练习题目"""
        exercises = []
        
        if task_type == "实践练习":
            exercise_type = random.choice(list(self.exercise_templates.keys()))
            template = random.choice(self.exercise_templates[exercise_type])
            exercises.append(template.format(skill=skill))
        elif task_type == "项目实战":
            exercises.append(f"开发一个{skill}相关的完整项目")
            exercises.append(f"优化现有{skill}项目的性能")
        
        return exercises
    
    def _generate_completion_criteria(self, skill: str, task_type: str, difficulty: str) -> List[str]:
        """生成完成标准"""
        criteria = []
        
        if task_type == "理论学习":
            criteria = [
                f"完成{skill}相关文档的阅读",
                f"理解{skill}的核心概念",
                f"能够解释{skill}的基本原理"
            ]
        elif task_type == "实践练习":
            criteria = [
                f"完成{skill}相关的编程练习",
                f"代码能够正常运行",
                f"通过相关的测试用例"
            ]
        elif task_type == "项目实战":
            criteria = [
                f"完成{skill}项目的开发",
                f"项目功能完整可用",
                f"代码质量达到要求"
            ]
        
        return criteria
    
    def _generate_weekly_goals(self, current_tasks: List[Dict[str, Any]], 
                             learning_path: Dict[str, Any]) -> List[str]:
        """生成周目标"""
        goals = []
        
        # 基于当前任务生成目标
        if current_tasks:
            top_task = current_tasks[0]
            goals.append(f"掌握{top_task['title']}的核心概念和用法")
            
            if len(current_tasks) > 1:
                second_task = current_tasks[1]
                goals.append(f"开始学习{second_task['title']}的基础知识")
        
        # 添加通用目标
        goals.append("保持每日学习习惯，完成所有计划任务")
        goals.append("总结本周学习心得，记录重要知识点")
        
        return goals
    
    def _generate_progress_summary(self, daily_tasks: List[DailyTask], 
                                 weekly_goals: List[str]) -> Dict[str, Any]:
        """生成进度摘要"""
        total_tasks = len(daily_tasks)
        total_minutes = sum(task.estimated_minutes for task in daily_tasks)
        
        # 按类别统计
        category_stats = {}
        for task in daily_tasks:
            category = task.category
            if category not in category_stats:
                category_stats[category] = {"count": 0, "minutes": 0}
            category_stats[category]["count"] += 1
            category_stats[category]["minutes"] += task.estimated_minutes
        
        return {
            "total_tasks": total_tasks,
            "total_minutes": total_minutes,
            "total_hours": total_minutes / 60,
            "category_stats": category_stats,
            "weekly_goals": weekly_goals
        }
    
    def generate_motivational_message(self, user_progress: Dict[str, Any]) -> str:
        """生成激励消息"""
        messages = [
            "坚持就是胜利！每天进步一点点，离目标更近一步。",
            "学习编程就像搭积木，每一步都很重要。继续加油！",
            "你已经很棒了！保持这个学习节奏，成功就在前方。",
            "编程之路没有捷径，但每一步都算数。坚持住！",
            "今天的努力是为了明天的成功。相信自己，你可以的！"
        ]
        
        # 根据进度调整消息
        progress_percentage = user_progress.get("progress_percentage", 0)
        if progress_percentage >= 80:
            messages.extend([
                "太棒了！你已经接近目标了，继续冲刺！",
                "胜利在望！保持这个状态，成功就在眼前。"
            ])
        elif progress_percentage >= 50:
            messages.extend([
                "已经过半了！保持这个势头，继续前进！",
                "做得很棒！你已经完成了大部分工作。"
            ])
        else:
            messages.extend([
                "好的开始是成功的一半！继续努力！",
                "每一步都在为成功铺路，加油！"
            ])
        
        return random.choice(messages)
    
    def export_weekly_plan(self, weekly_plan: WeeklyPlan, format: str = "json") -> str:
        """导出周计划"""
        if format == "json":
            return json.dumps({
                "id": weekly_plan.id,
                "user_id": weekly_plan.user_id,
                "week_start": weekly_plan.week_start.isoformat(),
                "week_end": weekly_plan.week_end.isoformat(),
                "weekly_goals": weekly_plan.weekly_goals,
                "progress_summary": weekly_plan.progress_summary,
                "created_at": weekly_plan.created_at.isoformat(),
                "daily_tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "category": task.category,
                        "difficulty": task.difficulty,
                        "estimated_minutes": task.estimated_minutes,
                        "learning_objectives": task.learning_objectives,
                        "resources": task.resources,
                        "practice_exercises": task.practice_exercises,
                        "completion_criteria": task.completion_criteria,
                        "due_date": task.due_date.isoformat(),
                        "is_completed": task.is_completed
                    }
                    for task in weekly_plan.daily_tasks
                ]
            }, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def get_daily_progress(self, daily_tasks: List[DailyTask]) -> Dict[str, Any]:
        """获取每日进度"""
        total_tasks = len(daily_tasks)
        completed_tasks = [task for task in daily_tasks if task.is_completed]
        completed_count = len(completed_tasks)
        
        progress_percentage = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0
        
        total_minutes = sum(task.estimated_minutes for task in daily_tasks)
        completed_minutes = sum(task.estimated_minutes for task in completed_tasks)
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "progress_percentage": progress_percentage,
            "total_minutes": total_minutes,
            "completed_minutes": completed_minutes,
            "remaining_minutes": total_minutes - completed_minutes
        } 