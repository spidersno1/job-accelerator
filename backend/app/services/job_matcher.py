from typing import List, Dict, Any
from sqlalchemy.orm import Session
import json

class JobMatcher:
    def __init__(self):
        self.skill_weights = {
            "programming_language": 0.3,
            "framework_tool": 0.25,
            "algorithm": 0.2,
            "data_structure": 0.15,
            "project_type": 0.1
        }
    
    def analyze_match(self, user_id: int, job_id: int, db: Session) -> Dict[str, Any]:
        """分析用户与岗位的匹配度"""
        from app.models.user import User
        from app.models.skill import Skill
        from app.models.job import Job
        
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"match_score": 0, "skill_match": "{}", "gap_analysis": "{}"}
        
        # 获取岗位信息
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"match_score": 0, "skill_match": "{}", "gap_analysis": "{}"}
        
        # 获取用户技能
        user_skills = db.query(Skill).filter(Skill.user_id == user_id).all()
        
        # 分析岗位要求
        job_requirements = self._parse_job_requirements(job.requirements)
        
        # 计算匹配度
        match_result = self._calculate_match_score(user_skills, job_requirements)
        
        return match_result
    
    def recommend_jobs(self, user_id: int, limit: int, db: Session) -> List[Dict[str, Any]]:
        """推荐岗位"""
        from app.models.job import Job
        from app.models.skill import Skill
        
        # 获取用户技能
        user_skills = db.query(Skill).filter(Skill.user_id == user_id).all()
        
        # 获取所有活跃岗位
        jobs = db.query(Job).filter(Job.is_active == True).limit(100).all()
        
        # 计算每个岗位的匹配度
        job_scores = []
        for job in jobs:
            job_requirements = self._parse_job_requirements(job.requirements)
            match_score = self._calculate_match_score(user_skills, job_requirements)["match_score"]
            
            job_scores.append({
                "job_id": job.id,
                "match_score": match_score,
                "skill_match": "{}",
                "gap_analysis": "{}"
            })
        
        # 按匹配度排序
        job_scores.sort(key=lambda x: x["match_score"], reverse=True)
        
        return job_scores[:limit]
    
    def match_jobs_simple(self, user_skills: list, job_listings: list) -> list:
        """
        简化的职位匹配算法，直接基于技能名称和水平进行匹配
        :param user_skills: 用户技能列表 [{"name": "Python", "level": 8}, ...]
        :param job_listings: 职位列表 [{"id": 1, "title": "后端开发", "required_skills": [...]}, ...]
        :return: 排序后的匹配结果
        """
        matched_jobs = []
        
        # 将用户技能转换为字典便于快速查找
        user_skill_dict = {skill["name"].lower(): skill["level"] for skill in user_skills}
        
        for job in job_listings:
            total_score = 0.0
            total_possible = 0.0
            skills_matched = []
            skills_missing = []
            
            # 解析职位要求（如果requirements是JSON字符串）
            required_skills = job.get("required_skills", [])
            if isinstance(job.get("requirements"), str):
                try:
                    requirements_data = json.loads(job["requirements"])
                    if isinstance(requirements_data, dict):
                        # 如果是分类格式，转换为扁平列表
                        required_skills = []
                        for category, skills in requirements_data.items():
                            if isinstance(skills, list):
                                for skill in skills:
                                    required_skills.append({
                                        "name": skill,
                                        "required_level": 5,  # 默认要求水平
                                        "weight": self.skill_weights.get(category, 0.1)
                                    })
                    elif isinstance(requirements_data, list):
                        required_skills = requirements_data
                except:
                    pass
            
            for req_skill in required_skills:
                if isinstance(req_skill, str):
                    # 如果是字符串，转换为标准格式
                    skill_name = req_skill
                    required_level = 5
                    weight = 1.0
                else:
                    skill_name = req_skill.get("name", "")
                    required_level = req_skill.get("required_level", 5)
                    weight = req_skill.get("weight", 1.0)
                
                # 获取用户该技能水平（若无此技能则为0）
                user_level = user_skill_dict.get(skill_name.lower(), 0)
                
                # 判断是否匹配（用户水平达到要求的60%以上认为匹配）
                if user_level >= required_level * 0.6:
                    skills_matched.append(skill_name)
                    # 计算技能匹配度（用户水平/要求水平，上限1.0）
                    skill_match = min(user_level / required_level, 1.0) if required_level > 0 else 0
                else:
                    skills_missing.append(skill_name)
                    skill_match = 0
                
                # 加权计算
                total_score += skill_match * weight
                total_possible += weight
            
            # 计算总体匹配度百分比
            if total_possible > 0:
                match_percentage = (total_score / total_possible) * 100
            else:
                match_percentage = 0.0
                
            matched_jobs.append({
                "job_id": job["id"],
                "title": job["title"],
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "salary_range": job.get("salary_range", ""),
                "experience_level": job.get("experience_level", ""),
                "job_type": job.get("job_type", ""),
                "match_percentage": round(match_percentage, 2),
                "skills_matched": skills_matched,
                "skills_missing": skills_missing,
                "source_url": job.get("source_url", ""),
                "source_site": job.get("source_site", ""),
                "posted_date": job.get("posted_date", "")
            })
        
        # 按匹配度降序排序
        return sorted(matched_jobs, key=lambda x: x["match_percentage"], reverse=True)
    
    def _parse_job_requirements(self, requirements: str) -> Dict[str, List[str]]:
        """解析岗位要求"""
        if not requirements:
            return {}
        
        try:
            req_data = json.loads(requirements)
            return req_data
        except:
            # 如果解析失败，返回空字典
            return {}
    
    def _calculate_match_score(self, user_skills: List, job_requirements: Dict[str, List[str]]) -> Dict[str, Any]:
        """计算匹配度分数"""
        if not job_requirements:
            return {
                "match_score": 50,  # 默认中等匹配度
                "skill_match": "{}",
                "gap_analysis": "{}"
            }
        
        skill_match = {}
        gap_analysis = {}
        total_score = 0
        total_weight = 0
        
        # 分析每个技能类别
        for category, required_skills in job_requirements.items():
            if not isinstance(required_skills, list):
                continue
            
            # 找到用户在该类别的技能
            user_category_skills = [s for s in user_skills if s.skill_category == category]
            
            # 计算该类别的匹配度
            category_score = 0
            matched_skills = []
            missing_skills = []
            
            for required_skill in required_skills:
                # 检查用户是否有匹配的技能
                matched = False
                for user_skill in user_category_skills:
                    if required_skill.lower() in user_skill.skill_name.lower():
                        category_score += user_skill.proficiency_level
                        matched_skills.append({
                            "required": required_skill,
                            "user_skill": user_skill.skill_name,
                            "proficiency": user_skill.proficiency_level
                        })
                        matched = True
                        break
                
                if not matched:
                    missing_skills.append(required_skill)
            
            # 计算该类别的平均分数
            if matched_skills:
                category_score = category_score / len(matched_skills)
            
            # 应用权重
            weight = self.skill_weights.get(category, 0.1)
            total_score += category_score * weight
            total_weight += weight
            
            # 记录匹配结果
            skill_match[category] = {
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "category_score": category_score
            }
            
            if missing_skills:
                gap_analysis[category] = missing_skills
        
        # 计算总体匹配度
        if total_weight > 0:
            overall_score = min(100, (total_score / total_weight) * 100)
        else:
            overall_score = 0
        
        return {
            "match_score": round(overall_score, 2),
            "skill_match": json.dumps(skill_match),
            "gap_analysis": json.dumps(gap_analysis)
        } 