from typing import Dict, Any, List
from sqlalchemy.orm import Session
import json

class LearningPathGenerator:
    def __init__(self):
        self.role_paths = {
            "前端开发工程师": {
                "path_name": "前端开发工程师学习路径",
                "description": "从HTML/CSS基础到现代前端框架的完整学习路径",
                "estimated_duration": 90,
                "tasks": [
                    {
                        "task_name": "HTML/CSS基础",
                        "description": "学习HTML5和CSS3的基础语法和布局",
                        "task_type": "学习",
                        "difficulty": "简单",
                        "estimated_hours": 20,
                        "resources": json.dumps(["https://developer.mozilla.org/zh-CN/docs/Web/HTML"])
                    },
                    {
                        "task_name": "JavaScript基础",
                        "description": "掌握JavaScript核心概念和ES6+语法",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 40,
                        "resources": json.dumps(["https://developer.mozilla.org/zh-CN/docs/Web/JavaScript"])
                    },
                    {
                        "task_name": "React框架学习",
                        "description": "学习React核心概念和Hooks",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 30,
                        "resources": json.dumps(["https://react.dev/"])
                    }
                ]
            },
            "后端开发工程师": {
                "path_name": "后端开发工程师学习路径",
                "description": "从编程语言基础到微服务架构的完整学习路径",
                "estimated_duration": 120,
                "tasks": [
                    {
                        "task_name": "Python基础",
                        "description": "学习Python语法和面向对象编程",
                        "task_type": "学习",
                        "difficulty": "简单",
                        "estimated_hours": 30,
                        "resources": json.dumps(["https://docs.python.org/zh-cn/3/"])
                    },
                    {
                        "task_name": "FastAPI框架",
                        "description": "学习FastAPI构建RESTful API",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 25,
                        "resources": json.dumps(["https://fastapi.tiangolo.com/"])
                    },
                    {
                        "task_name": "数据库设计",
                        "description": "学习SQL和数据库设计原则",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 20,
                        "resources": json.dumps(["https://www.postgresql.org/docs/"])
                    }
                ]
            },
            "数据分析师": {
                "path_name": "数据分析师学习路径",
                "description": "从数据处理到机器学习建模的完整学习路径",
                "estimated_duration": 150,
                "tasks": [
                    {
                        "task_name": "Python数据分析基础",
                        "description": "学习NumPy、Pandas数据处理",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 40,
                        "resources": json.dumps(["https://pandas.pydata.org/docs/"])
                    },
                    {
                        "task_name": "数据可视化",
                        "description": "掌握Matplotlib和Seaborn可视化",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 30,
                        "resources": json.dumps(["https://matplotlib.org/stable/contents.html"])
                    },
                    {
                        "task_name": "机器学习基础",
                        "description": "学习Scikit-learn机器学习",
                        "task_type": "学习",
                        "difficulty": "困难",
                        "estimated_hours": 50,
                        "resources": json.dumps(["https://scikit-learn.org/stable/"])
                    }
                ]
            },
            "DevOps工程师": {
                "path_name": "DevOps工程师学习路径",
                "description": "从Linux基础到云原生架构的完整学习路径",
                "estimated_duration": 180,
                "tasks": [
                    {
                        "task_name": "Linux系统管理",
                        "description": "学习Linux常用命令和系统管理",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 40,
                        "resources": json.dumps(["https://linuxjourney.com/"])
                    },
                    {
                        "task_name": "Docker容器技术",
                        "description": "掌握Docker容器化技术",
                        "task_type": "学习",
                        "difficulty": "中等",
                        "estimated_hours": 30,
                        "resources": json.dumps(["https://docs.docker.com/"])
                    },
                    {
                        "task_name": "Kubernetes编排",
                        "description": "学习Kubernetes集群管理",
                        "task_type": "学习",
                        "difficulty": "困难",
                        "estimated_hours": 50,
                        "resources": json.dumps(["https://kubernetes.io/docs/home/"])
                    }
                ]
            }
        }
    
    async def generate_path(self, target_role: str, user_id: int, db: Session, skill_report: Dict[str, Any] = None, progress: Dict[str, Any] = None, leetcode_username: str = None) -> Dict[str, Any]:
        """生成学习路径
        Args:
            target_role: 目标岗位
            user_id: 用户ID
            db: 数据库会话
            skill_report: 技能分析报告
            progress: 用户当前学习进度
            leetcode_username: LeetCode用户名(可选)
        """
        if target_role in self.role_paths:
            path = self.role_paths[target_role].copy()
            
            # 整合LeetCode数据
            if leetcode_username:
                from backend.app.services.leetcode_service import LeetCodeService
                leetcode_service = LeetCodeService()
                leetcode_skills = await leetcode_service.analyze_user_skills(leetcode_username)
                if leetcode_skills:
                    if not skill_report:
                        skill_report = {"strengths": [], "weaknesses": []}
                    skill_report["strengths"].extend(leetcode_skills)
            
            if skill_report:
                path = self._customize_path(path, skill_report)
            if progress:
                path = self._apply_progress(path, progress)
            return path
        else:
            return self._generate_default_path(target_role)

    def _apply_progress(self, path: Dict[str, Any], progress: Dict[str, Any]) -> Dict[str, Any]:
        """应用用户学习进度"""
        completed_tasks = progress.get('completed_tasks', [])
        in_progress_tasks = progress.get('in_progress_tasks', {})
        
        for task in path['tasks']:
            if task['task_name'] in completed_tasks:
                task['status'] = 'completed'
                task['progress'] = 100
            elif task['task_name'] in in_progress_tasks:
                task['status'] = 'in_progress'
                task['progress'] = in_progress_tasks[task['task_name']]
            else:
                task['status'] = 'not_started'
                task['progress'] = 0
        
        # 计算整体进度
        total_tasks = len(path['tasks'])
        completed_count = len(completed_tasks)
        in_progress_sum = sum(
            p for t, p in in_progress_tasks.items() 
            if t not in completed_tasks
        ) / 100
        path['overall_progress'] = round(
            (completed_count + in_progress_sum) / total_tasks * 100, 
            1
        )
        return path
    
    def _customize_path(self, path: Dict[str, Any], skill_report: Dict[str, Any]) -> Dict[str, Any]:
        """根据技能报告定制学习路径"""
        # 1. 识别需要强化的技能
        weak_skills = {s['skill_name']: s['proficiency'] for s in skill_report.get('weaknesses', [])}
        
        # 2. 调整任务优先级和依赖关系
        for i, task in enumerate(path['tasks']):
            # 添加前置任务要求
            if i > 0:
                task['prerequisites'] = [path['tasks'][i-1]['task_name']]
            
            # 如果任务相关技能是弱项，增加学习时间
            for skill in weak_skills:
                if skill.lower() in task['task_name'].lower():
                    task['estimated_hours'] = min(
                        int(task['estimated_hours'] * 1.5), 
                        100  # 最大不超过100小时
                    )
                    task['description'] += f" (需重点强化)"
                    task['difficulty'] = self._adjust_difficulty(task['difficulty'], weak_skills[skill])
        
        # 3. 添加针对弱项的额外任务
        if weak_skills:
            path['tasks'].insert(0, {
                "task_name": "基础技能强化",
                "description": f"重点强化{len(weak_skills)}项薄弱技能",
                "task_type": "强化",
                "difficulty": "中等",
                "estimated_hours": 20,
                "resources": self._recommend_resources(weak_skills.keys())
            })
            path['estimated_duration'] += 20
        
        return path

    def _adjust_difficulty(self, current: str, proficiency: float) -> str:
        """根据熟练度调整难度"""
        if proficiency < 0.3:
            return "困难" if current == "中等" else current
        return current

    def _recommend_resources(self, skills: List[str]) -> str:
        """智能推荐学习资源"""
        resource_map = {
            "react": ["https://react.dev/learn", "https://egghead.io/t/react"],
            "python": ["https://realpython.com", "https://www.pythoncheatsheet.org"],
            "数据分析": ["https://www.kaggle.com/learn", "https://www.datacamp.com"],
            "机器学习": ["https://www.coursera.org/learn/machine-learning", "https://developers.google.com/machine-learning/crash-course"],
            "docker": ["https://docker-curriculum.com", "https://training.play-with-docker.com"],
            "kubernetes": ["https://kubernetes.io/docs/tutorials", "https://www.katacoda.com/courses/kubernetes"]
        }
        
        resources = []
        for skill in skills:
            skill_lower = skill.lower()
            matched = False
            
            # 检查精确匹配
            for key, urls in resource_map.items():
                if key in skill_lower:
                    resources.extend(urls)
                    matched = True
                    break
            
            # 如果没有精确匹配，尝试模糊匹配
            if not matched:
                if "前端" in skill or "web" in skill_lower:
                    resources.append("https://developer.mozilla.org")
                elif "后端" in skill or "api" in skill_lower:
                    resources.append("https://dev.to/t/backend")
                elif "数据" in skill:
                    resources.append("https://towardsdatascience.com")
                elif "devops" in skill_lower:
                    resources.append("https://devops.com")
                else:
                    resources.append(f"https://www.google.com/search?q={skill}+教程")
        
        # 去重并限制数量
        unique_resources = list(dict.fromkeys(resources))
        return json.dumps(unique_resources[:5])  # 最多推荐5个资源
    
    def _generate_default_path(self, target_role: str) -> Dict[str, Any]:
        """生成默认学习路径"""
        return {
            "path_name": f"{target_role}学习路径",
            "description": f"成为{target_role}的通用学习路径",
            "estimated_duration": 90,
            "tasks": [
                {
                    "task_name": "基础知识学习",
                    "description": "学习相关领域的基础知识",
                    "task_type": "学习",
                    "difficulty": "简单",
                    "estimated_hours": 30,
                    "resources": json.dumps(["https://www.google.com"])
                },
                {
                    "task_name": "进阶技能学习",
                    "description": "学习进阶技能和框架",
                    "task_type": "学习",
                    "difficulty": "中等",
                    "estimated_hours": 40,
                    "resources": json.dumps(["https://github.com"])
                }
            ]
        }

    def generate_ai_suggestions(self, path: Dict[str, Any], progress: Dict[str, Any]) -> Dict[str, Any]:
        """生成AI学习建议
        根据用户当前学习进度和路径情况，提供智能化的学习建议
        
        Args:
            path: 当前学习路径数据，包含任务列表和进度信息
            progress: 用户学习进度数据，包含已完成任务和进行中任务
            
        Returns:
            更新后的学习路径数据，包含新增的AI建议列表
            
        建议类型包括:
        1. 进度相关建议 - 根据完成进度给出学习节奏建议
        2. 难度相关建议 - 针对高难度任务的特殊处理建议
        3. 效率建议 - 提高学习效率的方法
        4. 个性化建议 - 根据学习风格定制
        """
        suggestions = []
        completed_count = len(progress.get('completed_tasks', []))
        total_tasks = len(path['tasks'])
        
        # 1. 进度分析建议
        progress_ratio = completed_count / total_tasks if total_tasks > 0 else 0
        if progress_ratio == 0:
            suggestions.append("建议从基础任务开始，先掌握核心概念")
        elif progress_ratio < 0.3:
            suggestions.append("基础阶段，建议每天投入1-2小时巩固基础")
        elif progress_ratio < 0.7:
            suggestions.append("进阶阶段，建议每天投入2-3小时深入学习")
        else:
            suggestions.append("冲刺阶段，建议每天投入3-4小时完成剩余任务")
        
        # 2. 任务难度分析
        hard_tasks = [t for t in path['tasks'] if t.get('difficulty') == '困难' and t.get('status') != 'completed']
        if hard_tasks:
            suggestions.append(f"有{len(hard_tasks)}个高难度任务，建议拆分学习并寻求帮助")
        
        # 3. 学习效率建议
        avg_hours = sum(t.get('estimated_hours', 0) for t in path['tasks']) / total_tasks if total_tasks > 0 else 0
        if avg_hours > 30:
            suggestions.append("部分任务耗时较长，建议采用番茄工作法提高效率")
        
        # 4. 个性化建议
        learning_style = progress.get('learning_style', '')
        if learning_style == 'visual':
            suggestions.append("检测到您更适合视觉学习，已优先推荐视频教程")
        elif learning_style == 'reading':
            suggestions.append("检测到您更适合阅读学习，已优先推荐文档资料")
        
        path['ai_suggestions'] = suggestions[:5]  # 最多5条建议
        return path

    def adjust_path_with_feedback(self, path: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """根据用户反馈调整学习路径"""
        # 处理任务难度反馈
        for task_feedback in feedback.get('task_difficulty', []):
            for task in path['tasks']:
                if task['task_name'] == task_feedback['task_name']:
                    if task_feedback['too_hard']:
                        task['estimated_hours'] = min(int(task['estimated_hours'] * 1.2), 100)
                        task['difficulty'] = self._adjust_difficulty(task['difficulty'], 0.3)
        
        # 处理资源反馈
        for resource_feedback in feedback.get('resources', []):
            for task in path['tasks']:
                if task['task_name'] == resource_feedback['task_name']:
                    resources = json.loads(task['resources'])
                    if resource_feedback['resource'] not in resources:
                        resources.append(resource_feedback['resource'])
                    task['resources'] = json.dumps(resources[:5])  # 最多保留5个资源
        
        # 实时调整路径
        path = self._realtime_adjust(path, feedback.get('learning_style'))
        return path

    def _realtime_adjust(self, path: Dict[str, Any], learning_style: str = None) -> Dict[str, Any]:
        """实时调整学习路径"""
        if learning_style == 'visual':
            for task in path['tasks']:
                if 'resources' in task:
                    resources = json.loads(task['resources'])
                    resources = [r for r in resources if 'video' in r.lower() or 'youtube' in r.lower()]
                    if not resources:
                        resources.append('https://www.youtube.com/results?search_query=' + task['task_name'])
                    task['resources'] = json.dumps(resources)
        return path

    def generate_visualization_data(self, path: Dict[str, Any]) -> Dict[str, Any]:
        """生成可视化数据"""
        return {
            'progress': path.get('overall_progress', 0),
            'tasks': [
                {
                    'name': task['task_name'],
                    'status': task.get('status', 'not_started'),
                    'progress': task.get('progress', 0),
                    'difficulty': task.get('difficulty', 'medium')
                }
                for task in path['tasks']
            ],
            'timeline': {
                'estimated': path['estimated_duration'],
                'completed': sum(
                    1 for t in path['tasks'] 
                    if t.get('status') == 'completed'
                ) / len(path['tasks']) * path['estimated_duration']
            }
        }
