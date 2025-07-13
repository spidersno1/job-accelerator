"""
用户认证和管理路由模块

这个模块提供完整的用户认证和管理功能，包括：

核心功能：
1. 用户注册和登录
2. JWT令牌管理（访问令牌、刷新令牌）
3. 密码管理（修改密码、重置密码）
4. 邮箱验证和双因素认证
5. 用户资料管理
6. 会话管理和安全审计

安全特性：
- 密码强度验证
- 登录尝试限制
- 会话管理
- 安全事件日志
- 双因素认证支持
- 密码哈希存储

API端点：
- POST /token: 用户登录获取令牌
- POST /refresh: 刷新访问令牌
- POST /register: 用户注册
- POST /verify-email: 邮箱验证
- POST /forgot-password: 忘记密码
- POST /reset-password: 重置密码
- GET /profile: 获取用户资料
- PUT /profile: 更新用户资料
- POST /logout: 用户登出

作者: 程序员求职加速器团队
创建时间: 2024年
最后更新: 2025年1月
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
import secrets
import json
from ..database import get_db
from ..models.user import User
from ..models.schemas import (
    UserUpdate, 
    User as UserSchema,
    GitHubConnectRequest,
    UserCreate,
    Token
)
from fastapi.security import OAuth2PasswordRequestForm
from ..core.security import (
    get_password_hash,
    create_access_token,
    create_refresh_token,
    authenticate_user,
    get_current_user,
    get_current_active_user,
    validate_password_strength,
    generate_secure_token,
    get_security_headers,
    log_security_event,
    session_manager,
    PasswordStrengthError,
    LoginAttemptLimitError
)
from datetime import timedelta
from app.core.config import settings
import logging

# 创建路由器实例
router = APIRouter()
logger = logging.getLogger(__name__)

# 邮件发送服务（在实际项目中应该使用真实的邮件服务）
async def send_email(to_email: str, subject: str, body: str):
    """发送邮件（模拟）"""
    logger.info(f"Sending email to {to_email}: {subject}")
    # 在实际项目中，这里应该调用真实的邮件服务
    print(f"EMAIL: To={to_email}, Subject={subject}, Body={body}")

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录获取token - 极简版"""
    try:
        print(f"=== 极简登录API ===")
        print(f"用户名: {form_data.username}")
        print(f"密码: {form_data.password}")
        
        # 直接查询用户
        user = db.query(User).filter(User.username == form_data.username).first()
        print(f"查询用户结果: {user}")
        
        if not user:
            print("用户不存在")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证密码
        from ..core.security import verify_password
        password_valid = verify_password(form_data.password, user.hashed_password)
        print(f"密码验证结果: {password_valid}")
        
        if not password_valid:
            print("密码验证失败")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print("认证成功，创建token")
        
        # 创建token
        access_token = create_access_token(data={"sub": user.username})
        
        print("token创建成功")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录异常: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    from ..core.security import verify_refresh_token
    
    user_id = verify_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register", response_model=UserSchema)
