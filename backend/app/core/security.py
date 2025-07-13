from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import random
import string
import time
import re
import hashlib
import secrets
import warnings
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..database import get_db
from ..models.user import User
from app.core.config import settings

# 过滤bcrypt版本警告
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

# 登录尝试限制配置
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 30  # 分钟
LOGIN_ATTEMPTS_CACHE = {}  # 在生产环境中应使用Redis

# 密码强度配置 - 放宽要求
MIN_PASSWORD_LENGTH = 6
REQUIRE_UPPERCASE = False
REQUIRE_LOWERCASE = False
REQUIRE_NUMBERS = False
REQUIRE_SPECIAL_CHARS = False

class SecurityException(Exception):
    """安全相关异常"""
    pass

class PasswordStrengthError(SecurityException):
    """密码强度不足异常"""
    pass

class LoginAttemptLimitError(SecurityException):
    """登录尝试次数超限异常"""
    pass

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    验证密码强度 - 简化版本
    返回验证结果和改进建议
    """
    errors = []
    suggestions = []
    score = 0
    
    # 长度检查
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"密码长度至少需要{MIN_PASSWORD_LENGTH}个字符")
        suggestions.append("增加密码长度")
    else:
        score += 50
    
    # 基本字符检查
    if len(password) >= 8:
        score += 20
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    
    strength_level = "弱"
    if score >= 80:
        strength_level = "强"
    elif score >= 60:
        strength_level = "中等"
    
    return {
        "is_valid": len(errors) == 0,
        "score": max(0, score),
        "strength_level": strength_level,
        "errors": errors,
        "suggestions": suggestions
    }

def check_login_attempts(identifier: str, client_ip: str) -> bool:
    """
    检查登录尝试次数
    identifier: 用户名或邮箱
    client_ip: 客户端IP
    """
    current_time = datetime.utcnow()
    
    # 检查用户名/邮箱的尝试次数
    user_key = f"user:{identifier}"
    if user_key in LOGIN_ATTEMPTS_CACHE:
        attempts = LOGIN_ATTEMPTS_CACHE[user_key]
        if attempts['count'] >= MAX_LOGIN_ATTEMPTS:
            if current_time < attempts['locked_until']:
                return False
            else:
                # 锁定期已过，重置计数
                del LOGIN_ATTEMPTS_CACHE[user_key]
    
    # 检查IP的尝试次数
    ip_key = f"ip:{client_ip}"
    if ip_key in LOGIN_ATTEMPTS_CACHE:
        attempts = LOGIN_ATTEMPTS_CACHE[ip_key]
        if attempts['count'] >= MAX_LOGIN_ATTEMPTS * 2:  # IP限制更严格
            if current_time < attempts['locked_until']:
                return False
            else:
                del LOGIN_ATTEMPTS_CACHE[ip_key]
    
    return True

def record_login_attempt(identifier: str, client_ip: str, success: bool):
    """
    记录登录尝试
    """
    current_time = datetime.utcnow()
    
    if success:
        # 登录成功，清除尝试记录
        user_key = f"user:{identifier}"
        ip_key = f"ip:{client_ip}"
        if user_key in LOGIN_ATTEMPTS_CACHE:
            del LOGIN_ATTEMPTS_CACHE[user_key]
        if ip_key in LOGIN_ATTEMPTS_CACHE:
            del LOGIN_ATTEMPTS_CACHE[ip_key]
    else:
        # 登录失败，增加尝试计数
        for key in [f"user:{identifier}", f"ip:{client_ip}"]:
            if key in LOGIN_ATTEMPTS_CACHE:
                LOGIN_ATTEMPTS_CACHE[key]['count'] += 1
                if LOGIN_ATTEMPTS_CACHE[key]['count'] >= MAX_LOGIN_ATTEMPTS:
                    LOGIN_ATTEMPTS_CACHE[key]['locked_until'] = current_time + timedelta(minutes=LOCKOUT_DURATION)
            else:
                LOGIN_ATTEMPTS_CACHE[key] = {
                    'count': 1,
                    'first_attempt': current_time,
                    'locked_until': None
                }

def generate_secure_token() -> str:
    """生成安全的随机令牌"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """对令牌进行哈希处理"""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # 验证密码强度
    validation_result = validate_password_strength(password)
    if not validation_result["is_valid"]:
        raise PasswordStrengthError(f"密码强度不足: {', '.join(validation_result['errors'])}")
    
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str, client_ip: str = None, device_info: Dict[str, Any] = None) -> Optional[User]:
    """用户认证 - 增强版"""
    print(f"=== authenticate_user 调试 ===")
    print(f"输入用户名: {username}")
    print(f"输入密码: {password}")
    print(f"客户端IP: {client_ip}")
    
    # 检查登录尝试限制
    if client_ip and not check_login_attempts(username, client_ip):
        print("登录尝试次数超限")
        record_login_attempt(username, client_ip, False)
        raise LoginAttemptLimitError("登录尝试次数过多，账户已被暂时锁定")
    
    print("登录尝试次数检查通过")
    
    # 同时支持username和email登录
    print("查询用户...")
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    print(f"数据库查询结果: {user}")
    if user:
        print(f"找到用户: {user.username}, 邮箱: {user.email}")
        print(f"用户激活状态: {user.is_active}")
        print(f"数据库密码哈希: {user.hashed_password[:50]}...")
    else:
        print("数据库中未找到用户")
    
    # 验证密码
    print("开始密码验证...")
    if user:
        try:
            auth_success = verify_password(password, user.hashed_password)
            print(f"密码验证结果: {auth_success}")
        except Exception as e:
            print(f"密码验证异常: {e}")
            auth_success = False
    else:
        auth_success = False
        print("用户不存在，密码验证跳过")
    
    # 记录登录尝试
    if client_ip:
        record_login_attempt(username, client_ip, auth_success)
        print(f"登录尝试已记录: {auth_success}")
    
    if not auth_success:
        print("认证失败，返回None")
        return None
    
    print("认证成功，准备更新用户信息...")
    
    # 更新用户登录信息
    if user and client_ip:
        user.last_login_ip = client_ip
        user.last_login_at = datetime.utcnow()
        
        # 更新登录历史
        login_history = []
        if user.login_history:
            try:
                login_history = json.loads(user.login_history)
            except:
                login_history = []
        
        login_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "ip": client_ip,
            "device": device_info or {},
            "user_agent": device_info.get("user_agent", "") if device_info else ""
        })
        
        # 只保留最近10次登录记录
        user.login_history = json.dumps(login_history[-10:])
        db.commit()
        print("用户登录信息更新完成")
    
    # 检查是否需要二次认证
    if user.two_factor_enabled:
        user.require_reauth = True
        user.two_factor_secret = ''.join(random.choices(string.digits, k=6))
        user.two_factor_expires = datetime.utcnow() + timedelta(minutes=10)  # 10分钟有效期
        db.commit()
        print("启用二次认证")
    
    print(f"=== 认证成功，返回用户: {user.username} ===")
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问token - 增强版"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加额外的安全信息
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": generate_secure_token()[:16],  # JWT ID
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int) -> str:
    """创建刷新token"""
    data = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
        "jti": generate_secure_token()[:16]
    }
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_refresh_token(token: str) -> Optional[int]:
    """验证刷新token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        user_id = payload.get("sub")
        return int(user_id) if user_id else None
    except JWTError:
        return None

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户 - 增强版"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if username is None or token_type != "access":
            raise credentials_exception
            
        # 检查token是否在黑名单中（在生产环境中应使用Redis）
        # 这里可以添加token黑名单检查逻辑
        
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # 检查用户是否仍然活跃
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户 - 增强版"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    if current_user.require_reauth:
        # 检查二次认证是否过期
        if current_user.two_factor_expires and datetime.utcnow() > current_user.two_factor_expires:
            # 二次认证已过期，清除状态
            current_user.require_reauth = False
            current_user.two_factor_secret = None
            current_user.two_factor_expires = None
            # 这里需要数据库会话，在实际使用中需要处理
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="需要二次认证",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return current_user

