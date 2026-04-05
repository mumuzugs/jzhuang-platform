"""
短信服务
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from src.core.config import settings
from src.core.security import generate_sms_code
from src.core.database import async_session_factory

logger = logging.getLogger(__name__)


class SmsService:
    """短信服务"""
    
    # 验证码有效期（分钟）
    CODE_EXPIRE_MINUTES = 5
    
    # 发送限制
    MAX_SENDS_PER_HOUR = 5
    MIN_INTERVAL_SECONDS = 60
    
    def __init__(self):
        self._code_store: dict[str, tuple[str, datetime]] = {}  # phone -> (code, expire_time)
    
    async def send_login_code(self, phone: str) -> dict:
        """
        发送登录验证码
        
        Args:
            phone: 手机号
            
        Returns:
            {"success": bool, "message": str, "code": str or None}
        """
        # 验证手机号格式
        if not self._validate_phone(phone):
            return {"success": False, "message": "手机号格式不正确", "code": None}
        
        # 检查发送频率
        if not await self._check_rate_limit(phone):
            return {
                "success": False,
                "message": f"发送太频繁，请{MIN_INTERVAL_SECONDS}秒后重试",
                "code": None
            }
        
        # 生成验证码
        code = generate_sms_code(6)
        
        # 存储验证码
        expire_time = datetime.utcnow() + timedelta(minutes=self.CODE_EXPIRE_MINUTES)
        await self._store_code(phone, code, expire_time)
        
        # 实际发送短信（这里用日志模拟）
        # TODO: 集成真实的短信服务商（阿里云、腾讯云等）
        success = await self._send_sms(phone, code)
        
        if success:
            logger.info(f"短信验证码已发送: {phone} -> {code}")
            return {"success": True, "message": "验证码已发送", "code": code}
        else:
            return {"success": False, "message": "短信发送失败，请稍后重试", "code": None}
    
    async def verify_code(self, phone: str, code: str) -> bool:
        """
        验证验证码
        
        Args:
            phone: 手机号
            code: 验证码
            
        Returns:
            bool: 验证是否成功
        """
        stored = self._code_store.get(phone)
        if not stored:
            return False
        
        stored_code, expire_time = stored
        
        # 检查是否过期
        if datetime.utcnow() > expire_time:
            del self._code_store[phone]
            return False
        
        # 检查验证码
        if stored_code == code:
            # 验证成功后删除验证码
            del self._code_store[phone]
            return True
        
        return False
    
    async def _store_code(self, phone: str, code: str, expire_time: datetime):
        """存储验证码"""
        self._code_store[phone] = (code, expire_time)
        
        # 保存到数据库
        async with async_session_factory() as db:
            from src.models.user import SmsCode
            from sqlalchemy import select, update
            
            # 使之前的验证码失效
            await db.execute(
                update(SmsCode)
                .where(SmsCode.phone == phone, SmsCode.status == "pending")
                .values(status="expired")
            )
            
            # 创建新验证码记录
            sms_record = SmsCode(
                phone=phone,
                code=code,
                purpose="login",
                expire_at=expire_time
            )
            db.add(sms_record)
            await db.commit()
    
    async def _check_rate_limit(self, phone: str) -> bool:
        """检查发送频率限制"""
        async with async_session_factory() as db:
            from src.models.user import SmsCode
            from sqlalchemy import select, func
            from datetime import timedelta
            
            # 检查最近1小时内的发送次数
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            result = await db.execute(
                select(func.count(SmsCode.id))
                .where(
                    SmsCode.phone == phone,
                    SmsCode.created_at >= one_hour_ago,
                    SmsCode.status == "pending"
                )
            )
            count = result.scalar()
            
            if count >= self.MAX_SENDS_PER_HOUR:
                return False
            
            # 检查最小间隔
            result = await db.execute(
                select(SmsCode.created_at)
                .where(
                    SmsCode.phone == phone,
                    SmsCode.status == "pending"
                )
                .order_by(SmsCode.created_at.desc())
                .limit(1)
            )
            last_send = result.scalar_one_or_none()
            
            if last_send:
                interval = (datetime.utcnow() - last_send).total_seconds()
                if interval < self.MIN_INTERVAL_SECONDS:
                    return False
            
            return True
    
    async def _send_sms(self, phone: str, code: str) -> bool:
        """
        实际发送短信
        
        TODO: 集成真实的短信服务商
        - 阿里云短信服务
        - 腾讯云短信服务
        - 华为云短信服务
        """
        # 模拟发送成功
        # 实际项目中需要调用真实的短信API
        logger.info(f"[模拟短信] 发送到 {phone}，验证码: {code}")
        return True
    
    def _validate_phone(self, phone: str) -> bool:
        """验证手机号格式"""
        import re
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))


# 全局单例
sms_service = SmsService()


# 便捷函数
async def send_sms_code(phone: str) -> str:
    """发送短信验证码"""
    result = await sms_service.send_login_code(phone)
    if result["success"]:
        return result["code"]
    raise ValueError(result["message"])


async def verify_sms_code(phone: str, code: str) -> bool:
    """验证短信验证码"""
    return await sms_service.verify_code(phone, code)