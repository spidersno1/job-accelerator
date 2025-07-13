from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
import base64

from app.database import get_db
from app.models.skill import Skill, SkillReport
from app.models.schemas import SkillBase, GitHubAnalysisRequest, LeetCodeAnalysisRequest, SkillReport as SkillReportSchema
from app.services.skill_analyzer import SkillAnalyzer
from app.services.code_analyzer import CodeAnalyzer
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.leetcode_service import LeetCodeService

router = APIRouter(prefix="", tags=["技能分析"])

# 原有的分析GitHub技能的端点
@router.post("/analyze-github", response_model=dict)
async def analyze_github_skills(
    request: GitHubAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析GitHub数据并提取技能"""
    try:
        analyzer = SkillAnalyzer(db)
        skills = analyzer.analyze_github_skills(current_user.id, {"token": request.token})
        
        # 保存到数据库
        db.add_all(skills)
        db.commit()
        
        # 返回更详细的分析结果
        from app.services.github_service import GitHubService
        github_service = GitHubService()
        token = request.token
        analysis = await github_service.analyze_user_skills(token=token)
        
        # 获取用户名
        username = await github_service.get_username(token)
        
        return {
            "status": "success",
            "skills": skills,
            "analysis": analysis,
            "summary": {
                "total_repos": analysis.get("total_repos", 0),
                "top_languages": list(analysis.get("languages", {}).keys())[:5],
                "activity_score": analysis.get("activity", {}).get("activity_score", 0)
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"GitHub分析失败: {str(e)}"
            }
        )

# 新增的代码分析端点
@router.post("/analyze-code", response_model=dict)
async def analyze_code(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    analysis_type: str = Form(...),  # 'file', 'text', 'image'
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析代码并提取技能 - 支持文件上传、文本输入和图片分析"""
    try:
        code_analyzer = CodeAnalyzer()
        analysis_results = []
        
        if analysis_type == "file" and file:
            # 文件分析
            file_content = await file.read()
            result = code_analyzer.analyze_file(file.filename, file_content)
            analysis_results.append(result)
            
        elif analysis_type == "text" and text_content:
            # 文本分析
            result = code_analyzer.analyze_text(text_content)
            analysis_results.append(result)
            
        elif analysis_type == "image" and file:
            # 图片分析
            file_content = await file.read()
            result = code_analyzer.analyze_image(file_content)
            analysis_results.append(result)
            
        else:
            raise HTTPException(
                status_code=400,
                detail="请提供有效的分析数据"
            )
        
        # 生成综合技能报告
        skill_report = code_analyzer.generate_skill_report(analysis_results)
        
        # 保存分析结果到数据库
        await _save_code_analysis_to_db(db, current_user.id, skill_report, analysis_results)
        
        return {
            "status": "success",
            "analysis_results": analysis_results,
            "skill_report": skill_report,
            "message": "代码分析完成"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"代码分析失败: {str(e)}"
            }
        )

@router.post("/analyze-multiple-files", response_model=dict)
async def analyze_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """批量分析多个文件"""
    try:
        code_analyzer = CodeAnalyzer()
        analysis_results = []
        
        for file in files:
            file_content = await file.read()
            result = code_analyzer.analyze_file(file.filename, file_content)
            analysis_results.append(result)
        
        # 生成综合技能报告
        skill_report = code_analyzer.generate_skill_report(analysis_results)
        
        # 保存分析结果到数据库
        await _save_code_analysis_to_db(db, current_user.id, skill_report, analysis_results)
        
        return {
            "status": "success",
            "total_files": len(files),
            "analysis_results": analysis_results,
            "skill_report": skill_report,
            "message": f"成功分析 {len(files)} 个文件"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"批量文件分析失败: {str(e)}"
            }
        )

