"""
短信服务 - 简化版（内存存储）
"""
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class SmsService:
    """短信服务"""
    
    CODE_EXPIRE_MINUTES = 5
    MAX_SENDS_PER_HOUR = 5
    MIN_INTERVAL_SECONDS = 60
    
    # 内存存储
    _code_store: dict = {}
    _send_times: dict = {}
    
    def send_login_code(self, phone: str) -> dict:
        """发送登录验证码"""
        # 验证手机号格式
        if not self._validate_phone(phone):
            return {"success": False, "message": "手机号格式不正确", "code": None}
        
        # 检查发送频率
        if not self._check_rate_limit(phone):
            return {"success": False, "message": f"发送太频繁，请{self.MIN_INTERVAL_SECONDS}秒后重试", "code": None}
        
        # 生成验证码（测试环境固定为123456）
        code = "123456"
        
        # 存储验证码
        expire_time = datetime.utcnow() + timedelta(minutes=self.CODE_EXPIRE_MINUTES)
        self._code_store[phone] = (code, expire_time)
        
        # 记录发送时间
        if phone not in self._send_times:
            self._send_times[phone] = []
        self._send_times[phone].append(datetime.utcnow())
        
        logger.info(f"[模拟短信] 发送到 {phone}，验证码: {code}")
        return {"success": True, "message": "验证码已发送", "code": code}
    
    def verify_code(self, phone: str, code: str) -> bool:
        """验证验证码"""
        stored = self._code_store.get(phone)
        if not stored:
            return False
        
        stored_code, expire_time = stored
        
        if datetime.utcnow() > expire_time:
            del self._code_store[phone]
            return False
        
        if stored_code == code:
            del self._code_store[phone]
            return True
        
        return False
    
    def _check_rate_limit(self, phone: str) -> bool:
        """检查发送频率限制"""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        send_times = self._send_times.get(phone, [])
        recent_sends = [t for t in send_times if t > one_hour_ago]
        
        if len(recent_sends) >= self.MAX_SENDS_PER_HOUR:
            return False
        
        if recent_sends:
            last_send = max(recent_sends)
            if (now - last_send).total_seconds() < self.MIN_INTERVAL_SECONDS:
                return False
        
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))


# 全局单例
sms_service = SmsService()


async def send_sms_code(phone: str) -> str:
    """发送短信验证码"""
    result = sms_service.send_login_code(phone)
    if result["success"]:
        return result["code"]
    raise ValueError(result["message"])


async def verify_sms_code(phone: str, code: str) -> bool:
    """验证短信验证码"""
    return sms_service.verify_code(phone, code)
