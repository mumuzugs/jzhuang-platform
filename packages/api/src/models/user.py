"""
用户模型
"""
from datetime import datetime
import enum
import uuid

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum as SQLEnum, select

from src.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色"""
    FREE = "FREE"
    PRO = "PRO"
    ADMIN = "ADMIN"


class UserStatus(str, enum.Enum):
    """用户状态"""
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
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

    @property
    def is_pro(self) -> bool:
        if self.role == UserRole.PRO and self.pro_expire_time:
            return self.pro_expire_time > datetime.utcnow()
        return self.role == UserRole.PRO

    @classmethod
    async def get_by_phone(cls, db, phone: str):
        result = await db.execute(
            select(cls).where(cls.phone == phone, cls.status != UserStatus.DELETED)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, db, user_id: str):
        result = await db.execute(
            select(cls).where(cls.id == user_id, cls.status != UserStatus.DELETED)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, db, phone: str, **kwargs):
        user = cls(phone=phone, **kwargs)
        db.add(user)
        await db.flush()
        return user


class Order(Base):
    """订单表（最小兼容声明）"""
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    order_no = Column(String(64), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    payment_method = Column(String(20), nullable=True)
    payment_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
