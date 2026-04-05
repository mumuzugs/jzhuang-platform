"""
设计方案模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, Index, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.core.database import Base


class DesignStyle(str, enum.Enum):
    """装修风格"""
    MODERN_SIMPLE = "modern_simple"     # 现代简约
    NORDIC = "nordic"                  # 北欧
    CHINESE = "chinese"                # 新中式


class LayoutType(str, enum.Enum):
    """布局类型"""
    SPACE_UTILIZATION = "space"        # 极致空间利用率
    FAMILY_FRIENDLY = "family"         # 亲子友好型
    SIMPLE_OPEN = "simple"             # 极简通透型


class DesignStatus(str, enum.Enum):
    """设计状态"""
    PENDING = "pending"                # 待处理
    PROCESSING = "processing"           # 生成中
    COMPLETED = "completed"            # 已完成
    FAILED = "failed"                  # 失败


class DesignProject(Base):
    """设计方案表"""
    __tablename__ = "design_projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    
    # 房屋信息
    house_type = Column(String(20), nullable=True)  # 户型
    area = Column(Integer, nullable=True)  # 面积
    city = Column(String(50), nullable=True)
    
    # 户型图
    layout_image = Column(String(500), nullable=True)
    layout_data = Column(JSON, nullable=True)  # 解析后的户型数据
    
    # 设计参数
    style = Column(SQLEnum(DesignStyle), nullable=True)
    layout_type = Column(SQLEnum(LayoutType), nullable=True)
    
    # 生成的方案
    layouts = Column(JSON, nullable=True)  # 3套平面布局方案
    selected_layout = Column(JSON, nullable=True)  # 用户选择的方案
    
    # 效果图
    render_images = Column(JSON, nullable=True)  # 效果图URL列表
    
    # 施工图
    construction_drawings = Column(JSON, nullable=True)  # 施工图列表
    
    # 材料清单
    material_list = Column(JSON, nullable=True)  # 材料清单
    
    # 状态
    status = Column(SQLEnum(DesignStatus), default=DesignStatus.PENDING)
    
    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_design_user", "user_id"),
        Index("idx_design_status", "status"),
    )


class BudgetItem(Base):
    """预算明细项"""
    __tablename__ = "budget_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, index=True)
    
    # 分类
    category = Column(String(50), nullable=False)  # 材料费/人工费/管理费/杂费
    space = Column(String(50), nullable=True)  # 空间：客厅/卧室/厨房...
    item_name = Column(String(100), nullable=False)  # 项目名称
    
    # 规格
    spec = Column(String(200), nullable=True)  # 规格
    unit = Column(String(20), nullable=True)  # 单位
    quantity = Column(Float, nullable=True)  # 数量
    unit_price = Column(Integer, nullable=True)  # 单价（分）
    total_price = Column(Integer, nullable=True)  # 总价（分）
    
    # 品牌
    brand = Column(String(100), nullable=True)
    material = Column(String(100), nullable=True)  # 材质
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_budget_project", "project_id"),
    )


class BudgetSummary(Base):
    """预算汇总"""
    __tablename__ = "budget_summaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, index=True, unique=True)
    
    # 各项汇总
    material_cost = Column(Integer, default=0)  # 材料费
    labor_cost = Column(Integer, default=0)     # 人工费
    management_fee = Column(Integer, default=0) # 管理费
    misc_cost = Column(Integer, default=0)       # 杂费
    
    # 总价
    total_cost = Column(Integer, default=0)
    
    # 预算红线
    budget_limit = Column(Integer, nullable=True)
    is_over_budget = Column(Boolean, default=False)
    over_amount = Column(Integer, default=0)
    
    # 版本
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_budget_project", "project_id"),
    )