async def _save_code_analysis_to_db(db: Session, user_id: int, skill_report: dict, analysis_results: list):
    """保存代码分析结果到数据库"""
    try:
        # 保存技能数据
        for skill_data in skill_report.get('skills', []):
            skill = Skill(
                user_id=user_id,
                skill_name=skill_data['name'],
                skill_category=skill_data.get('category', 'Programming'),
                proficiency_level=min(int(skill_data['confidence'] * 100), 100),
                source='code_analysis',
                evidence=json.dumps({
                    'confidence': skill_data['confidence'],
                    'occurrences': skill_data['occurrences'],
                    'analysis_timestamp': datetime.now().isoformat()
                })
            )
            db.add(skill)
        
        # 保存框架技能数据
        for framework_data in skill_report.get('frameworks', []):
            skill = Skill(
                user_id=user_id,
                skill_name=framework_data['name'],
                skill_category=framework_data.get('category', 'Framework'),
                proficiency_level=min(int(framework_data['confidence'] * 100), 100),
                source='code_analysis',
                evidence=json.dumps({
                    'confidence': framework_data['confidence'],
                    'occurrences': framework_data['occurrences'],
                    'analysis_timestamp': datetime.now().isoformat()
                })
            )
            db.add(skill)
        
        # 保存技能报告
        report_data_with_type = {
            'report_type': 'code_analysis',
            'skill_report': skill_report,
            'analysis_results': analysis_results,
            'created_at': datetime.now().isoformat()
        }
        skill_report_obj = SkillReport(
            user_id=user_id,
            report_data=json.dumps(report_data_with_type)
        )
        db.add(skill_report_obj)
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e

