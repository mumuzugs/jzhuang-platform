"""
施工项目模型
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Enum as SQLEnum, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.core.database import Base


class ConstructionStatus(str, enum.Enum):
    """施工状态"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class NodeStatus(str, enum.Enum):
    """节点状态"""
    PENDING = "pending"          # 待开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"       # 已完成
    OVERDUE = "overdue"          # 已延期


class ConstructionProject(Base):
    """装修项目表"""
    __tablename__ = "construction_projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    design_project_id = Column(String(36), nullable=True)  # 关联设计方案
    
    # 项目信息
    name = Column(String(100), nullable=False)
    address = Column(String(500), nullable=True)
    area = Column(Integer, nullable=True)
    
    # 施工周期
    total_cycle = Column(Integer, nullable=True)  # 总工期（天）
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    
    # 状态
    status = Column(SQLEnum(ConstructionStatus), default=ConstructionStatus.NOT_STARTED)
    
    # 进度
    progress = Column(Integer, default=0)  # 0-100%
    
    # 施工计划
    plan = Column(JSON, nullable=True)  # 施工计划详情
    
    # 时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_construction_user", "user_id"),
        Index("idx_construction_status", "status"),
    )


class ConstructionNode(Base):
    """施工节点表"""
    __tablename__ = "construction_nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, index=True)
    
    # 节点信息
    name = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)  # 节点类型
    sequence = Column(Integer, nullable=False)  # 顺序
    
    # 工期
    standard_days = Column(Integer, default=7)  # 标准工期
    planned_start = Column(DateTime, nullable=True)
    planned_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # 状态
    status = Column(SQLEnum(NodeStatus), default=NodeStatus.PENDING)
    
    # 验收
    acceptance_status = Column(String(20), default="pending")  # pending, passed, failed
    acceptance_comment = Column(Text, nullable=True)
    
    # 注意事项
    notes = Column(Text, nullable=True)
    standards = Column(Text, nullable=True)  # 验收标准
    
    # 预警
    warning_level = Column(String(20), nullable=True)  # normal, warning, danger
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_node_project", "project_id"),
        Index("idx_node_status", "status"),
    )


class SitePhoto(Base):
    """工地照片表"""
    __tablename__ = "site_photos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False, index=True)
    node_id = Column(String(36), nullable=True)  # 关联节点
    
    # 照片信息
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    
    # AI识别结果
    recognized_node = Column(String(50), nullable=True)
    progress_percentage = Column(Integer, nullable=True)  # 识别出的进度
    is_normal = Column(Boolean, default=True)
    abnormal_issues = Column(JSON, nullable=True)  # 识别出的问题
    
    # 上传信息
    uploaded_by = Column(String(36), nullable=False)  # user_id 或 工长ID
    uploader_type = Column(String(20), default="user")  # user, worker
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index("idx_photo_project", "project_id"),
        Index("idx_photo_node", "node_id"),
    )


# 标准施工节点定义
STANDARD_NODES = [
    {"name": "开工准备", "type": "preparation", "days": 3, "sequence": 1,
     "notes": "办理物业手续、确定设计方案、进场准备",
     "standards": "施工许可证办理完成、材料进场验收"},
    
    {"name": "水电改造", "type": "electrical", "days": 7, "sequence": 2,
     "notes": "水电定位、开槽、布管、穿线",
     "standards": "电线走活线、水管打压测试"},
    
    {"name": "防水工程", "type": "waterproof", "days": 5, "sequence": 3,
     "notes": "卫生间、厨房、阳台防水处理",
     "standards": "闭水试验48小时无渗漏"},
    
    {"name": "泥瓦工程", "type": "tiling", "days": 14, "sequence": 4,
     "notes": "墙地砖铺贴、地面找平",
     "standards": "瓷砖空鼓率<5%、接缝均匀"},
    
    {"name": "木工工程", "type": "carpentry", "days": 10, "sequence": 5,
     "notes": "吊顶、背景墙、定制柜体",
     "standards": "结构稳固、表面平整"},
    
    {"name": "油漆工程", "type": "painting", "days": 8, "sequence": 6,
     "notes": "墙面刮腻子、刷漆",
     "standards": "墙面平整、无色差"},
    
    {"name": "安装工程", "type": "installation", "days": 5, "sequence": 7,
     "notes": "灯具、开关插座、洁具安装",
     "standards": "功能正常、安装牢固"},
    
    {"name": "竣工验收", "type": "acceptance", "days": 3, "sequence": 8,
     "notes": "整体验收、整改、交付",
     "standards": "符合设计方案、验收合格"},
]
