'use client'
/**
 * 认证上下文提供者 - 商业级认证状态管理
 * 功能特性:
 * 1. 全局认证状态管理
 * 2. 自动令牌刷新
 * 3. 会话监控和安全检查
 * 4. 多设备登录检测
 * 5. 错误处理和恢复
 * 6. 性能优化和缓存
 */

import { 
  createContext, 
  useContext, 
  useState, 
  useEffect, 
  ReactNode, 
  useCallback,
  useRef,
  useMemo
} from 'react'
import { getCurrentUser, isTokenValid, logout } from '../lib/auth'

// 认证状态枚举
export enum AuthStatus {
  LOADING = 'loading',
  AUTHENTICATED = 'authenticated',
  UNAUTHENTICATED = 'unauthenticated',
  ERROR = 'error',
  EXPIRED = 'expired'
}

// 用户信息接口
export interface UserInfo {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  avatar?: string;
  current_role?: string;
  target_role?: string;
  email_verified: boolean;
  two_factor_enabled: boolean;
  last_login_at?: string;
  created_at?: string;
}

// 会话信息接口
export interface SessionInfo {
  session_id: string;
  client_ip: string;
  device_info: {
    user_agent: string;
    platform?: string;
    browser?: string;
  };
  created_at: string;
  last_activity: string;
}

// 认证上下文类型定义
interface AuthContextType {
  // 基础状态
  status: AuthStatus;
  isLoggedIn: boolean;
  user: UserInfo | null;
  
  // 会话管理
  sessions: SessionInfo[];
  currentSession: SessionInfo | null;
  
  // 错误处理
  error: string | null;
  lastError: Error | null;
  
  // 功能方法
  login: (username: string, password: string, deviceInfo?: any) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  clearError: () => void;
  
  // 会话管理
  refreshSessions: () => Promise<void>;
  revokeSession: (sessionId: string) => Promise<void>;
  
  // 安全功能
  checkSecurityStatus: () => Promise<void>;
  requireReauth: boolean;
  
  // 设置方法
  setIsLoggedIn: (value: boolean) => void;
  setUser: (user: UserInfo | null) => void;
}

// 创建上下文
const AuthContext = createContext<AuthContextType>({
  status: AuthStatus.LOADING,
  isLoggedIn: false,
  user: null,
  sessions: [],
  currentSession: null,
  error: null,
  lastError: null,
  login: async () => false,
  logout: async () => {},
  refreshAuth: async () => {},
  clearError: () => {},
  refreshSessions: async () => {},
  revokeSession: async () => {},
  checkSecurityStatus: async () => {},
  requireReauth: false,
  setIsLoggedIn: () => {},
  setUser: () => {}
})

// 自定义Hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// 配置常量
const CONFIG = {
  TOKEN_REFRESH_INTERVAL: 5 * 60 * 1000, // 5分钟检查一次
  SESSION_CHECK_INTERVAL: 30 * 60 * 1000, // 30分钟检查一次会话
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  STORAGE_KEYS: {
    USER: 'auth_user',
    LAST_ACTIVITY: 'auth_last_activity',
    SESSION_ID: 'auth_session_id'
  }
}

/**
 * 认证上下文提供者组件
 */