# 原有的其他端点保持不变
@router.post("/analyze-leetcode", response_model=dict)
async def analyze_leetcode_skills(
    request: LeetCodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """分析LeetCode数据并提取技能"""
    try:
        leetcode_service = LeetCodeService()
        analysis = leetcode_service.analyze_leetcode_data(request.data)
        
        # 保存技能到数据库
        skills = []
        for skill_name, skill_data in analysis.get("skills", {}).items():
            skill = Skill(
                user_id=current_user.id,
                name=skill_name,
                category="Algorithm",
                proficiency_level=skill_data.get("level", 50),
                source="leetcode",
                evidence=json.dumps(skill_data)
            )
            skills.append(skill)
            db.add(skill)
        
        # 保存技能报告
        skill_report = SkillReport(
            user_id=current_user.id,
            report_type="leetcode",
            report_data=json.dumps(analysis),
            created_at=datetime.now()
        )
        db.add(skill_report)
        
        db.commit()
        
        return {
            "status": "success",
            "skills": skills,
            "analysis": analysis,
            "summary": {
                "total_problems": analysis.get("total_problems", 0),
                "difficulty_distribution": analysis.get("difficulty_stats", {}),
                "top_topics": analysis.get("top_topics", [])
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"LeetCode分析失败: {str(e)}"
            }
        )

# 新增的LeetCode综合分析端点
@router.post("/analyze-leetcode-comprehensive", response_model=dict)
async def analyze_leetcode_comprehensive(
    request: LeetCodeAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """LeetCode综合分析 - 商业级功能"""
    try:
        leetcode_service = LeetCodeService()
        
        # 获取综合分析结果
        analysis_result = await leetcode_service.get_comprehensive_analysis(request.username_or_url)
        
        # 保存技能到数据库
        skills = []
        
        # 保存编程语言技能
        for lang, data in analysis_result.skill_analysis.get("programming_languages", {}).items():
            skill = Skill(
                user_id=current_user.id,
                name=f"{lang}编程",
                category="programming_language",
                proficiency_level=int(data.get("proficiency_score", 0)),
                source="leetcode_comprehensive",
                evidence=json.dumps({
                    "problems_solved": data.get("problems_solved", 0),
                    "usage_percentage": data.get("usage_percentage", 0),
                    "level": data.get("level", "")
                })
            )
            skills.append(skill)
            db.add(skill)
        
        # 保存算法技能
        for algo, data in analysis_result.skill_analysis.get("algorithms", {}).items():
            skill = Skill(
                user_id=current_user.id,
                name=algo.replace("_", " ").title(),
                category="algorithm",
                proficiency_level=int(data.get("skill_score", 0)),
                source="leetcode_comprehensive",
                evidence=json.dumps({
                    "solved_count": data.get("solved_count", 0),
                    "accuracy_rate": data.get("accuracy_rate", 0),
                    "level": data.get("level", "")
                })
            )
            skills.append(skill)
            db.add(skill)
        
        # 保存数据结构技能
        for ds, data in analysis_result.skill_analysis.get("data_structures", {}).items():
            skill = Skill(
                user_id=current_user.id,
                name=ds,
                category="data_structure",
                proficiency_level=int(data.get("proficiency_score", 0)),
                source="leetcode_comprehensive",
                evidence=json.dumps({
                    "estimated_usage": data.get("estimated_usage", 0),
                    "confidence": data.get("confidence", ""),
                    "level": data.get("level", "")
                })
            )
            skills.append(skill)
            db.add(skill)
        
        # 保存综合技能报告
        skill_report = SkillReport(
            user_id=current_user.id,
            report_type="leetcode_comprehensive",
            report_data=json.dumps({
                "user_profile": analysis_result.user_profile,
                "skill_analysis": analysis_result.skill_analysis,
                "performance_metrics": analysis_result.performance_metrics,
                "learning_recommendations": analysis_result.learning_recommendations,
                "competitive_ranking": analysis_result.competitive_ranking,
                "problem_solving_patterns": analysis_result.problem_solving_patterns
            }),
            created_at=datetime.now()
        )
        db.add(skill_report)
        
        db.commit()
        
        return {
            "status": "success",
            "user_profile": analysis_result.user_profile,
            "skill_analysis": analysis_result.skill_analysis,
            "performance_metrics": analysis_result.performance_metrics,
            "learning_recommendations": analysis_result.learning_recommendations,
            "competitive_ranking": analysis_result.competitive_ranking,
            "problem_solving_patterns": analysis_result.problem_solving_patterns,
            "skills_saved": len(skills),
            "message": "LeetCode综合分析完成"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"LeetCode comprehensive analysis failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": f"LeetCode综合分析失败: {str(e)}"
            }
        )

@router.get("/analyze", response_model=dict)
def analyze_skills(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的综合技能分析"""
    try:
        # 获取用户的所有技能
        skills = db.query(Skill).filter(Skill.user_id == current_user.id).all()
        
        if not skills:
            return {
                "status": "error",
                "message": "未找到技能数据，请先进行技能分析"
            }
        
        # 按类别分组技能
        skills_by_category = {}
        for skill in skills:
            category = skill.skill_category or "Other"
            if category not in skills_by_category:
                skills_by_category[category] = []
            
            skills_by_category[category].append({
                "name": skill.skill_name,
                "proficiency_level": skill.proficiency_level,
                "source": skill.source,
                "evidence": json.loads(skill.evidence) if skill.evidence else {},
                "created_at": skill.created_at.isoformat() if skill.created_at else None
            })
        
        # 计算统计信息
        total_skills = len(skills)
        avg_proficiency = sum(skill.proficiency_level for skill in skills) / total_skills if total_skills > 0 else 0
        
        # 找出最强技能
        top_skills = sorted(skills, key=lambda x: x.proficiency_level, reverse=True)[:5]
        
        # 找出需要改进的技能
        improvement_skills = sorted(skills, key=lambda x: x.proficiency_level)[:3]
        
        # 生成学习建议
        learning_recommendations = []
        for skill in improvement_skills:
            learning_recommendations.append({
                "skill": skill.skill_name,
                "current_level": skill.proficiency_level,
                "suggestion": f"提升 {skill.skill_name} 技能水平",
                "resources": ["官方文档", "在线教程", "实践项目"]
            })
        
        return {
            "status": "success",
            "overview": {
                "total_skills": total_skills,
                "average_proficiency": round(avg_proficiency, 1),
                "categories": list(skills_by_category.keys()),
                "top_skills": [{"name": skill.skill_name, "level": skill.proficiency_level} for skill in top_skills],
                "improvement_areas": [{"name": skill.skill_name, "level": skill.proficiency_level} for skill in improvement_skills]
            },
            "details": {
                "skills_by_category": skills_by_category,
                "skill_distribution": {
                    "beginner": len([s for s in skills if s.proficiency_level < 40]),
                    "intermediate": len([s for s in skills if 40 <= s.proficiency_level < 70]),
                    "advanced": len([s for s in skills if s.proficiency_level >= 70])
                }
            },
            "recommendations": {
                "learning_suggestions": learning_recommendations,
                "skill_gaps": [skill.skill_name for skill in improvement_skills],
                "next_steps": ["专注提升核心技能", "学习相关技术栈", "参与实际项目"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"技能分析失败: {str(e)}"
            }
        )

@router.get("/test-analyze", response_model=dict)
def test_analyze_skills(db: Session = Depends(get_db)):
    """测试技能分析功能（无需认证）"""
    try:
        # 创建测试数据
        test_skills = [
            {"skill_name": "Python", "skill_category": "Programming", "proficiency_level": 85, "source": "test"},
            {"skill_name": "JavaScript", "skill_category": "Programming", "proficiency_level": 75, "source": "test"},
            {"skill_name": "React", "skill_category": "Framework", "proficiency_level": 70, "source": "test"},
            {"skill_name": "Django", "skill_category": "Framework", "proficiency_level": 80, "source": "test"},
            {"skill_name": "MySQL", "skill_category": "Database", "proficiency_level": 65, "source": "test"},
        ]
        
        # 按类别分组
        skills_by_category = {}
        for skill in test_skills:
            category = skill["skill_category"]
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill)
        
        # 计算统计信息
        total_skills = len(test_skills)
        avg_proficiency = sum(skill["proficiency_level"] for skill in test_skills) / total_skills
        
        # 找出最强技能
        top_skills = sorted(test_skills, key=lambda x: x["proficiency_level"], reverse=True)[:3]
        
        # 找出需要改进的技能
        improvement_skills = sorted(test_skills, key=lambda x: x["proficiency_level"])[:2]
        
        return {
            "status": "success",
            "message": "这是测试数据",
            "overview": {
                "total_skills": total_skills,
                "average_proficiency": round(avg_proficiency, 1),
                "categories": list(skills_by_category.keys()),
                "top_skills": [{"name": skill["name"], "level": skill["proficiency_level"]} for skill in top_skills],
                "improvement_areas": [{"name": skill["name"], "level": skill["proficiency_level"]} for skill in improvement_skills]
            },
            "details": {
                "skills_by_category": skills_by_category,
                "skill_distribution": {
                    "beginner": len([s for s in test_skills if s["proficiency_level"] < 40]),
                    "intermediate": len([s for s in test_skills if 40 <= s["proficiency_level"] < 70]),
                    "advanced": len([s for s in test_skills if s["proficiency_level"] >= 70])
                }
            },
            "recommendations": {
                "learning_suggestions": [
                    {"skill": skill["name"], "current_level": skill["proficiency_level"], "suggestion": f"提升 {skill['name']} 技能水平"}
                    for skill in improvement_skills
                ],
                "skill_gaps": [skill["name"] for skill in improvement_skills],
                "next_steps": ["专注提升核心技能", "学习相关技术栈", "参与实际项目"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"测试分析失败: {str(e)}"
            }
        )

@router.get("/reports", response_model=List[dict])
def get_skill_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的技能报告列表"""
    try:
        reports = db.query(SkillReport).filter(SkillReport.user_id == current_user.id).all()
        
        result = []
        for report in reports:
            report_dict = {
                "id": report.id,
                "report_type": report.report_type,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "report_data": json.loads(report.report_data) if report.report_data else {}
            }
            result.append(report_dict)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取技能报告失败: {str(e)}"
        )

@router.get("/", response_model=List[dict])
def get_skills(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的技能列表"""
    try:
        skills = db.query(Skill).filter(Skill.user_id == current_user.id).all()
        
        result = []
        for skill in skills:
            skill_dict = {
                "id": skill.id,
                "name": skill.name,
                "category": skill.category,
                "proficiency_level": skill.proficiency_level,
                "source": skill.source,
                "evidence": json.loads(skill.evidence) if skill.evidence else {},
                "created_at": skill.created_at.isoformat() if skill.created_at else None
            }
            result.append(skill_dict)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取技能列表失败: {str(e)}"
        )