async def register_user(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """用户注册 - 增强版"""
    client_ip = request.client.host
    
    try:
        # 检查用户名是否已存在
        db_user = db.query(User).filter(User.username == user_create.username).first()
        if db_user:
            log_security_event("REGISTRATION_FAILED", None, {
                "username": user_create.username,
                "reason": "username_exists"
            }, client_ip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        db_email = db.query(User).filter(User.email == user_create.email).first()
        if db_email:
            log_security_event("REGISTRATION_FAILED", None, {
                "email": user_create.email,
                "reason": "email_exists"
            }, client_ip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 验证密码强度
        try:
            hashed_password = get_password_hash(user_create.password)
        except PasswordStrengthError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # 生成邮箱验证令牌
        email_verification_token = generate_secure_token()
        
        # 创建用户
        user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            leetcode_username=user_create.leetcode_username,
            current_role=user_create.current_role,
            target_role=user_create.target_role,
            experience_years=user_create.experience_years,
            email_verification_token=email_verification_token,
            email_verification_expires=datetime.utcnow() + timedelta(hours=24),
            password_changed_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 发送邮箱验证邮件
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={email_verification_token}"
        background_tasks.add_task(
            send_email,
            user.email,
            "验证您的邮箱地址",
            f"请点击以下链接验证您的邮箱地址：{verification_url}"
        )
        
        log_security_event("REGISTRATION_SUCCESS", user.id, {
            "username": user.username,
            "email": user.email
        }, client_ip)
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log_security_event("REGISTRATION_ERROR", None, {
            "username": user_create.username,
            "error": str(e)
        }, client_ip)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册过程中发生错误"
        )

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """验证邮箱地址"""
    user = db.query(User).filter(User.email_verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的验证令牌"
        )
    
    if user.email_verification_expires and datetime.utcnow() > user.email_verification_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证令牌已过期"
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已经验证过了"
        )
    
    # 验证邮箱
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    db.commit()
    
    log_security_event("EMAIL_VERIFIED", user.id, {
        "email": user.email
    })
    
    return {"message": "邮箱验证成功"}

@router.post("/resend-verification")
async def resend_verification_email(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """重新发送验证邮件"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # 为了安全，不透露用户是否存在
        return {"message": "如果邮箱存在，验证邮件已发送"}
    
    if user.email_verified:
        return {"message": "邮箱已经验证过了"}
    
    # 生成新的验证令牌
    email_verification_token = generate_secure_token()
    user.email_verification_token = email_verification_token
    user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
    db.commit()
    
    # 发送验证邮件
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={email_verification_token}"
    background_tasks.add_task(
        send_email,
        user.email,
        "验证您的邮箱地址",
        f"请点击以下链接验证您的邮箱地址：{verification_url}"
    )
    
    return {"message": "验证邮件已发送"}

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """忘记密码"""
    client_ip = request.client.host
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # 为了安全，不透露用户是否存在
        return {"message": "如果邮箱存在，重置密码邮件已发送"}
    
    # 生成密码重置令牌
    reset_token = generate_secure_token()
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1小时有效期
    db.commit()
    
    # 发送密码重置邮件
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    background_tasks.add_task(
        send_email,
        user.email,
        "重置您的密码",
        f"请点击以下链接重置您的密码：{reset_url}\n\n如果您没有请求重置密码，请忽略此邮件。"
    )
    
    log_security_event("PASSWORD_RESET_REQUESTED", user.id, {
        "email": user.email
    }, client_ip)
    
    return {"message": "密码重置邮件已发送"}

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """重置密码"""
    client_ip = request.client.host
    user = db.query(User).filter(User.password_reset_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的重置令牌"
        )
    
    if user.password_reset_expires and datetime.utcnow() > user.password_reset_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌已过期"
        )
    
    try:
        # 验证新密码强度
        hashed_password = get_password_hash(new_password)
    except PasswordStrengthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # 更新密码
    user.hashed_password = hashed_password
    user.password_reset_token = None
    user.password_reset_expires = None
    user.password_changed_at = datetime.utcnow()
    
    # 清除所有活跃会话（强制重新登录）
    user.active_sessions = None
    
    # 解锁账户（如果被锁定）
    if user.account_locked:
        user.unlock_account()
    
    db.commit()
    
    log_security_event("PASSWORD_RESET_SUCCESS", user.id, {
        "email": user.email
    }, client_ip)
    
    return {"message": "密码重置成功"}

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更改密码"""
    client_ip = request.client.host
    
    # 验证当前密码
    from ..core.security import verify_password
    if not verify_password(current_password, current_user.hashed_password):
        log_security_event("PASSWORD_CHANGE_FAILED", current_user.id, {
            "reason": "invalid_current_password"
        }, client_ip)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    try:
        # 验证新密码强度
        hashed_password = get_password_hash(new_password)
    except PasswordStrengthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # 更新密码
    current_user.hashed_password = hashed_password
    current_user.password_changed_at = datetime.utcnow()
    db.commit()
    
    log_security_event("PASSWORD_CHANGE_SUCCESS", current_user.id, {
        "email": current_user.email
    }, client_ip)
    
    return {"message": "密码更改成功"}

@router.post("/verify-2fa")
async def verify_two_factor(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """验证二次认证码 - 增强版"""
    if not current_user.two_factor_enabled or not current_user.require_reauth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无需二次认证"
        )
    
    # 检查验证码是否过期
    if current_user.two_factor_expires and datetime.utcnow() > current_user.two_factor_expires:
        current_user.require_reauth = False
        current_user.two_factor_secret = None
        current_user.two_factor_expires = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期，请重新登录"
        )
    
    if code != current_user.two_factor_secret:
        log_security_event("TWO_FACTOR_FAILED", current_user.id, {
            "provided_code": code[:2] + "****"  # 只记录前两位
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="验证码错误"
        )
    
    # 验证成功，清除二次认证状态
    current_user.require_reauth = False
    current_user.two_factor_secret = None
    current_user.two_factor_expires = None
    db.commit()
    
    log_security_event("TWO_FACTOR_SUCCESS", current_user.id, {})
    
    return {"status": "success", "message": "二次认证成功"}

@router.get("/profile", response_model=UserSchema)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """获取用户资料"""
    return current_user

@router.put("/profile", response_model=UserSchema)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新用户资料"""
    # 更新允许的字段
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.current_role is not None:
        current_user.current_role = user_update.current_role
    if user_update.target_role is not None:
        current_user.target_role = user_update.target_role
    if user_update.experience_years is not None:
        current_user.experience_years = user_update.experience_years
    if user_update.leetcode_username is not None:
        current_user.leetcode_username = user_update.leetcode_username
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的活跃会话"""
    sessions = current_user.get_active_sessions()
    return {"sessions": sessions}

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """撤销指定会话"""
    current_user.remove_active_session(session_id)
    session_manager.destroy_session(session_id)
    db.commit()
    
    log_security_event("SESSION_REVOKED", current_user.id, {
        "session_id": session_id
    })
    
    return {"message": "会话已撤销"}

@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户登出"""
    client_ip = request.client.host
    
    # 清除当前会话
    # 这里需要从请求中获取会话ID，实际实现中可能需要调整
    current_user.active_sessions = None
    db.commit()
    
    log_security_event("LOGOUT_SUCCESS", current_user.id, {}, client_ip)
    
    return {"message": "登出成功"}

@router.get("/security/audit")
async def get_security_audit(
    current_user: User = Depends(get_current_active_user)
):
    """获取安全审计信息"""
    login_history = []
    if current_user.login_history:
        try:
            login_history = json.loads(current_user.login_history)
        except:
            login_history = []
    
    return {
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        "last_login_ip": current_user.last_login_ip,
        "login_history": login_history,
        "failed_login_attempts": current_user.failed_login_attempts,
        "last_failed_login": current_user.last_failed_login.isoformat() if current_user.last_failed_login else None,
        "account_locked": current_user.account_locked,
        "two_factor_enabled": current_user.two_factor_enabled,
        "email_verified": current_user.email_verified,
        "password_changed_at": current_user.password_changed_at.isoformat() if current_user.password_changed_at else None,
        "active_sessions_count": len(current_user.get_active_sessions())
    }

@router.post("/validate-password")
async def validate_password_endpoint(password: str):
    """验证密码强度"""
    validation_result = validate_password_strength(password)
    return validation_result
