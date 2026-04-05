"""
用户模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色"""
    FREE = "free"           # 免费版用户
    PRO = "pro"             # 专业版用户
    ADMIN = "admin"         # 管理员


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    phone = Column(String(11), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.FREE, nullable=False)
    
    # 会员信息
    pro_expire_time = Column(DateTime, nullable=True)  # 专业版到期时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # 关系
    orders = relationship("Order", back_populates="user")
    design_projects = relationship("DesignProject", back_populates="user")
    inspection_reports = relationship("InspectionReport", back_populates="user")
    construction_projects = relationship("ConstructionProject", back_populates="user")


class Order(Base):
    """订单表"""
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    order_no = Column(String(64), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)  # 金额（分）
    status = Column(String(20), default="pending", nullable=False)  # pending, paid, cancelled, refunded
    payment_method = Column(String(20), nullable=True)
    payment_time = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="orders")
