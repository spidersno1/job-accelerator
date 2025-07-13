from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import AgentRequest, AgentResponse, ChatRequest
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.agent_service import AgentService
from app.services.free_ai_agent_service import FreeAIAgentService
from typing import Dict, Any

router = APIRouter()

def get_current_user_id(current_user: User = Depends(get_current_active_user)) -> int:
    """获取当前用户ID"""
    return current_user.id

@router.post("/process", response_model=AgentResponse)
async def process_agent_request(
    request: AgentRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """处理AI Agent请求"""
    agent_service = AgentService()
    
    try:
        result = await agent_service.process_request(
            request_type=request.request_type,
            user_id=current_user_id,
            parameters=request.parameters,
            db=db
        )
        
        return AgentResponse(
            success=True,
            data=result,
            message="请求处理成功"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"请求处理失败: {str(e)}"
        )

@router.get("/daily-task", response_model=AgentResponse)
async def get_daily_task(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取每日AI督学任务 - 免费版"""
    free_agent = FreeAIAgentService()
    
    try:
        task = await free_agent.generate_daily_task(current_user_id)
        
        return AgentResponse(
            success=task["success"],
            data=task,
            message="获取每日任务成功" if task["success"] else "获取每日任务失败"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"获取每日任务失败: {str(e)}"
        )

@router.post("/complete-task", response_model=AgentResponse)
async def complete_daily_task(
    task_id: str,
    completion_data: Dict[str, Any],
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """完成每日任务"""
    agent_service = AgentService()
    
    try:
        result = await agent_service.complete_daily_task(
            task_id=task_id,
            user_id=current_user_id,
            completion_data=completion_data,
            db=db
        )
        
        return AgentResponse(
            success=True,
            data=result,
            message="任务完成"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"任务完成失败: {str(e)}"
        )

@router.get("/progress", response_model=AgentResponse)
async def get_learning_progress(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取学习进度"""
    agent_service = AgentService()
    
    try:
        progress = await agent_service.get_learning_progress(current_user_id, db)
        
        return AgentResponse(
            success=True,
            data=progress,
            message="获取学习进度成功"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"获取学习进度失败: {str(e)}"
        )

@router.post("/chat", response_model=AgentResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """与AI Agent对话 - 免费版"""
    free_agent = FreeAIAgentService()
    
    try:
        response = await free_agent.chat(
            message=request.message,
            user_id=current_user_id,
            context=request.context
        )
        
        return AgentResponse(
            success=response["success"],
            data=response,
            message="对话成功" if response["success"] else "对话失败"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"对话失败: {str(e)}"
        )

@router.post("/analyze-resume", response_model=AgentResponse)
async def analyze_resume(
    resume_text: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """分析简历"""
    agent_service = AgentService()
    
    try:
        analysis = await agent_service.analyze_resume(
            resume_text=resume_text,
            user_id=current_user_id,
            db=db
        )
        
        return AgentResponse(
            success=True,
            data=analysis,
            message="简历分析完成"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"简历分析失败: {str(e)}"
        )

@router.post("/generate-cover-letter", response_model=AgentResponse)
async def generate_cover_letter(
    job_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """生成求职信"""
    agent_service = AgentService()
    
    try:
        cover_letter = await agent_service.generate_cover_letter(
            job_id=job_id,
            user_id=current_user_id,
            db=db
        )
        
        return AgentResponse(
            success=True,
            data=cover_letter,
            message="求职信生成完成"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"求职信生成失败: {str(e)}"
        )

@router.get("/usage-stats", response_model=AgentResponse)
async def get_usage_stats(
    current_user_id: int = Depends(get_current_user_id)
):
    """获取免费AI使用统计"""
    free_agent = FreeAIAgentService()
    
    try:
        stats = await free_agent.get_usage_stats(current_user_id)
        
        return AgentResponse(
            success=True,
            data=stats,
            message="获取使用统计成功"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"获取使用统计失败: {str(e)}"
        )

@router.get("/health", response_model=AgentResponse)
async def health_check():
    """免费AI Agent健康检查"""
    free_agent = FreeAIAgentService()
    
    try:
        health = await free_agent.health_check()
        
        return AgentResponse(
            success=health["overall_status"] != "error",
            data=health,
            message=f"系统状态: {health['overall_status']}"
        )
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"健康检查失败: {str(e)}"
        )
