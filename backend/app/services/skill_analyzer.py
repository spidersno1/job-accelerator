from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.skill import Skill, SkillReport
from app.models.user import User
import json
from collections import defaultdict

class SkillAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.skill_weights = {
            "算法": 1.5,
            "数据结构": 1.5,
            "编程语言": 1.2,
            "框架": 1.0
        }

    def generate_skill_report(self, user_id: int) -> SkillReport:
        """生成技能分析报告"""
        skills = self.db.query(Skill).filter(Skill.user_id == user_id).all()
        
        # 计算加权技能分
        weighted_skills = []
        for s in skills:
            weight = self.skill_weights.get(s.skill_category, 1.0)
            weighted_skills.append((
                s.skill_name,
                s.proficiency_level * weight,
                s.skill_category
            ))
        
        report_data = {
            "summary": {
                "total_skills": len(skills),
                "top_skills": sorted(
                    weighted_skills,
                    key=lambda x: x[1], reverse=True)[:5],
                "skill_distribution": defaultdict(int)
            },
            "by_category": {},
            "details": [{
                "skill_name": s.skill_name,
                "category": s.skill_category,
                "level": s.proficiency_level,
                "weighted_level": s.proficiency_level * self.skill_weights.get(s.skill_category, 1.0),
                "source": s.source
            } for s in skills]
        }
        
        # 按分类统计
        for s in skills:
            if s.skill_category not in report_data["by_category"]:
                report_data["by_category"][s.skill_category] = []
            report_data["by_category"][s.skill_category].append({
                "skill_name": s.skill_name,
                "level": s.proficiency_level,
                "weighted_level": s.proficiency_level * self.skill_weights.get(s.skill_category, 1.0)
            })
            report_data["summary"]["skill_distribution"][s.skill_category] += 1
        
        report = SkillReport(
            user_id=user_id,
            report_data=json.dumps(report_data)
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        return report

    def save_leetcode_skills(self, user_id: int, leetcode_data: List[Dict]) -> List[Skill]:
        """保存LeetCode分析结果到技能数据库"""
        skills = []
        
        for skill_data in leetcode_data:
            category = skill_data.get('category', 'algorithm')
            name = skill_data.get('name', '')
            evidence = skill_data.get('evidence', {})
            
            # 更细致的熟练度计算
            if category == 'programming_language':
                # 基础分：解决问题数量
                base = evidence.get('problems_solved', 0) * 4
                # 难度加分：困难题额外权重
                difficulty_bonus = (
                    evidence.get('easy_solved', 0) * 1 +
                    evidence.get('medium_solved', 0) * 3 +
                    evidence.get('hard_solved', 0) * 6
                )
                # 代码质量分：平均运行时间和内存使用
                avg_runtime = min(evidence.get('avg_runtime_percentile', 50) / 50, 2.0)
                avg_memory = min(evidence.get('avg_memory_percentile', 50) / 50, 2.0)
                quality_bonus = (avg_runtime + avg_memory) * 5
                
                proficiency = min(base + difficulty_bonus + quality_bonus, 100)
            else:  # algorithm
                # 算法熟练度多维评估
                problem_solving = (
                    evidence.get('easy_solved', 0) * 1 +
                    evidence.get('medium_solved', 0) * 3 +
                    evidence.get('hard_solved', 0) * 5
                )
                # 考虑最优解比例
                optimal_solution_rate = min(evidence.get('optimal_solution_rate', 0.5), 1.0) * 20
                # 考虑解题速度
                speed_factor = min(evidence.get('avg_solving_speed_percentile', 50) / 50, 1.5)
                # 考虑通过率
                acceptance_rate = min(evidence.get('acceptance_rate', 1.0), 1.0)
                
                proficiency = min(
                    (problem_solving + optimal_solution_rate) * 
                    speed_factor * 
                    acceptance_rate, 
                    100
                )
            
            skill = Skill(
                user_id=user_id,
                skill_name=name,
                skill_category=category,
                proficiency_level=proficiency,
                source="leetcode",
                evidence=json.dumps(evidence)
            )
            skills.append(skill)
        
        return skills

    def match_job_skills(self, user_id: int, job_requirements: Dict) -> Dict:
        """匹配用户技能与岗位需求"""
        user_skills = self.db.query(Skill).filter(Skill.user_id == user_id).all()
        
        matched_skills = []
        missing_skills = []
        match_score = 0
        max_possible = 0
        skill_relations = {
            "Python": ["Django", "Flask"],
            "Java": ["Spring"],
            "JavaScript": ["React", "Vue"]
        }
        
        for req in job_requirements.get('skills', []):
            req_name = req['name']
            req_level = req.get('level', 50)
            req_weight = req.get('weight', 1.0)
            req_priority = req.get('priority', 1.0)  # 新增：技能优先级
            
            max_possible += req_level * req_weight * req_priority
            
            # 查找匹配技能（精确匹配+关联技能）
            matched = None
            related_matches = []
            
            for skill in user_skills:
                # 精确匹配
                if skill.skill_name.lower() == req_name.lower():
                    matched = skill
                    break
                # 关联技能匹配（如会Python的也部分匹配Django）
                if req_name in skill_relations.get(skill.skill_name, []):
                    related_matches.append((skill, 0.6))  # 关联技能匹配度为60%
            
            if matched:
                # 计算精确匹配度
                skill_level = matched.proficiency_level
                category_weight = self.skill_weights.get(matched.skill_category, 1.0)
                match_value = min(skill_level, req_level) * req_weight * category_weight * req_priority
                
                matched_skills.append({
                    'name': req_name,
                    'user_level': skill_level,
                    'required_level': req_level,
                    'match_value': match_value,
                    'match_type': 'exact'
                })
                match_score += match_value
            elif related_matches:
                # 使用关联技能中最高的匹配度
                best_related = max(related_matches, key=lambda x: x[0].proficiency_level * x[1])
                related_skill, relation_factor = best_related
                
                skill_level = related_skill.proficiency_level * relation_factor
                category_weight = self.skill_weights.get(related_skill.skill_category, 1.0)
                match_value = min(skill_level, req_level) * req_weight * category_weight * req_priority
                
                matched_skills.append({
                    'name': f"{req_name} (via {related_skill.skill_name})",
                    'user_level': skill_level,
                    'required_level': req_level,
                    'match_value': match_value,
                    'match_type': 'related'
                })
                match_score += match_value
            else:
                missing_skills.append({
                    'name': req_name,
                    'required_level': req_level,
                    'priority': req_priority
                })
        
        # 计算匹配百分比（考虑岗位紧急程度）
        job_urgency = job_requirements.get('urgency_factor', 1.0)
        match_percent = (match_score / max_possible * 100 * job_urgency) if max_possible > 0 else 0
        
        return {
            'match_percentage': round(min(match_percent, 100), 2),
            'matched_skills': sorted(matched_skills, key=lambda x: -x['match_value']),
            'missing_skills': sorted(missing_skills, key=lambda x: -x['priority']),
            'total_score': match_score,
            'skill_gap_analysis': self._generate_skill_gap_analysis(missing_skills)
        }

    def _generate_skill_gap_analysis(self, missing_skills: List[Dict]) -> List[Dict]:
        """生成技能缺口分析"""
        gap_analysis = []
        learning_resources = {
            "Python": "https://learnpython.com",
            "Java": "https://learnjava.com",
            "React": "https://reactjs.org/docs"
        }
        
        for skill in missing_skills:
            gap_analysis.append({
                'skill_name': skill['name'],
                'priority': skill['priority'],
                'learning_path': f"预计需要{skill['required_level']//20 + 1}周掌握",
                'resources': learning_resources.get(skill['name'], "通用学习资源")
            })
        
        return gap_analysis
