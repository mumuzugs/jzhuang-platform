"""
订单和支付模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.core.database import Base


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"          # 待支付
    PAID = "paid"               # 已支付
    CANCELLED = "cancelled"     # 已取消
    REFUNDED = "refunded"       # 已退款


class PaymentMethod(str, enum.Enum):
    """支付方式"""
    WECHAT = "wechat"           # 微信支付
    ALIPAY = "alipay"           # 支付宝


class Order(Base):
    """订单表"""
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_no = Column(String(64), unique=True, nullable=False)  # 订单号
    
    user_id = Column(String(36), nullable=False, index=True)
    
    # 商品信息
    product_type = Column(String(50), nullable=False)  # vip_pro, add_service
    product_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 金额（分）
    amount = Column(Integer, nullable=False)
    
    # 订单状态
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    
    # 支付信息
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    payment_time = Column(DateTime, nullable=True)
    wechat_order_no = Column(String(64), nullable=True)  # 微信支付订单号
    
    # 有效期
    expire_days = Column(Integer, default=180)  # 有效期天数（默认6个月）
    effective_time = Column(DateTime, nullable=True)  # 生效时间
    expire_time = Column(DateTime, nullable=True)     # 过期时间
    
    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_order_user", "user_id"),
        Index("idx_order_status", "status"),
        Index("idx_order_no", "order_no"),
    )


class PaymentCallback(Base):
    """支付回调记录表"""
    __tablename__ = "payment_callbacks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), nullable=False, index=True)
    
    # 回调信息
    callback_type = Column(String(20), nullable=False)  # wechat, alipay
    callback_data = Column(JSON, nullable=True)
    callback_status = Column(String(20), default="pending")  # pending, processed, failed
    
    # 处理结果
    process_result = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_callback_order", "order_id"),
    )


# 产品定价
PRODUCTS = {
    "vip_pro": {
        "name": "全周期专业版",
        "description": "解锁全部核心功能，服务至装修完成",
        "price": 29900,  # 299元
        "expire_days": 180,
        "features": [
            "无限次AI验房+高清报告下载",
            "全套AI设计服务",
            "设计-预算实时联动+预算红线预警",
            "自动生成施工计划+节点主动通知",
            "无限次AI云监工+进度识别+异常预警",
            "工程档案归档"
        ]
    }
}
