from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job, JobMatch
from app.models.schemas import Job as JobSchema, JobMatch as JobMatchSchema
from app.models.schemas import JobCreate, JobMatchCreate, JobMatchUpdate
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.skill import Skill
from app.services.job_matcher import JobMatcher
from app.services.job_crawler import JobCrawler
from app.services.job_crawler_enhanced import JobCrawlerEnhanced, JobInfo, convert_job_info_to_dict
from typing import List
import json
from datetime import datetime

router = APIRouter()

def get_current_user_id(current_user: User = Depends(get_current_active_user)) -> int:
    """获取当前用户ID"""
    return current_user.id

@router.get("/", response_model=List[JobSchema])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    location: str = None,
    job_type: str = None,
    experience_level: str = None,
    db: Session = Depends(get_db)
):
    """获取岗位列表"""
    query = db.query(Job).filter(Job.is_active == True)
    
    if location:
        query = query.filter(Job.location.contains(location))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobSchema)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """获取特定岗位"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    return job

@router.get("/matches", response_model=List[JobMatchSchema])
def get_job_matches(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取用户的岗位匹配"""
    matches = db.query(JobMatch).filter(JobMatch.user_id == current_user_id).all()
    return matches

@router.post("/matches/{job_id}", response_model=JobMatchSchema)
def create_job_match(
    job_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建岗位匹配"""
    # 检查岗位是否存在
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位不存在"
        )
    
    # 检查是否已经匹配过
    existing_match = db.query(JobMatch).filter(
        JobMatch.user_id == current_user_id,
        JobMatch.job_id == job_id
    ).first()
    
    if existing_match:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已经匹配过该岗位"
        )
    
    # 进行岗位匹配分析
    matcher = JobMatcher()
    match_result = matcher.analyze_match(current_user_id, job_id, db)
    
    # 创建匹配记录
    job_match = JobMatch(
        user_id=current_user_id,
        job_id=job_id,
        match_score=match_result["match_score"],
        skill_match=match_result["skill_match"],
        gap_analysis=match_result["gap_analysis"]
    )
    
    db.add(job_match)
    db.commit()
    db.refresh(job_match)
    return job_match

@router.put("/matches/{match_id}", response_model=JobMatchSchema)
def update_job_match(
    match_id: int,
    match_update: JobMatchUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """更新岗位匹配状态"""
    job_match = db.query(JobMatch).filter(
        JobMatch.id == match_id,
        JobMatch.user_id == current_user_id
    ).first()
    
    if not job_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="岗位匹配不存在"
        )
    
    update_data = match_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job_match, field, value)
    
    db.commit()
    db.refresh(job_match)
    return job_match

@router.post("/search", response_model=List[JobSchema])
def search_jobs(
    keyword: str,
    location: str = None,
    job_type: str = None,
    experience_level: str = None,
    db: Session = Depends(get_db)
):
    """搜索岗位"""
    query = db.query(Job).filter(Job.is_active == True)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            (Job.title.contains(keyword)) |
            (Job.company.contains(keyword)) |
            (Job.job_description.contains(keyword))
        )
    
    if location:
        query = query.filter(Job.location.contains(location))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    
    jobs = query.all()
    return jobs

@router.post("/recommend", response_model=List[JobMatchSchema])
def recommend_jobs(
    current_user_id: int = Depends(get_current_user_id),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """AI推荐岗位"""
    matcher = JobMatcher()
    recommendations = matcher.recommend_jobs(current_user_id, limit, db)
    
    # 保存推荐结果
    for rec in recommendations:
        job_match = JobMatch(
            user_id=current_user_id,
            job_id=rec["job_id"],
            match_score=rec["match_score"],
            skill_match=rec["skill_match"],
            gap_analysis=rec["gap_analysis"]
        )
        db.add(job_match)
    
    db.commit()
    return recommendations

@router.post("/crawl", response_model=dict)
async def crawl_jobs(
    keywords: List[str],
    locations: List[str] = None,
    max_jobs_per_site: int = 30,
    db: Session = Depends(get_db)
):
    """爬取岗位信息 - 使用增强版爬虫"""
    try:
        async with JobCrawlerEnhanced() as crawler:
            jobs_data = await crawler.crawl_jobs(
                keywords=keywords, 
                locations=locations or ['北京', '上海', '广州', '深圳'],
                max_pages=3,
                max_jobs_per_site=max_jobs_per_site
            )
        
        # 保存到数据库
        saved_jobs = []
        for job_info in jobs_data:
            job_dict = convert_job_info_to_dict(job_info)
            
            # 检查是否已存在相同职位
            existing_job = db.query(Job).filter(
                Job.title == job_dict["title"],
                Job.company == job_dict["company"],
                Job.location == job_dict["location"]
            ).first()
            
            if not existing_job:
                job = Job(
                    title=job_dict["title"],
                    company=job_dict["company"],
                    location=job_dict["location"],
                    salary_range=job_dict["salary_range"],
                    job_description=job_dict["job_description"],
                    requirements=job_dict["requirements"],
                    job_type=job_dict["job_type"],
                    experience_level=job_dict["experience_level"],
                    source_url=job_dict["source_url"],
                    skills_required=json.dumps(job_dict["skills_required"]),
                    posted_date=job_dict["posted_date"],
                    source_site=job_dict["source_site"]
                )
                db.add(job)
                saved_jobs.append(job_dict)
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"成功爬取 {len(jobs_data)} 个岗位，保存 {len(saved_jobs)} 个新岗位",
            "total_crawled": len(jobs_data),
            "newly_saved": len(saved_jobs),
            "keywords": keywords,
            "locations": locations or ['北京', '上海', '广州', '深圳'],
            "crawl_time": datetime.now().isoformat()
        }
        
    except Exception as e:
                 raise HTTPException(
             status_code=500,
             detail=f"爬取岗位信息失败: {str(e)}"
         )

@router.post("/crawl-by-skills", response_model=dict)
async def crawl_jobs_by_user_skills(
    current_user: User = Depends(get_current_active_user),
    locations: List[str] = None,
    max_jobs_per_site: int = 20,
    db: Session = Depends(get_db)
):
    """根据用户技能自动爬取相关职位"""
    try:
        # 获取用户的技能
        user_skills = db.query(Skill).filter(Skill.user_id == current_user.id).all()
        
        if not user_skills:
            return {
                "status": "error",
                "message": "用户暂无技能数据，请先进行技能分析",
                "total_crawled": 0,
                "newly_saved": 0
            }
        
        # 提取技能关键词用于搜索
        skill_keywords = []
        for skill in user_skills:
            if skill.proficiency_level >= 60:  # 只搜索熟练度较高的技能
                skill_keywords.append(skill.name)
        
        # 限制搜索关键词数量，避免过多请求
        skill_keywords = skill_keywords[:5]
        
        if not skill_keywords:
            return {
                "status": "error", 
                "message": "用户暂无熟练度较高的技能，请提升技能水平后再试",
                "total_crawled": 0,
                "newly_saved": 0
            }
        
        # 使用增强版爬虫根据技能搜索职位
        async with JobCrawlerEnhanced() as crawler:
            jobs_data = await crawler.crawl_jobs(
                keywords=skill_keywords,
                locations=locations or ['北京', '上海', '广州', '深圳'],
                max_pages=2,  # 减少页数，提高效率
                max_jobs_per_site=max_jobs_per_site
            )
        
        # 保存到数据库
        saved_jobs = []
        for job_info in jobs_data:
            job_dict = convert_job_info_to_dict(job_info)
            
            # 检查是否已存在相同职位
            existing_job = db.query(Job).filter(
                Job.title == job_dict["title"],
                Job.company == job_dict["company"],
                Job.location == job_dict["location"]
            ).first()
            
            if not existing_job:
                job = Job(
                    title=job_dict["title"],
                    company=job_dict["company"],
                    location=job_dict["location"],
                    salary_range=job_dict["salary_range"],
                    job_description=job_dict["job_description"],
                    requirements=job_dict["requirements"],
                    job_type=job_dict["job_type"],
                    experience_level=job_dict["experience_level"],
                    source_url=job_dict["source_url"],
                    skills_required=json.dumps(job_dict["skills_required"]),
                    posted_date=job_dict["posted_date"],
                    source_site=job_dict["source_site"]
                )
                db.add(job)
                saved_jobs.append(job_dict)
        
        db.commit()
        
        # 为新职位创建匹配分析
        matcher = JobMatcher()
        match_results = []
        
        for job_dict in saved_jobs[:10]:  # 限制匹配分析数量
            # 找到对应的数据库记录
            job_record = db.query(Job).filter(
                Job.title == job_dict["title"],
                Job.company == job_dict["company"],
                Job.location == job_dict["location"]
            ).first()
            
            if job_record:
                try:
                    match_result = matcher.match_jobs_simple(current_user.id, [job_record.id], db)
                    if match_result:
                        match_results.extend(match_result)
                except Exception as e:
                    print(f"匹配分析失败: {e}")
        
        return {
            "status": "success",
            "message": f"基于用户技能爬取完成：{', '.join(skill_keywords)}",
            "total_crawled": len(jobs_data),
            "newly_saved": len(saved_jobs),
            "user_skills": skill_keywords,
            "locations": locations or ['北京', '上海', '广州', '深圳'],
            "match_results": match_results[:5],  # 返回前5个匹配结果
            "crawl_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"基于技能爬取职位失败: {str(e)}"
        )

@router.post("/match-simple", response_model=List[dict])
def match_jobs_simple(
    current_user_id: int = Depends(get_current_user_id),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """使用简化算法快速匹配职位"""
    from app.models.skill import Skill
    
    # 获取用户技能
    user_skills = db.query(Skill).filter(Skill.user_id == current_user_id).all()
    user_skills_data = [
        {"name": skill.skill_name, "level": skill.proficiency_level} 
        for skill in user_skills
    ]
    
    # 获取所有活跃职位
    jobs = db.query(Job).filter(Job.is_active == True).limit(100).all()
    job_listings = [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "requirements": job.requirements
        } for job in jobs
    ]
    
    # 使用简化匹配算法
    matcher = JobMatcher()
    matched_jobs = matcher.match_jobs_simple(user_skills_data, job_listings)
    
    return matched_jobs[:limit]
