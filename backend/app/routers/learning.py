from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from app.database import get_db
from app.models.learning import LearningPath, LearningTask
from app.models.user import User
from app.core.security import get_current_active_user
from app.services.learning_path_enhanced import LearningPathEnhanced

router = APIRouter(prefix="", tags=["学习路径"])

@router.post("/generate", response_model=dict)
def generate_learning_path(
    target_job_id: Optional[int] = None,
    target_skills: Optional[Dict[str, int]] = None,
    learning_style: str = "balanced",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """生成个性化学习路径"""
    try:
        learning_service = LearningPathEnhanced(db)
        
        # 生成学习路径
        learning_path = learning_service.generate_learning_path(
            user_id=current_user.id,
            target_job_id=target_job_id,
            target_skills=target_skills,
            learning_style=learning_style
        )
        
        return {
            "status": "success",
            "message": "学习路径生成成功",
            "learning_path": {
                "id": learning_path.id,
                "title": learning_path.title,
                "description": learning_path.description,
                "target_job": learning_path.target_job,
                "difficulty_level": learning_path.difficulty_level,
                "total_estimated_hours": learning_path.total_estimated_hours,
                "estimated_completion_weeks": learning_path.estimated_completion_weeks,
                "current_skills": learning_path.current_skills,
                "target_skills": learning_path.target_skills,
                "skill_gaps": learning_path.skill_gaps,
                "steps_count": len(learning_path.steps),
                "success_metrics": learning_path.success_metrics,
                "created_at": learning_path.created_at.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成学习路径失败: {str(e)}"
        )

@router.get("/", response_model=List[dict])
def get_learning_paths(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取用户的学习路径列表"""
    try:
        learning_service = LearningPathEnhanced(db)
        paths = learning_service.get_user_learning_paths(current_user.id)
        
        return paths
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取学习路径失败: {str(e)}"
        )

@router.get("/{path_id}", response_model=dict)
def get_learning_path_detail(
    path_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取学习路径详情"""
    try:
        learning_path = db.query(LearningPath).filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            raise HTTPException(
                status_code=404,
                detail="学习路径不存在"
            )
        
        # 获取关联的任务
        tasks = db.query(LearningTask).filter(
            LearningTask.learning_path_id == path_id
        ).all()
        
        # 计算进度
        total_progress = sum(task.progress for task in tasks)
        avg_progress = total_progress / len(tasks) if tasks else 0
        
        return {
            "id": learning_path.id,
            "title": learning_path.title,
            "description": learning_path.description,
            "target_job": learning_path.target_job,
            "difficulty_level": learning_path.difficulty_level,
            "estimated_hours": learning_path.estimated_hours,
            "estimated_weeks": learning_path.estimated_weeks,
            "progress": round(avg_progress, 1),
            "created_at": learning_path.created_at.isoformat() if learning_path.created_at else None,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "skill_target": task.skill_target,
                    "target_proficiency": task.target_proficiency,
                    "estimated_hours": task.estimated_hours,
                    "status": task.status,
                    "progress": task.progress,
                    "is_milestone": task.is_milestone,
                    "prerequisites": json.loads(task.prerequisites) if task.prerequisites else [],
                    "resources": json.loads(task.resources) if task.resources else [],
                    "practice_tasks": json.loads(task.practice_tasks) if task.practice_tasks else [],
                    "assessment_criteria": json.loads(task.assessment_criteria) if task.assessment_criteria else [],
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in tasks
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取学习路径详情失败: {str(e)}"
        )

@router.put("/tasks/{task_id}/progress", response_model=dict)
def update_task_progress(
    task_id: int,
    progress: int,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新任务进度"""
    try:
        # 验证任务是否属于当前用户
        task = db.query(LearningTask).join(LearningPath).filter(
            LearningTask.id == task_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail="任务不存在或无权限访问"
            )
        
        # 验证进度值
        if progress < 0 or progress > 100:
            raise HTTPException(
                status_code=400,
                detail="进度值必须在0-100之间"
            )
        
        learning_service = LearningPathEnhanced(db)
        success = learning_service.update_task_progress(task_id, progress, status)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="更新任务进度失败"
            )
        
        return {
            "status": "success",
            "message": "任务进度更新成功",
            "task_id": task_id,
            "progress": progress,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新任务进度失败: {str(e)}"
        )

@router.post("/generate-by-job", response_model=dict)
def generate_learning_path_by_job(
    job_id: int,
    learning_style: str = "balanced",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据目标职位生成学习路径"""
    try:
        learning_service = LearningPathEnhanced(db)
        
        # 生成基于职位的学习路径
        learning_path = learning_service.generate_learning_path(
            user_id=current_user.id,
            target_job_id=job_id,
            learning_style=learning_style
        )
        
        return {
            "status": "success",
            "message": "基于职位的学习路径生成成功",
            "learning_path": {
                "id": learning_path.id,
                "title": learning_path.title,
                "description": learning_path.description,
                "target_job": learning_path.target_job,
                "difficulty_level": learning_path.difficulty_level,
                "total_estimated_hours": learning_path.total_estimated_hours,
                "estimated_completion_weeks": learning_path.estimated_completion_weeks,
                "skill_gaps": learning_path.skill_gaps,
                "steps_count": len(learning_path.steps),
                "success_metrics": learning_path.success_metrics
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成基于职位的学习路径失败: {str(e)}"
        )

@router.post("/generate-by-skills", response_model=dict)
def generate_learning_path_by_skills(
    target_skills: Dict[str, int],
    learning_style: str = "balanced",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """根据目标技能生成学习路径"""
    try:
        # 验证技能数据
        if not target_skills:
            raise HTTPException(
                status_code=400,
                detail="目标技能不能为空"
            )
        
        # 验证技能水平值
        for skill, level in target_skills.items():
            if level < 0 or level > 100:
                raise HTTPException(
                    status_code=400,
                    detail=f"技能 {skill} 的水平值必须在0-100之间"
                )
        
        learning_service = LearningPathEnhanced(db)
        
        # 生成基于技能的学习路径
        learning_path = learning_service.generate_learning_path(
            user_id=current_user.id,
            target_skills=target_skills,
            learning_style=learning_style
        )
        
        return {
            "status": "success",
            "message": "基于技能的学习路径生成成功",
            "learning_path": {
                "id": learning_path.id,
                "title": learning_path.title,
                "description": learning_path.description,
                "target_job": learning_path.target_job,
                "difficulty_level": learning_path.difficulty_level,
                "total_estimated_hours": learning_path.total_estimated_hours,
                "estimated_completion_weeks": learning_path.estimated_completion_weeks,
                "current_skills": learning_path.current_skills,
                "target_skills": learning_path.target_skills,
                "skill_gaps": learning_path.skill_gaps,
                "steps_count": len(learning_path.steps),
                "success_metrics": learning_path.success_metrics
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成基于技能的学习路径失败: {str(e)}"
        )

@router.get("/progress/overview", response_model=dict)
def get_learning_progress_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取学习进度概览"""
    try:
        # 获取用户的所有学习路径
        learning_paths = db.query(LearningPath).filter(
            LearningPath.user_id == current_user.id
        ).all()
        
        if not learning_paths:
            return {
                "status": "success",
                "overview": {
                    "total_paths": 0,
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "in_progress_tasks": 0,
                    "total_hours": 0,
                    "completed_hours": 0,
                    "overall_progress": 0
                },
                "recent_activities": []
            }
        
        # 统计数据
        total_paths = len(learning_paths)
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        total_hours = 0
        completed_hours = 0
        recent_activities = []
        
        for path in learning_paths:
            total_hours += path.estimated_hours or 0
            
            tasks = db.query(LearningTask).filter(
                LearningTask.learning_path_id == path.id
            ).all()
            
            total_tasks += len(tasks)
            
            for task in tasks:
                if task.status == 'completed':
                    completed_tasks += 1
                    completed_hours += task.estimated_hours or 0
                elif task.status == 'in_progress':
                    in_progress_tasks += 1
                    completed_hours += (task.estimated_hours or 0) * (task.progress / 100)
                
                # 收集最近活动
                if task.updated_at:
                    recent_activities.append({
                        "type": "task_update",
                        "task_title": task.title,
                        "path_title": path.title,
                        "progress": task.progress,
                        "status": task.status,
                        "updated_at": task.updated_at.isoformat()
                    })
        
        # 按时间排序最近活动
        recent_activities.sort(key=lambda x: x["updated_at"], reverse=True)
        recent_activities = recent_activities[:10]  # 只返回最近10条
        
        overall_progress = (completed_hours / total_hours * 100) if total_hours > 0 else 0
        
        return {
            "status": "success",
            "overview": {
                "total_paths": total_paths,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "total_hours": total_hours,
                "completed_hours": round(completed_hours, 1),
                "overall_progress": round(overall_progress, 1)
            },
            "recent_activities": recent_activities
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取学习进度概览失败: {str(e)}"
        )

@router.delete("/{path_id}", response_model=dict)
def delete_learning_path(
    path_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除学习路径"""
    try:
        # 验证学习路径是否属于当前用户
        learning_path = db.query(LearningPath).filter(
            LearningPath.id == path_id,
            LearningPath.user_id == current_user.id
        ).first()
        
        if not learning_path:
            raise HTTPException(
                status_code=404,
                detail="学习路径不存在或无权限访问"
            )
        
        # 删除相关任务
        db.query(LearningTask).filter(
            LearningTask.learning_path_id == path_id
        ).delete()
        
        # 删除学习路径
        db.delete(learning_path)
        db.commit()
        
        return {
            "status": "success",
            "message": "学习路径删除成功",
            "path_id": path_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除学习路径失败: {str(e)}"
        )