def get_security_headers() -> Dict[str, str]:
    """获取安全响应头"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

def log_security_event(event_type: str, user_id: Optional[int], details: Dict[str, Any], client_ip: str = None):
    """记录安全事件"""
    # 在生产环境中，这应该写入专门的安全日志系统
    security_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "client_ip": client_ip,
        "details": details
    }
    
    # 这里可以集成到日志系统或安全监控系统
    print(f"SECURITY EVENT: {json.dumps(security_log)}")

# 会话管理类
class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.active_sessions = {}  # 在生产环境中应使用Redis
    
    def create_session(self, user_id: int, client_ip: str, device_info: Dict[str, Any]) -> str:
        """创建会话"""
        session_id = generate_secure_token()
        session_data = {
            "user_id": user_id,
            "client_ip": client_ip,
            "device_info": device_info,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        self.active_sessions[session_id] = session_data
        return session_id
    
    def validate_session(self, session_id: str, client_ip: str) -> bool:
        """验证会话"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # 检查IP是否匹配
        if session["client_ip"] != client_ip:
            return False
        
        # 检查会话是否过期
        if datetime.utcnow() - session["last_activity"] > timedelta(hours=24):
            self.destroy_session(session_id)
            return False
        
        # 更新最后活动时间
        session["last_activity"] = datetime.utcnow()
        return True
    
    def destroy_session(self, session_id: str):
        """销毁会话"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户的所有会话"""
        return [
            {
                "session_id": sid,
                "client_ip": session["client_ip"],
                "device_info": session["device_info"],
                "created_at": session["created_at"],
                "last_activity": session["last_activity"]
            }
            for sid, session in self.active_sessions.items()
            if session["user_id"] == user_id
        ]

# 全局会话管理器实例
session_manager = SessionManager()
