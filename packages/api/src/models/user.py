"""
用户模型
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色"""
    FREE = "free"
    PRO = "pro"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.FREE, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    pro_expire_time = Column(DateTime, nullable=True)
    pro_order_no = Column(String(64), nullable=True)
    sms_code = Column(String(6), nullable=True)
    sms_code_expire = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)
    
    __table_args__ = (
        Index("idx_user_phone", "phone"),
        Index("idx_user_created_at", "created_at"),
        Index("idx_user_role", "role"),
    )
    
    @property
    def is_pro(self) -> bool:
        """是否专业版用户"""
        if self.role == UserRole.PRO and self.pro_expire_time:
            return self.pro_expire_time > datetime.utcnow()
        return False
    
    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        if self.pro_expire_time:
            return self.pro_expire_time < datetime.utcnow()
        return False


class SmsCode(Base):
    """短信验证码表"""
    __tablename__ = "sms_codes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(11), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    purpose = Column(String(20), nullable=False)
    status = Column(String(20), default="pending")
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expire_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index("idx_sms_code_phone", "phone", "purpose"),
        Index("idx_sms_code_expire", "expire_at"),
    )


class LoginLog(Base):
    """登录日志表"""
    __tablename__ = "login_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)
    phone = Column(String(11), nullable=False, index=True)
    ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_login_log_phone", "phone"),
        Index("idx_login_log_created_at", "created_at"),
    )


# 便捷函数
async def get_user_by_phone(db, phone: str):
    """根据手机号查询用户"""
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.phone == phone, User.status != UserStatus.DELETED)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db, user_id: str):
    """根据ID查询用户"""
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(db, phone: str, **kwargs):
    """创建用户"""
    user = User(phone=phone, **kwargs)
    db.add(user)
    await db.flush()
    return user


async def update_user_login(db, user: User, ip: str = None):
    """更新登录信息"""
    user.last_login_at = datetime.utcnow()
    if ip:
        user.last_login_ip = ip
    await db.flush()
