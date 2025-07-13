"""
使用量追踪器

监控免费API的使用情况，防止超出限制
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class UsageTracker:
    """使用量追踪器"""
    
    def __init__(self):
        # 使用内存存储，生产环境建议使用Redis
        self.daily_usage = defaultdict(lambda: defaultdict(int))
        self.minute_usage = defaultdict(lambda: defaultdict(int))
        self.last_cleanup = datetime.now()
        
        # 使用限制配置
        self.limits = {
            "groq": {
                "daily": 100,
                "minute": 30
            },
            "ollama": {
                "daily": -1,  # 无限制
                "minute": -1
            },
            "rule_based": {
                "daily": -1,  # 无限制
                "minute": -1
            }
        }
    
    async def increment_usage(self, user_id: int, service: str, count: int = 1):
        """增加使用计数"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 增加每日使用量
            self.daily_usage[current_date][f"{user_id}_{service}"] += count
            
            # 增加每分钟使用量
            self.minute_usage[current_minute][f"{user_id}_{service}"] += count
            
            # 定期清理过期数据
            await self._cleanup_expired_data()
            
            logger.debug(f"用户 {user_id} 服务 {service} 使用量 +{count}")
            
        except Exception as e:
            logger.error(f"记录使用量失败: {e}")
    
    async def get_daily_usage(self, user_id: int, service: str) -> int:
        """获取每日使用量"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            key = f"{user_id}_{service}"
            return self.daily_usage[current_date].get(key, 0)
        except Exception as e:
            logger.error(f"获取每日使用量失败: {e}")
            return 0
    
    async def get_minute_usage(self, user_id: int, service: str) -> int:
        """获取每分钟使用量"""
        try:
            current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
            key = f"{user_id}_{service}"
            return self.minute_usage[current_minute].get(key, 0)
        except Exception as e:
            logger.error(f"获取每分钟使用量失败: {e}")
            return 0
    
    async def check_limit(self, user_id: int, service: str) -> Dict[str, bool]:
        """检查是否超出限制"""
        try:
            service_limits = self.limits.get(service, {"daily": -1, "minute": -1})
            
            daily_usage = await self.get_daily_usage(user_id, service)
            minute_usage = await self.get_minute_usage(user_id, service)
            
            daily_ok = service_limits["daily"] == -1 or daily_usage < service_limits["daily"]
            minute_ok = service_limits["minute"] == -1 or minute_usage < service_limits["minute"]
            
            return {
                "daily_ok": daily_ok,
                "minute_ok": minute_ok,
                "can_proceed": daily_ok and minute_ok
            }
            
        except Exception as e:
            logger.error(f"检查限制失败: {e}")
            return {"daily_ok": True, "minute_ok": True, "can_proceed": True}
    
    async def get_usage_stats(self, user_id: int, service: str) -> Dict[str, Any]:
        """获取使用统计"""
        try:
            service_limits = self.limits.get(service, {"daily": -1, "minute": -1})
            
            daily_usage = await self.get_daily_usage(user_id, service)
            minute_usage = await self.get_minute_usage(user_id, service)
            
            return {
                "service": service,
                "daily": {
                    "used": daily_usage,
                    "limit": service_limits["daily"],
                    "remaining": max(0, service_limits["daily"] - daily_usage) if service_limits["daily"] != -1 else -1,
                    "percentage": (daily_usage / service_limits["daily"] * 100) if service_limits["daily"] > 0 else 0
                },
                "minute": {
                    "used": minute_usage,
                    "limit": service_limits["minute"],
                    "remaining": max(0, service_limits["minute"] - minute_usage) if service_limits["minute"] != -1 else -1,
                    "percentage": (minute_usage / service_limits["minute"] * 100) if service_limits["minute"] > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"获取使用统计失败: {e}")
            return {
                "service": service,
                "daily": {"used": 0, "limit": -1, "remaining": -1, "percentage": 0},
                "minute": {"used": 0, "limit": -1, "remaining": -1, "percentage": 0}
            }
    
    async def get_all_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """获取所有服务的使用统计"""
        try:
            stats = {}
            for service in self.limits.keys():
                stats[service] = await self.get_usage_stats(user_id, service)
            
            # 计算总体统计
            total_requests = sum([
                stats[service]["daily"]["used"] 
                for service in stats 
                if stats[service]["daily"]["used"] > 0
            ])
            
            return {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "total_requests_today": total_requests,
                "services": stats
            }
            
        except Exception as e:
            logger.error(f"获取全部使用统计失败: {e}")
            return {"user_id": user_id, "services": {}}
    
    async def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            current_time = datetime.now()
            
            # 每小时清理一次
            if current_time - self.last_cleanup < timedelta(hours=1):
                return
            
            # 清理超过7天的每日数据
            cutoff_date = (current_time - timedelta(days=7)).strftime("%Y-%m-%d")
            expired_dates = [
                date for date in self.daily_usage.keys() 
                if date < cutoff_date
            ]
            for date in expired_dates:
                del self.daily_usage[date]
            
            # 清理超过1小时的每分钟数据
            cutoff_minute = (current_time - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
            expired_minutes = [
                minute for minute in self.minute_usage.keys() 
                if minute < cutoff_minute
            ]
            for minute in expired_minutes:
                del self.minute_usage[minute]
            
            self.last_cleanup = current_time
            logger.debug(f"清理过期数据: {len(expired_dates)}天, {len(expired_minutes)}分钟")
            
        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
    
    async def reset_user_usage(self, user_id: int, service: str):
        """重置用户使用量（管理员功能）"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            key = f"{user_id}_{service}"
            
            if key in self.daily_usage[current_date]:
                del self.daily_usage[current_date][key]
            
            if key in self.minute_usage[current_minute]:
                del self.minute_usage[current_minute][key]
            
            logger.info(f"重置用户 {user_id} 服务 {service} 使用量")
            
        except Exception as e:
            logger.error(f"重置使用量失败: {e}")
    
    def update_limits(self, service: str, daily_limit: int = None, minute_limit: int = None):
        """更新服务限制"""
        try:
            if service not in self.limits:
                self.limits[service] = {"daily": -1, "minute": -1}
            
            if daily_limit is not None:
                self.limits[service]["daily"] = daily_limit
            
            if minute_limit is not None:
                self.limits[service]["minute"] = minute_limit
            
            logger.info(f"更新服务 {service} 限制: 每日{daily_limit}, 每分钟{minute_limit}")
            
        except Exception as e:
            logger.error(f"更新限制失败: {e}")

# 全局实例
usage_tracker = UsageTracker() 