export default function AuthProvider({ children }: { children: ReactNode }) {
  // 基础状态
  const [status, setStatus] = useState<AuthStatus>(AuthStatus.LOADING);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  
  // 会话管理
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [currentSession, setCurrentSession] = useState<SessionInfo | null>(null);
  
  // 错误处理
  const [error, setError] = useState<string | null>(null);
  const [lastError, setLastError] = useState<Error | null>(null);
  const [requireReauth, setRequireReauth] = useState(false);
  
  // 定时器引用
  const tokenCheckTimer = useRef<NodeJS.Timeout | null>(null);
  const sessionCheckTimer = useRef<NodeJS.Timeout | null>(null);
  const retryAttempts = useRef(0);
  
  // 清除错误
  const clearError = useCallback(() => {
    setError(null);
    setLastError(null);
  }, []);

  // 设置错误状态
  const setErrorState = useCallback((err: Error | string) => {
    const errorObj = err instanceof Error ? err : new Error(err);
    setLastError(errorObj);
    setError(errorObj.message);
    setStatus(AuthStatus.ERROR);
  }, []);

  // 延迟重试函数
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  // 带重试的API请求
  const apiRequest = useCallback(async (
    requestFn: () => Promise<any>,
    maxRetries: number = CONFIG.MAX_RETRY_ATTEMPTS
  ): Promise<any> => {
    let lastError: Error;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const result = await requestFn();
        retryAttempts.current = 0; // 重置重试计数
        return result;
      } catch (err) {
        lastError = err instanceof Error ? err : new Error(String(err));
        
        if (attempt < maxRetries) {
          await delay(CONFIG.RETRY_DELAY * Math.pow(2, attempt)); // 指数退避
        }
      }
    }
    
    throw lastError!;
  }, []);

  // 检查认证状态
  const checkAuthStatus = useCallback(async () => {
    try {
      setStatus(AuthStatus.LOADING);
      
      // 检查本地存储的用户信息
      const storedUser = localStorage.getItem(CONFIG.STORAGE_KEYS.USER);
      if (storedUser) {
        try {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
        } catch (err) {
          console.warn('Failed to parse stored user data:', err);
          localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
        }
      }
      
      // 验证令牌有效性
      if (!isTokenValid()) {
        setStatus(AuthStatus.UNAUTHENTICATED);
        setIsLoggedIn(false);
        setUser(null);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
        return;
      }
      
      // 获取当前用户信息
      const currentUser = await apiRequest(getCurrentUser);
      
      if (currentUser) {
        setUser(currentUser);
        setIsLoggedIn(true);
        setStatus(AuthStatus.AUTHENTICATED);
        
        // 缓存用户信息
        localStorage.setItem(CONFIG.STORAGE_KEYS.USER, JSON.stringify(currentUser));
        
        // 更新最后活动时间
        localStorage.setItem(CONFIG.STORAGE_KEYS.LAST_ACTIVITY, Date.now().toString());
      } else {
        setStatus(AuthStatus.UNAUTHENTICATED);
        setIsLoggedIn(false);
        setUser(null);
      }
      
    } catch (err) {
      console.error('Auth status check failed:', err);
      
      // 如果是401错误，说明令牌已过期
      if (err instanceof Error && err.message.includes('401')) {
        setStatus(AuthStatus.EXPIRED);
        setIsLoggedIn(false);
        setUser(null);
        localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
      } else {
        setErrorState(err instanceof Error ? err : new Error('认证检查失败'));
      }
    }
  }, [apiRequest, setErrorState]);

  // 刷新认证状态
  const refreshAuth = useCallback(async () => {
    await checkAuthStatus();
  }, [checkAuthStatus]);

  // 登录函数
  const login = useCallback(async (username: string, password: string, deviceInfo?: any): Promise<boolean> => {
    try {
      setStatus(AuthStatus.LOADING);
      clearError();
      
      // 获取设备信息
      const fullDeviceInfo = {
        user_agent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        screen_resolution: `${screen.width}x${screen.height}`,
        ...deviceInfo
      };
      
      // 调用登录API
      const success = await apiRequest(async () => {
        const { login } = await import('../lib/auth');
        return login(username, password, fullDeviceInfo);
      });
      
      if (success) {
        // 重新检查认证状态
        await checkAuthStatus();
        return true;
      }
      
      return false;
    } catch (err) {
      setErrorState(err instanceof Error ? err : new Error('登录失败'));
      return false;
    }
  }, [apiRequest, checkAuthStatus, clearError, setErrorState]);

  // 登出函数
  const logoutUser = useCallback(async () => {
    try {
      setStatus(AuthStatus.LOADING);
      
      // 调用登出API
      await apiRequest(async () => {
        await logout();
      });
      
      // 清除本地状态
      setIsLoggedIn(false);
      setUser(null);
      setSessions([]);
      setCurrentSession(null);
      setRequireReauth(false);
      setStatus(AuthStatus.UNAUTHENTICATED);
      
      // 清除本地存储
      localStorage.removeItem(CONFIG.STORAGE_KEYS.USER);
      localStorage.removeItem(CONFIG.STORAGE_KEYS.LAST_ACTIVITY);
      localStorage.removeItem(CONFIG.STORAGE_KEYS.SESSION_ID);
      
    } catch (err) {
      console.error('Logout failed:', err);
      // 即使登出失败，也要清除本地状态
      setIsLoggedIn(false);
      setUser(null);
      setStatus(AuthStatus.UNAUTHENTICATED);
    }
  }, [apiRequest]);

  // 刷新会话列表
  const refreshSessions = useCallback(async () => {
    if (!isLoggedIn) return;
    
    try {
      const response = await fetch('/api/users/sessions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (err) {
      console.error('Failed to refresh sessions:', err);
    }
  }, [isLoggedIn]);

  // 撤销会话
  const revokeSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`/api/users/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        setSessions(prev => prev.filter(session => session.session_id !== sessionId));
      }
    } catch (err) {
      console.error('Failed to revoke session:', err);
      setErrorState(err instanceof Error ? err : new Error('撤销会话失败'));
    }
  }, [setErrorState]);

  // 检查安全状态
  const checkSecurityStatus = useCallback(async () => {
    if (!isLoggedIn) return;
    
    try {
      const response = await fetch('/api/users/security/audit', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (response.ok) {
        const securityData = await response.json();
        
        // 检查是否需要重新认证
        if (securityData.account_locked || securityData.failed_login_attempts > 3) {
          setRequireReauth(true);
        }
        
        // 检查异常登录活动
        if (securityData.login_history && securityData.login_history.length > 0) {
          const recentLogin = securityData.login_history[0];
          const lastActivity = localStorage.getItem(CONFIG.STORAGE_KEYS.LAST_ACTIVITY);
          
          if (lastActivity) {
            const timeDiff = Date.now() - parseInt(lastActivity);
            if (timeDiff > 24 * 60 * 60 * 1000) { // 24小时
              console.warn('Long period of inactivity detected');
            }
          }
        }
      }
    } catch (err) {
      console.error('Security check failed:', err);
    }
  }, [isLoggedIn]);

  // 设置定时检查
  useEffect(() => {
    if (isLoggedIn) {
      // 定期检查令牌状态
      tokenCheckTimer.current = setInterval(() => {
        if (!isTokenValid()) {
          setStatus(AuthStatus.EXPIRED);
          setIsLoggedIn(false);
          setUser(null);
        }
      }, CONFIG.TOKEN_REFRESH_INTERVAL);
      
      // 定期检查会话状态
      sessionCheckTimer.current = setInterval(() => {
        checkSecurityStatus();
        refreshSessions();
      }, CONFIG.SESSION_CHECK_INTERVAL);
    }
    
    return () => {
      if (tokenCheckTimer.current) {
        clearInterval(tokenCheckTimer.current);
      }
      if (sessionCheckTimer.current) {
        clearInterval(sessionCheckTimer.current);
      }
    };
  }, [isLoggedIn, checkSecurityStatus, refreshSessions]);

  // 组件挂载时初始化
  useEffect(() => {
    checkAuthStatus();
    
    // 监听storage变化（多标签页同步）
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'access_token') {
        checkAuthStatus();
      }
    };
    
    // 监听在线状态变化
    const handleOnlineChange = () => {
      if (navigator.onLine && isLoggedIn) {
        checkAuthStatus();
      }
    };
    
    // 监听页面可见性变化
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isLoggedIn) {
        checkAuthStatus();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('online', handleOnlineChange);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('online', handleOnlineChange);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [checkAuthStatus, isLoggedIn]);

  // 监听令牌变化
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !isLoggedIn) {
      setIsLoggedIn(true);
      checkAuthStatus();
    } else if (!token && isLoggedIn) {
      setIsLoggedIn(false);
      setUser(null);
      setStatus(AuthStatus.UNAUTHENTICATED);
    }
  }, [checkAuthStatus, isLoggedIn]);

  // 优化的上下文值
  const contextValue = useMemo(() => ({
    status,
    isLoggedIn,
    user,
    sessions,
    currentSession,
    error,
    lastError,
    requireReauth,
    login,
    logout: logoutUser,
    refreshAuth,
    clearError,
    refreshSessions,
    revokeSession,
    checkSecurityStatus,
    setIsLoggedIn,
    setUser
  }), [
    status,
    isLoggedIn,
    user,
    sessions,
    currentSession,
    error,
    lastError,
    requireReauth,
    login,
    logoutUser,
    refreshAuth,
    clearError,
    refreshSessions,
    revokeSession,
    checkSecurityStatus
  ]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}
