import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from dataclasses import dataclass, asdict
import logging

from app.models.skill import Skill
from app.models.job import Job
from app.models.learning import LearningPath, LearningTask
from app.models.user import User

@dataclass
class LearningResource:
    """学习资源数据类"""
    title: str
    type: str  # 'video', 'article', 'course', 'book', 'practice'
    url: str
    description: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    duration: str  # 预计学习时间
    provider: str
    rating: float = 0.0
    tags: List[str] = None

@dataclass
class LearningStep:
    """学习步骤数据类"""
    id: str
    title: str
    description: str
    skill_target: str
    target_proficiency: int
    estimated_hours: int
    prerequisites: List[str]
    resources: List[LearningResource]
    practice_tasks: List[str]
    assessment_criteria: List[str]
    milestone: bool = False

@dataclass
class LearningPathPlan:
    """学习路径计划数据类"""
    id: str
    title: str
    description: str
    target_job: str
    current_skills: Dict[str, int]
    target_skills: Dict[str, int]
    skill_gaps: Dict[str, int]
    total_estimated_hours: int
    estimated_completion_weeks: int
    difficulty_level: str
    steps: List[LearningStep]
    success_metrics: List[str]
    created_at: datetime

class LearningPathEnhanced:
    """增强版学习路径生成器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # 技能难度映射
        self.skill_difficulty = {
            'HTML': 'beginner',
            'CSS': 'beginner',
            'JavaScript': 'intermediate',
            'Python': 'intermediate',
            'React': 'intermediate',
            'Vue': 'intermediate',
            'Angular': 'advanced',
            'Node.js': 'intermediate',
            'Django': 'intermediate',
            'Flask': 'intermediate',
            'FastAPI': 'intermediate',
            'MySQL': 'intermediate',
            'PostgreSQL': 'intermediate',
            'MongoDB': 'intermediate',
            'Redis': 'intermediate',
            'Docker': 'advanced',
            'Kubernetes': 'advanced',
            'AWS': 'advanced',
            'Machine Learning': 'advanced',
            'Deep Learning': 'advanced',
            'Data Science': 'advanced',
            'System Design': 'advanced',
            'Algorithms': 'intermediate',
            'Data Structures': 'intermediate'
        }
        
        # 技能学习时间估算（小时）
        self.skill_learning_hours = {
            'HTML': 20,
            'CSS': 30,
            'JavaScript': 80,
            'Python': 60,
            'React': 50,
            'Vue': 45,
            'Angular': 70,
            'Node.js': 40,
            'Django': 50,
            'Flask': 30,
            'FastAPI': 25,
            'MySQL': 40,
            'PostgreSQL': 35,
            'MongoDB': 30,
            'Redis': 20,
            'Docker': 45,
            'Kubernetes': 60,
            'AWS': 80,
            'Machine Learning': 120,
            'Deep Learning': 150,
            'Data Science': 100,
            'System Design': 80,
            'Algorithms': 60,
            'Data Structures': 50
        }
        
        # 技能依赖关系
        self.skill_dependencies = {
            'React': ['JavaScript', 'HTML', 'CSS'],
            'Vue': ['JavaScript', 'HTML', 'CSS'],
            'Angular': ['JavaScript', 'TypeScript', 'HTML', 'CSS'],
            'Node.js': ['JavaScript'],
            'Django': ['Python'],
            'Flask': ['Python'],
            'FastAPI': ['Python'],
            'Docker': ['Linux'],
            'Kubernetes': ['Docker'],
            'AWS': ['Linux', 'Docker'],
            'Machine Learning': ['Python', 'Statistics'],
            'Deep Learning': ['Machine Learning', 'Python'],
            'Data Science': ['Python', 'Statistics', 'SQL'],
            'System Design': ['Database', 'API Design'],
            'TypeScript': ['JavaScript']
        }
        
        # 学习资源库
        self.learning_resources = self._initialize_resources()
    
    def _initialize_resources(self) -> Dict[str, List[LearningResource]]:
        """初始化学习资源库"""
        return {
            'Python': [
                LearningResource(
                    title="Python官方教程",
                    type="course",
                    url="https://docs.python.org/3/tutorial/",
                    description="Python官方提供的完整教程",
                    difficulty="beginner",
                    duration="40小时",
                    provider="Python.org",
                    rating=4.8,
                    tags=["official", "comprehensive"]
                ),
                LearningResource(
                    title="Python进阶编程",
                    type="book",
                    url="https://book.douban.com/subject/6049132/",
                    description="深入理解Python高级特性",
                    difficulty="advanced",
                    duration="60小时",
                    provider="豆瓣读书",
                    rating=4.6,
                    tags=["advanced", "deep-dive"]
                ),
                LearningResource(
                    title="LeetCode Python练习",
                    type="practice",
                    url="https://leetcode.com/problemset/all/",
                    description="通过算法题提升Python编程能力",
                    difficulty="intermediate",
                    duration="100小时",
                    provider="LeetCode",
                    rating=4.7,
                    tags=["practice", "algorithms"]
                )
            ],
            'JavaScript': [
                LearningResource(
                    title="现代JavaScript教程",
                    type="course",
                    url="https://javascript.info/",
                    description="全面的JavaScript学习资源",
                    difficulty="beginner",
                    duration="50小时",
                    provider="javascript.info",
                    rating=4.9,
                    tags=["modern", "comprehensive"]
                ),
                LearningResource(
                    title="JavaScript高级程序设计",
                    type="book",
                    url="https://book.douban.com/subject/10546125/",
                    description="JavaScript权威指南",
                    difficulty="intermediate",
                    duration="80小时",
                    provider="人民邮电出版社",
                    rating=4.5,
                    tags=["authoritative", "detailed"]
                )
            ],
            'React': [
                LearningResource(
                    title="React官方文档",
                    type="course",
                    url="https://react.dev/",
                    description="React官方学习资源",
                    difficulty="intermediate",
                    duration="30小时",
                    provider="React团队",
                    rating=4.8,
                    tags=["official", "up-to-date"]
                ),
                LearningResource(
                    title="React实战项目",
                    type="practice",
                    url="https://github.com/facebook/create-react-app",
                    description="通过实际项目学习React",
                    difficulty="intermediate",
                    duration="40小时",
                    provider="GitHub",
                    rating=4.6,
                    tags=["hands-on", "practical"]
                )
            ],
            'Machine Learning': [
                LearningResource(
                    title="机器学习实战",
                    type="course",
                    url="https://www.coursera.org/learn/machine-learning",
                    description="Andrew Ng的机器学习课程",
                    difficulty="intermediate",
                    duration="60小时",
                    provider="Coursera",
                    rating=4.9,
                    tags=["famous", "comprehensive"]
                ),
                LearningResource(
                    title="Scikit-learn实践",
                    type="practice",
                    url="https://scikit-learn.org/stable/tutorial/index.html",
                    description="使用Python进行机器学习实践",
                    difficulty="intermediate",
                    duration="40小时",
                    provider="Scikit-learn",
                    rating=4.7,
                    tags=["practical", "python"]
                )
            ]
        }
    
    def generate_learning_path(self, 
                             user_id: int, 
                             target_job_id: Optional[int] = None,
                             target_skills: Optional[Dict[str, int]] = None,
                             learning_style: str = "balanced") -> LearningPathPlan:
        """
        生成个性化学习路径
        
        Args:
            user_id: 用户ID
            target_job_id: 目标职位ID（可选）
            target_skills: 目标技能字典（可选）
            learning_style: 学习风格 ('fast', 'balanced', 'thorough')
        
        Returns:
            LearningPathPlan对象
        """
        # 获取用户当前技能
        current_skills = self._get_user_skills(user_id)
        
        # 确定目标技能
        if target_job_id:
            target_job = self.db.query(Job).filter(Job.id == target_job_id).first()
            if target_job:
                target_skills = self._extract_job_skills(target_job)
        
        if not target_skills:
            # 如果没有指定目标，基于用户当前技能推荐提升方向
            target_skills = self._recommend_skill_improvements(current_skills)
        
        # 计算技能差距
        skill_gaps = self._calculate_skill_gaps(current_skills, target_skills)
        
        # 生成学习步骤
        learning_steps = self._generate_learning_steps(
            current_skills, target_skills, skill_gaps, learning_style
        )
        
        # 计算总时间
        total_hours = sum(step.estimated_hours for step in learning_steps)
        estimated_weeks = max(1, total_hours // 10)  # 假设每周学习10小时
        
        # 确定难度级别
        difficulty_level = self._determine_difficulty_level(target_skills)
        
        # 生成成功指标
        success_metrics = self._generate_success_metrics(target_skills)
        
        # 创建学习路径计划
        plan = LearningPathPlan(
            id=f"path_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=f"个性化学习路径 - {target_job.title if target_job_id and target_job else '技能提升'}",
            description=f"基于当前技能水平定制的学习计划，预计{estimated_weeks}周完成",
            target_job=target_job.title if target_job_id and target_job else "技能提升",
            current_skills=current_skills,
            target_skills=target_skills,
            skill_gaps=skill_gaps,
            total_estimated_hours=total_hours,
            estimated_completion_weeks=estimated_weeks,
            difficulty_level=difficulty_level,
            steps=learning_steps,
            success_metrics=success_metrics,
            created_at=datetime.now()
        )
        
        # 保存到数据库
        self._save_learning_path(user_id, plan)
        
        return plan
    
    def _get_user_skills(self, user_id: int) -> Dict[str, int]:
        """获取用户当前技能"""
        skills = self.db.query(Skill).filter(Skill.user_id == user_id).all()
        return {skill.name: skill.proficiency_level for skill in skills}
    
    def _extract_job_skills(self, job: Job) -> Dict[str, int]:
        """从职位信息中提取技能要求"""
        skills = {}
        
        # 从职位描述和要求中提取技能
        text = f"{job.job_description} {job.requirements}".lower()
        
        for skill_name in self.skill_difficulty.keys():
            if skill_name.lower() in text:
                # 根据职位级别设定技能要求
                if job.experience_level == "1-3年":
                    skills[skill_name] = 60
                elif job.experience_level == "3-5年":
                    skills[skill_name] = 75
                elif job.experience_level == "5-10年":
                    skills[skill_name] = 85
                else:
                    skills[skill_name] = 70
        
        return skills
    
    def _recommend_skill_improvements(self, current_skills: Dict[str, int]) -> Dict[str, int]:
        """基于当前技能推荐提升方向"""
        recommendations = {}
        
        # 为现有技能推荐提升
        for skill, level in current_skills.items():
            if level < 80:
                recommendations[skill] = min(level + 20, 90)
        
        # 推荐相关技能
        for skill, level in current_skills.items():
            if level >= 60:  # 如果某技能已经比较熟练
                related_skills = self._get_related_skills(skill)
                for related_skill in related_skills:
                    if related_skill not in current_skills:
                        recommendations[related_skill] = 70
        
        return recommendations
    
    def _get_related_skills(self, skill: str) -> List[str]:
        """获取相关技能"""
        related = []
        
        if skill == "Python":
            related = ["Django", "Flask", "FastAPI", "Machine Learning"]
        elif skill == "JavaScript":
            related = ["React", "Vue", "Node.js", "TypeScript"]
        elif skill == "React":
            related = ["Redux", "Next.js", "TypeScript"]
        elif skill == "Machine Learning":
            related = ["Deep Learning", "Data Science", "TensorFlow", "PyTorch"]
        
        return related
    
    def _calculate_skill_gaps(self, current: Dict[str, int], target: Dict[str, int]) -> Dict[str, int]:
        """计算技能差距"""
        gaps = {}
        for skill, target_level in target.items():
            current_level = current.get(skill, 0)
            if target_level > current_level:
                gaps[skill] = target_level - current_level
        return gaps
    
    def _generate_learning_steps(self, 
                               current_skills: Dict[str, int],
                               target_skills: Dict[str, int],
                               skill_gaps: Dict[str, int],
                               learning_style: str) -> List[LearningStep]:
        """生成学习步骤"""
        steps = []
        
        # 根据依赖关系排序技能
        sorted_skills = self._sort_skills_by_dependency(list(skill_gaps.keys()))
        
        for i, skill in enumerate(sorted_skills):
            gap = skill_gaps[skill]
            current_level = current_skills.get(skill, 0)
            target_level = target_skills[skill]
            
            # 计算学习时间
            base_hours = self.skill_learning_hours.get(skill, 40)
            hours_multiplier = gap / 100  # 根据差距调整学习时间
            estimated_hours = int(base_hours * hours_multiplier)
            
            # 调整学习风格
            if learning_style == "fast":
                estimated_hours = int(estimated_hours * 0.7)
            elif learning_style == "thorough":
                estimated_hours = int(estimated_hours * 1.5)
            
            # 获取前置技能
            prerequisites = self.skill_dependencies.get(skill, [])
            
            # 获取学习资源
            resources = self.learning_resources.get(skill, [])
            
            # 生成实践任务
            practice_tasks = self._generate_practice_tasks(skill, target_level)
            
            # 生成评估标准
            assessment_criteria = self._generate_assessment_criteria(skill, target_level)
            
            step = LearningStep(
                id=f"step_{i+1}_{skill.lower().replace(' ', '_')}",
                title=f"学习 {skill}",
                description=f"从 {current_level}% 提升到 {target_level}%",
                skill_target=skill,
                target_proficiency=target_level,
                estimated_hours=estimated_hours,
                prerequisites=prerequisites,
                resources=resources,
                practice_tasks=practice_tasks,
                assessment_criteria=assessment_criteria,
                milestone=(i + 1) % 3 == 0  # 每3个步骤设置一个里程碑
            )
            
            steps.append(step)
        
        return steps
    
    def _sort_skills_by_dependency(self, skills: List[str]) -> List[str]:
        """根据依赖关系排序技能"""
        sorted_skills = []
        remaining_skills = skills.copy()
        
        while remaining_skills:
            for skill in remaining_skills:
                dependencies = self.skill_dependencies.get(skill, [])
                # 检查依赖是否已经在排序列表中或不在需要学习的技能中
                if all(dep in sorted_skills or dep not in skills for dep in dependencies):
                    sorted_skills.append(skill)
                    remaining_skills.remove(skill)
                    break
            else:
                # 如果没有找到可以添加的技能，说明有循环依赖，直接添加剩余技能
                sorted_skills.extend(remaining_skills)
                break
        
        return sorted_skills
    
    def _generate_practice_tasks(self, skill: str, target_level: int) -> List[str]:
        """生成实践任务"""
        tasks = []
        
        if skill == "Python":
            tasks = [
                "完成Python基础语法练习",
                "实现数据结构和算法",
                "开发一个Web应用",
                "参与开源项目贡献"
            ]
        elif skill == "JavaScript":
            tasks = [
                "完成JavaScript基础练习",
                "实现DOM操作项目",
                "开发交互式网页",
                "学习ES6+新特性"
            ]
        elif skill == "React":
            tasks = [
                "创建React基础组件",
                "实现状态管理",
                "开发完整的React应用",
                "优化性能和用户体验"
            ]
        else:
            tasks = [
                f"学习{skill}基础概念",
                f"完成{skill}实践项目",
                f"深入理解{skill}高级特性",
                f"在实际项目中应用{skill}"
            ]
        
        # 根据目标水平调整任务数量
        if target_level < 60:
            return tasks[:2]
        elif target_level < 80:
            return tasks[:3]
        else:
            return tasks
    
    def _generate_assessment_criteria(self, skill: str, target_level: int) -> List[str]:
        """生成评估标准"""
        criteria = []
        
        if target_level >= 60:
            criteria.append(f"能够独立使用{skill}完成基本任务")
        if target_level >= 70:
            criteria.append(f"理解{skill}的核心概念和最佳实践")
        if target_level >= 80:
            criteria.append(f"能够解决{skill}相关的复杂问题")
        if target_level >= 90:
            criteria.append(f"能够指导他人学习{skill}并优化性能")
        
        return criteria
    
    def _determine_difficulty_level(self, target_skills: Dict[str, int]) -> str:
        """确定学习路径的难度级别"""
        avg_target_level = sum(target_skills.values()) / len(target_skills)
        advanced_skills = sum(1 for skill in target_skills.keys() 
                            if self.skill_difficulty.get(skill, 'intermediate') == 'advanced')
        
        if avg_target_level >= 80 or advanced_skills >= 2:
            return "advanced"
        elif avg_target_level >= 60:
            return "intermediate"
        else:
            return "beginner"
    
    def _generate_success_metrics(self, target_skills: Dict[str, int]) -> List[str]:
        """生成成功指标"""
        metrics = []
        
        for skill, level in target_skills.items():
            if level >= 80:
                metrics.append(f"{skill}达到高级水平(≥80%)")
            elif level >= 60:
                metrics.append(f"{skill}达到中级水平(≥60%)")
            else:
                metrics.append(f"{skill}达到基础水平(≥40%)")
        
        metrics.append("完成所有实践项目")
        metrics.append("通过技能评估测试")
        
        return metrics
    
    def _save_learning_path(self, user_id: int, plan: LearningPathPlan):
        """保存学习路径到数据库"""
        try:
            # 保存学习路径
            learning_path = LearningPath(
                user_id=user_id,
                title=plan.title,
                description=plan.description,
                target_job=plan.target_job,
                difficulty_level=plan.difficulty_level,
                estimated_hours=plan.total_estimated_hours,
                estimated_weeks=plan.estimated_completion_weeks,
                path_data=json.dumps(asdict(plan), ensure_ascii=False, default=str),
                created_at=datetime.now()
            )
            
            self.db.add(learning_path)
            self.db.flush()  # 获取ID
            
            # 保存学习任务
            for step in plan.steps:
                task = LearningTask(
                    learning_path_id=learning_path.id,
                    title=step.title,
                    description=step.description,
                    skill_target=step.skill_target,
                    target_proficiency=step.target_proficiency,
                    estimated_hours=step.estimated_hours,
                    prerequisites=json.dumps(step.prerequisites),
                    resources=json.dumps([asdict(r) for r in step.resources], ensure_ascii=False),
                    practice_tasks=json.dumps(step.practice_tasks, ensure_ascii=False),
                    assessment_criteria=json.dumps(step.assessment_criteria, ensure_ascii=False),
                    is_milestone=step.milestone,
                    status='pending'
                )
                self.db.add(task)
            
            self.db.commit()
            self.logger.info(f"学习路径已保存: {plan.title}")
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"保存学习路径失败: {str(e)}")
            raise
    
    def get_user_learning_paths(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的学习路径"""
        paths = self.db.query(LearningPath).filter(LearningPath.user_id == user_id).all()
        
        result = []
        for path in paths:
            tasks = self.db.query(LearningTask).filter(LearningTask.learning_path_id == path.id).all()
            
            path_dict = {
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'target_job': path.target_job,
                'difficulty_level': path.difficulty_level,
                'estimated_hours': path.estimated_hours,
                'estimated_weeks': path.estimated_weeks,
                'created_at': path.created_at.isoformat() if path.created_at else None,
                'progress': self._calculate_path_progress(tasks),
                'tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'skill_target': task.skill_target,
                        'target_proficiency': task.target_proficiency,
                        'estimated_hours': task.estimated_hours,
                        'status': task.status,
                        'progress': task.progress,
                        'is_milestone': task.is_milestone,
                        'prerequisites': json.loads(task.prerequisites) if task.prerequisites else [],
                        'resources': json.loads(task.resources) if task.resources else [],
                        'practice_tasks': json.loads(task.practice_tasks) if task.practice_tasks else [],
                        'assessment_criteria': json.loads(task.assessment_criteria) if task.assessment_criteria else []
                    }
                    for task in tasks
                ]
            }
            result.append(path_dict)
        
        return result
    
    def _calculate_path_progress(self, tasks: List[LearningTask]) -> float:
        """计算学习路径进度"""
        if not tasks:
            return 0.0
        
        total_progress = sum(task.progress for task in tasks)
        return round(total_progress / len(tasks), 1)
    
    def update_task_progress(self, task_id: int, progress: int, status: str = None) -> bool:
        """更新任务进度"""
        try:
            task = self.db.query(LearningTask).filter(LearningTask.id == task_id).first()
            if not task:
                return False
            
            task.progress = min(max(progress, 0), 100)
            if status:
                task.status = status
            
            # 如果任务完成，自动设置状态
            if progress >= 100:
                task.status = 'completed'
                task.completed_at = datetime.now()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"更新任务进度失败: {str(e)}")
            return False 